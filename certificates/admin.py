from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from rest_framework.exceptions import APIException
from courses.models import Course
from .models import Certificate, CourseCertificatePolicy
from .services import confirmed_certificate_name, issue_certificate, revoke_certificate
from studio.permissions import moderator


class CertificateAdminPermission:
    def has_module_permission(self, request):
        # Issued records and policy configuration remain visible in read-only mode.
        return bool(request.user.is_staff and moderator(request.user))

    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request):
        return self.has_module_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False


class PolicyForm(forms.ModelForm):
    class Meta:
        model = CourseCertificatePolicy
        fields = '__all__'
        help_texts = {
            'required_lessons': 'When selected, only these lessons are required. If empty, the all-lessons setting below applies.',
            'require_all_lessons': 'Used only when no specific required lessons are selected.',
        }

    def clean(self):
        data = super().clean()
        course = data.get('course')
        assignments = data.get('required_assignments')
        lessons = data.get('required_lessons')
        if course and assignments is not None and assignments.exclude(lesson__module__course=course).exists():
            self.add_error('required_assignments', 'Select assignments belonging to this course.')
        if course and lessons is not None and lessons.exclude(module__course=course).exists():
            self.add_error('required_lessons', 'Select lessons belonging to this course.')
        return data


@admin.register(CourseCertificatePolicy)
class PolicyAdmin(CertificateAdminPermission, admin.ModelAdmin):
    list_display = ('course', 'enabled', 'issuer_name', 'issuer_approved')
    filter_horizontal = ('required_lessons', 'required_assignments')
    form = PolicyForm

    def has_add_permission(self, request):
        return bool(getattr(settings, 'CERTIFICATES_ENABLED', False) and super().has_add_permission(request))

    def has_change_permission(self, request, obj=None):
        return bool(getattr(settings, 'CERTIFICATES_ENABLED', False) and super().has_change_permission(request, obj))


class IssueForm(forms.Form):
    student = forms.ModelChoiceField(queryset=get_user_model().objects.filter(is_active=True))
    course = forms.ModelChoiceField(queryset=Course.objects.filter(is_published=True))
    learner_name = forms.CharField(
        label='Student-confirmed certificate name', required=False, disabled=True,
        help_text='Read-only value confirmed by the student. It cannot be edited by an administrator.',
    )
    confirmation = forms.BooleanField(label='I confirm the learner name and approved issuer identity.')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        student_value = self.data.get(self.add_prefix('student')) if self.is_bound else self.initial.get('student')
        student_id = getattr(student_value, 'pk', student_value)
        student = get_user_model().objects.filter(pk=student_id, is_active=True).first() if student_id else None
        self.fields['learner_name'].initial = confirmed_certificate_name(student) or ''

    def clean(self):
        data = super().clean()
        student = data.get('student')
        if student and not confirmed_certificate_name(student):
            self.add_error('student', 'The student has not confirmed a valid certificate name.')
        return data


@admin.register(Certificate)
class CertificateAdmin(CertificateAdminPermission, admin.ModelAdmin):
    list_display = ('student', 'course', 'verification_code', 'issued_at', 'revoked_at')
    readonly_fields = tuple(field.name for field in Certificate._meta.fields)
    actions = ('revoke_selected',)
    change_list_template = 'admin/certificates/change_list.html'

    def changelist_view(self, request, extra_context=None):
        return super().changelist_view(request, extra_context={
            **(extra_context or {}),
            'certificate_issuance_enabled': bool(getattr(settings, 'CERTIFICATES_ENABLED', False)),
        })

    def get_urls(self):
        return [path('issue/', self.admin_site.admin_view(self.issue_view), name='certificates_certificate_issue')] + super().get_urls()

    def issue_view(self, request):
        if not self.has_module_permission(request) or not getattr(settings, 'CERTIFICATES_ENABLED', False):
            raise PermissionDenied
        form = IssueForm(request.POST or None)
        if request.method == 'POST' and form.is_valid():
            try:
                certificate, created = issue_certificate(administrator=request.user, student=form.cleaned_data['student'], course_id=form.cleaned_data['course'].pk)
            except APIException as exc:
                form.add_error(None, str(exc.detail))
            else:
                self.message_user(request, 'Certificate issued.' if created else 'Certificate already exists; no duplicate created.', messages.SUCCESS)
                return redirect(reverse('admin:certificates_certificate_change', args=[certificate.pk]))
        return TemplateResponse(request, 'admin/certificates/issue.html', {**self.admin_site.each_context(request), 'title': 'Issue a verified course certificate', 'form': form, 'opts': self.model._meta})

    def has_add_permission(self, request):
        # All issuance must run the checked atomic service, never a raw admin form.
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not getattr(settings, 'CERTIFICATES_ENABLED', False):
            actions.pop('revoke_selected', None)
        return actions

    def has_change_permission(self, request, obj=None):
        # Issued snapshots/evidence are immutable, including for superusers.
        return False

    @admin.action(description='Revoke selected certificates', permissions=['view'])
    def revoke_selected(self, request, queryset):
        for certificate in queryset:
            revoke_certificate(administrator=request.user, certificate=certificate, reason='Revoked by administrator through Django Admin.')
        self.message_user(request, 'Certificates revoked.', messages.SUCCESS)
