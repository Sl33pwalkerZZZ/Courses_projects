import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from courses.models import Course


def verification_code():
    return uuid.uuid4().hex


class CourseCertificatePolicy(models.Model):
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name='certificate_policy')
    enabled = models.BooleanField(default=False)
    require_all_lessons = models.BooleanField(default=True)
    final_quiz = models.ForeignKey('quizzes.Quiz', null=True, blank=True, on_delete=models.PROTECT)
    required_assignments = models.ManyToManyField('courses.Assignment', blank=True)
    issuer_name = models.CharField(max_length=200, blank=True)
    issuer_approved = models.BooleanField(default=False)

    def clean(self):
        super().clean()
        if self.final_quiz_id and self.final_quiz.lesson.module.course_id != self.course_id:
            raise ValidationError({'final_quiz': 'Select an assessment belonging to this course.'})
        if self.enabled and (not self.issuer_approved or not self.issuer_name.strip()):
            raise ValidationError('Approve an explicit issuer identity before enabling certificates.')

    def __str__(self):
        return str(self.course)


class Certificate(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    verification_code = models.CharField(max_length=32, unique=True, default=verification_code, editable=False)
    issued_at = models.DateTimeField(auto_now_add=True)
    learner_name = models.CharField(max_length=200, blank=True)
    course_title = models.CharField(max_length=255, blank=True)
    issuer_name = models.CharField(max_length=200, blank=True)
    evidence = models.JSONField(default=dict, blank=True, editable=False)
    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='issued_certificates')
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='revoked_certificates')
    revocation_reason = models.TextField(blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['student', 'course'], name='one_certificate_per_student_course')]

    def __str__(self):
        return f'{self.student} — {self.course}'
