from django import forms
from django.contrib import admin
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import reverse

from courses.models import Course

from .models import AssignmentSubmission, Enrollment, EnrollmentRequest, LessonProgress
from .services import review_enrollment_request


@admin.register(EnrollmentRequest)
class EnrollmentRequestAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "status", "created_at", "reviewed_by", "reviewed_at")
    list_filter = ("status", "course", "created_at")
    search_fields = ("student__username", "student__email", "course__title", "course__slug")
    list_select_related = ("student", "course", "reviewed_by")
    fields = ("student", "course", "message", "status", "admin_note", "created_at", "reviewed_by", "reviewed_at")
    readonly_fields = ("student", "course", "message", "status", "created_at", "reviewed_by", "reviewed_at")
    actions = ("approve_applications", "reject_applications")
    change_form_template = "admin/progress/enrollmentrequest/change_form.html"

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status != EnrollmentRequest.Status.PENDING:
            return self.readonly_fields + ("admin_note",)
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        # Only the note is editable. Never overwrite a decision from a stale form.
        # Django wraps change-form POSTs in a transaction; use the service's lock order.
        Course.objects.select_for_update().get(pk=obj.course_id)
        EnrollmentRequest.objects.filter(pk=obj.pk, status=EnrollmentRequest.Status.PENDING).update(
            admin_note=obj.admin_note,
        )
        obj.refresh_from_db()

    def response_change(self, request, obj):
        if "_approve" in request.POST or "_reject" in request.POST:
            application, changed = review_enrollment_request(
                application_id=obj.pk, reviewer=request.user,
                approve="_approve" in request.POST, note=obj.admin_note,
            )
            self.message_user(
                request,
                f"Application {application.get_status_display().lower()}." if changed
                else "This application was already reviewed; no changes were made.",
            )
            return HttpResponseRedirect(reverse("admin:progress_enrollmentrequest_change", args=[obj.pk]))
        return super().response_change(request, obj)

    def decide_selected(self, request, queryset, *, approve):
        changed = 0
        for application in queryset:
            _, reviewed = review_enrollment_request(
                application_id=application.pk, reviewer=request.user, approve=approve,
                note=application.admin_note,
            )
            changed += int(reviewed)
        decision = "approved" if approve else "rejected"
        self.message_user(request, f"{changed} application(s) {decision}. Already reviewed applications were skipped.")

    @admin.action(description="Approve selected pending applications", permissions=["change"])
    def approve_applications(self, request, queryset):
        self.decide_selected(request, queryset, approve=True)

    @admin.action(description="Reject selected pending applications", permissions=["change"])
    def reject_applications(self, request, queryset):
        self.decide_selected(request, queryset, approve=False)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "granted_at")
    list_filter = ("course",)


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "lesson", "completed_at")


class AssignmentSubmissionReviewForm(forms.ModelForm):
    expected_revision = forms.IntegerField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = AssignmentSubmission
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["expected_revision"].initial = self.instance.revision

    def clean(self):
        data = super().clean()
        if not self.instance.pk or not self.instance.is_structured:
            return data
        # Admin change POST already runs in an atomic transaction.
        current = AssignmentSubmission.objects.select_for_update().get(pk=self.instance.pk)
        if data.get("expected_revision") != current.revision:
            raise forms.ValidationError("This submission changed. Reload before reviewing.")
        if current.status == "pending":
            if data.get("status") not in ("pending", "approved", "rejected"):
                raise forms.ValidationError("Choose pending, approved or rejected.")
            if data.get("status") == "rejected" and not data.get("reviewer_comment", "").strip():
                raise forms.ValidationError("Include feedback explaining what the student should improve.")
        elif data.get("status", current.status) != current.status:
            raise forms.ValidationError("Only pending submissions can be reviewed.")
        return data


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    form = AssignmentSubmissionReviewForm
    list_display = ("student", "assignment", "status", "submitted_at", "is_structured")
    list_filter = ("status", "is_structured")

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.is_structured:
            fields = ("student", "assignment", "content", "file", "payload", "is_structured",
                      "revision", "review_history", "submitted_at", "reviewed_at")
            if obj.status != "pending":
                fields += ("status", "reviewer_comment")
            return fields
        return ("is_structured", "payload", "revision", "review_history")

    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_structured:
            return False
        return super().has_delete_permission(request, obj)

    def delete_queryset(self, request, queryset):
        # Bulk deletion must honor the same structured submission protection.
        super().delete_queryset(request, queryset.filter(is_structured=False))

    def save_model(self, request, obj, form, change):
        if change and obj.is_structured:
            current = AssignmentSubmission.objects.select_for_update().get(pk=obj.pk)
            if current.status == "pending":
                obj.revision = current.revision + 1
                if obj.status in ("approved", "rejected"):
                    obj.reviewed_at = timezone.now()
            else:
                return
        super().save_model(request, obj, form, change)
