from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models

from courses.models import Assignment, Course, Lesson


class Enrollment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["student", "course"]

    def __str__(self):
        return f"{self.student} → {self.course}"


class EnrollmentRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollment_requests",
    )
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="enrollment_requests")
    message = models.CharField(max_length=1000, validators=[MinLengthValidator(20)])
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="enrollment_decisions",
    )
    admin_note = models.TextField(blank=True, help_text="Visible to the student after a decision.")
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at", "-pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course"], condition=models.Q(status="pending"),
                name="one_pending_enrollment_request",
            ),
            models.CheckConstraint(
                condition=models.Q(status__in=["pending", "approved", "rejected"]),
                name="enrollment_request_valid_status",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(status="pending", reviewed_at__isnull=True, reviewed_by__isnull=True)
                    | models.Q(status__in=["approved", "rejected"], reviewed_at__isnull=False)
                ),
                name="enrollment_request_review_state",
            ),
        ]

    def clean(self):
        super().clean()
        self.message = (self.message or "").strip()
        if len(self.message) < 20:
            raise ValidationError({"message": "Enter a motivation message of 20–1000 characters."})
        if self._state.adding and self.status == self.Status.PENDING and self.student_id and self.course_id:
            if Enrollment.objects.filter(student_id=self.student_id, course_id=self.course_id).exists():
                raise ValidationError("You already have access to this course.", code="already_enrolled")

    def __str__(self):
        return f"{self.student} → {self.course} ({self.get_status_display()})"


class LessonProgress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name="lesson_progress")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ["enrollment", "lesson"]


class AssignmentSubmission(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Черновик"
        PENDING = "pending", "На проверке"
        APPROVED = "approved", "Принято"
        REJECTED = "rejected", "Отклонено"

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submissions")
    content = models.TextField(blank=True)
    file = models.FileField(upload_to="submissions/", blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    reviewer_comment = models.TextField(blank=True)
    # Opt in only: legacy submissions keep their existing defaults and behavior.
    is_structured = models.BooleanField(default=False)
    payload = models.JSONField(default=dict, blank=True)
    revision = models.PositiveIntegerField(default=0)
    review_history = models.JSONField(default=list, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    # Generic revisions are immutable records linked into a single history chain.
    # The opt-in structured Course 8 activity keeps its established single-row flow.
    previous_submission = models.OneToOneField(
        "self", null=True, blank=True, related_name="next_revision", on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "assignment"], condition=models.Q(is_structured=True),
                name="one_structured_assignment_per_student",
            ),
            models.UniqueConstraint(
                fields=["student", "assignment"],
                condition=models.Q(status="pending", is_structured=False),
                name="one_pending_generic_assignment_per_student",
            ),
        ]

    def __str__(self):
        return f"{self.student} — {self.assignment} ({self.get_status_display()})"


def assignment_submission_upload_to(instance, filename):
    # Never use a client filename as a path or storage key.
    from uuid import uuid4
    from pathlib import Path
    suffix = Path(filename).suffix.lower()
    return f"submissions/{uuid4().hex[:2]}/{uuid4().hex}{suffix}"


class AssignmentSubmissionAttachment(models.Model):
    submission = models.ForeignKey(AssignmentSubmission, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to=assignment_submission_upload_to, max_length=255)
    original_filename = models.CharField(max_length=255)
    detected_content_type = models.CharField(max_length=100)
    size = models.PositiveBigIntegerField()
    sha256 = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["pk"]
        constraints = [
            models.UniqueConstraint(fields=["submission", "sha256"], name="unique_assignment_submission_attachment_bytes"),
        ]

    def __str__(self):
        return self.original_filename
