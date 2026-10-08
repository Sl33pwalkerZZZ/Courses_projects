from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from courses.models import Course

from .models import Enrollment, EnrollmentRequest


@transaction.atomic
def submit_enrollment_request(*, student, course, message):
    # Serialize applications and decisions for this course on databases with row locks.
    course = Course.objects.select_for_update().get(pk=course.pk)
    if Enrollment.objects.filter(student=student, course=course).exists():
        raise ValidationError("You already have access to this course.", code="already_enrolled")
    if course.enrollment_mode != Course.EnrollmentMode.APPROVAL:
        raise ValidationError("This course uses immediate enrollment.", code="open_enrollment")
    if EnrollmentRequest.objects.filter(student=student, course=course, status="pending").exists():
        raise ValidationError("You already have a pending application.", code="duplicate_pending")

    application = EnrollmentRequest(student=student, course=course, message=message)
    application.full_clean()
    application.save()
    return application


@transaction.atomic
def review_enrollment_request(*, application_id, reviewer, approve, note=""):
    if not reviewer.is_active or not (
        reviewer.is_superuser
        or (reviewer.is_staff and reviewer.has_perm("progress.change_enrollmentrequest"))
    ):
        raise PermissionDenied("You do not have permission to review enrollment requests.")

    # Keep lock order consistent with submission: course, then application.
    course_id = EnrollmentRequest.objects.values_list("course_id", flat=True).get(pk=application_id)
    Course.objects.select_for_update().get(pk=course_id)
    application = EnrollmentRequest.objects.select_for_update().get(pk=application_id)
    if application.status != EnrollmentRequest.Status.PENDING:
        return application, False

    if approve:
        Enrollment.objects.get_or_create(student_id=application.student_id, course_id=application.course_id)
        application.status = EnrollmentRequest.Status.APPROVED
    else:
        application.status = EnrollmentRequest.Status.REJECTED
    application.admin_note = note.strip()
    application.reviewed_by = reviewer
    application.reviewed_at = timezone.now()
    application.save(update_fields=["status", "admin_note", "reviewed_by", "reviewed_at"])
    return application, True
