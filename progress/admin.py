from django.contrib import admin
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


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ("student", "assignment", "status", "submitted_at")
    list_filter = ("status",)
