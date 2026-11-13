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
    from studio.permissions import moderator

    if not reviewer.is_active or not (
        moderator(reviewer)
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


@transaction.atomic
def review_assignment_submission(*, submission_id, reviewer, revision, status, comment="", rubric_scores=None):
    """One auditable decision path shared by instructor review clients."""
    from studio.permissions import instructor, moderator
    from .models import AssignmentSubmission

    if not instructor(reviewer):
        raise PermissionDenied("Instructor access required.")
    initial = AssignmentSubmission.objects.select_related("assignment__lesson__module__course").get(pk=submission_id)
    course = initial.assignment.lesson.module.course
    if not moderator(reviewer) and course.author_id != reviewer.pk:
        raise PermissionDenied("Only the course owner can review this submission.")
    if initial.student_id == reviewer.pk:
        raise PermissionDenied("You cannot review your own submission.")
    course = Course.objects.select_for_update().get(pk=course.pk)
    if not moderator(reviewer) and course.author_id != reviewer.pk:
        raise PermissionDenied("Only the current course owner can review this submission.")
    submission = AssignmentSubmission.objects.select_for_update().get(pk=submission_id)
    if status not in ("approved", "rejected"):
        raise ValidationError({"status": "Choose approved or rejected."})
    if not isinstance(comment, str) or len(comment) > 10000 or status == "rejected" and not comment.strip():
        raise ValidationError({"reviewer_comment": "Include feedback explaining what should improve."})
    if submission.status != "pending":
        raise ValidationError({"status": "Only pending submissions can be reviewed."})
    if revision != submission.revision:
        raise ValidationError({"revision": "Submission changed. Reload before reviewing."}, code="revision_conflict")
    if submission.assignment.learning_activity == "final_media_project":
        expected = {"completeness", "application", "quality", "documentation"}
        if not isinstance(rubric_scores, dict) or set(rubric_scores) != expected:
            raise ValidationError({"rubric_scores": "Score all four final-project criteria."})
        if any(type(value) is not int or value < 0 or value > 25 for value in rubric_scores.values()):
            raise ValidationError({"rubric_scores": "Each criterion must be scored from 0 to 25."})
    rubric_scores = dict(rubric_scores) if rubric_scores is not None else None
    submission.status = status
    submission.reviewer_comment = comment.strip()
    submission.reviewed_at = timezone.now()
    submission.revision += 1
    event = {
        "reviewer_id": reviewer.pk, "status": status, "comment": submission.reviewer_comment,
        "reviewed_at": submission.reviewed_at.isoformat(), "revision": submission.revision,
    }
    if rubric_scores is not None:
        event["rubric_scores"] = rubric_scores
    submission.review_history = submission.review_history + [event]
    submission.save(update_fields=["status", "reviewer_comment", "reviewed_at", "revision", "review_history"])
    return submission


@transaction.atomic
def reopen_assignment_submission(*, submission_id, reviewer):
    """Create an auditable new draft after approval; never edit the approved record."""
    from studio.permissions import instructor, moderator
    from .models import AssignmentSubmission

    if not instructor(reviewer):
        raise PermissionDenied("Instructor access required.")
    initial = AssignmentSubmission.objects.select_related("assignment__lesson__module__course").get(pk=submission_id)
    course = initial.assignment.lesson.module.course
    if not moderator(reviewer) and course.author_id != reviewer.pk:
        raise PermissionDenied("Only the course owner can reopen this submission.")
    if initial.student_id == reviewer.pk:
        raise PermissionDenied("You cannot reopen your own submission.")
    Course.objects.select_for_update().get(pk=course.pk)
    submission = AssignmentSubmission.objects.select_for_update().select_related("assignment").get(pk=submission_id)
    if submission.is_structured:
        raise ValidationError("Structured submissions use their existing resubmission workflow.")
    if submission.status != "approved":
        raise ValidationError({"status": "Only approved submissions can be reopened."})
    if hasattr(submission, "next_revision"):
        raise ValidationError({"status": "This submission has already been reopened."})
    now = timezone.now()
    return AssignmentSubmission.objects.create(
        assignment=submission.assignment, student_id=submission.student_id, status="draft",
        previous_submission=submission,
        review_history=[{"action": "reopened", "reviewer_id": reviewer.pk, "reopened_at": now.isoformat()}],
    )
