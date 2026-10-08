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
        PENDING = "pending", "На проверке"
        APPROVED = "approved", "Принято"
        REJECTED = "rejected", "Отклонено"

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submissions")
    content = models.TextField(blank=True)
    file = models.FileField(upload_to="submissions/", blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    reviewer_comment = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.student} — {self.assignment} ({self.get_status_display()})"
