from django import forms
from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from rest_framework.exceptions import APIException
from courses.models import Course
from .models import Certificate, CourseCertificatePolicy
from .services import issue_certificate, revoke_certificate
from studio.permissions import moderator


class CertificateAdminPermission:
    def has_module_permission(self, request):
        # Administrators must be able to configure policies before enabling
        # issuance. The service, not admin visibility, enforces that switch.
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

    def clean(self):
        data = super().clean()
        course = data.get('course')
        assignments = data.get('required_assignments')
        if course and assignments is not None and assignments.exclude(lesson__module__course=course).exists():
            self.add_error('required_assignments', 'Select assignments belonging to this course.')
        return data


@admin.register(CourseCertificatePolicy)
class PolicyAdmin(CertificateAdminPermission, admin.ModelAdmin):
    list_display = ('course', 'enabled', 'issuer_name', 'issuer_approved')
    filter_horizontal = ('required_assignments',)
    form = PolicyForm


class IssueForm(forms.Form):
    student = forms.ModelChoiceField(queryset=get_user_model().objects.filter(is_active=True))
    course = forms.ModelChoiceField(queryset=Course.objects.filter(is_published=True))
    learner_name = forms.CharField(max_length=200, help_text='Confirm the full display name recorded in the learner profile.')
    confirmation = forms.BooleanField(label='I confirm the learner name and approved issuer identity.')


@admin.register(Certificate)
class CertificateAdmin(CertificateAdminPermission, admin.ModelAdmin):
    list_display = ('student', 'course', 'verification_code', 'issued_at', 'revoked_at')
    readonly_fields = tuple(field.name for field in Certificate._meta.fields)
    actions = ('revoke_selected',)
    change_list_template = 'admin/certificates/change_list.html'

    def get_urls(self):
        return [path('issue/', self.admin_site.admin_view(self.issue_view), name='certificates_certificate_issue')] + super().get_urls()

    def issue_view(self, request):
        if not self.has_module_permission(request):
            raise PermissionDenied
        form = IssueForm(request.POST or None)
        if request.method == 'POST' and form.is_valid():
            try:
                certificate, created = issue_certificate(administrator=request.user, student=form.cleaned_data['student'], course_id=form.cleaned_data['course'].pk, learner_name=form.cleaned_data['learner_name'])
            except APIException as exc:
                form.add_error(None, str(exc.detail))
            else:
                self.message_user(request, 'Certificate issued.' if created else 'Certificate already exists; no duplicate created.', messages.SUCCESS)
                return redirect(reverse('admin:certificates_certificate_change', args=[certificate.pk]))
        return TemplateResponse(request, 'admin/certificates/issue.html', {**self.admin_site.each_context(request), 'title': 'Issue a verified course certificate', 'form': form, 'opts': self.model._meta})

    def has_add_permission(self, request):
        # All issuance must run the checked atomic service, never a raw admin form.
        return False

    def has_change_permission(self, request, obj=None):
        # Issued snapshots/evidence are immutable, including for superusers.
        return False

    @admin.action(description='Revoke selected certificates', permissions=['view'])
    def revoke_selected(self, request, queryset):
        for certificate in queryset:
            revoke_certificate(administrator=request.user, certificate=certificate, reason='Revoked by administrator through Django Admin.')
        self.message_user(request, 'Certificates revoked.', messages.SUCCESS)
