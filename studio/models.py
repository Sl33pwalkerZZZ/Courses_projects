import uuid
from django.conf import settings
from django.db import models


class CourseSettings(models.Model):
    course = models.OneToOneField('courses.Course', on_delete=models.CASCADE, related_name='studio_settings')
    language = models.CharField(max_length=10, default='ru')


class LessonImageDescription(models.Model):
    image = models.OneToOneField('courses.LessonImage', on_delete=models.CASCADE, related_name='studio_description')
    alt_text = models.JSONField(default=dict)
    decorative = models.BooleanField(default=False)


class PublicationRequest(models.Model):
    course = models.ForeignKey('courses.Course', on_delete=models.PROTECT, related_name='publication_requests')
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='+')
    status = models.CharField(max_length=20, default='pending', choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')])
    source_reviewed = models.BooleanField(default=False)
    assessment_reviewed = models.BooleanField(default=False)
    fingerprint = models.CharField(max_length=64)
    note = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='+', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at', '-pk']
        constraints = [models.UniqueConstraint(fields=['course'], condition=models.Q(status='pending'), name='one_pending_publication')]


class PublicationEvent(models.Model):
    request = models.ForeignKey(PublicationRequest, on_delete=models.PROTECT, related_name='events')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='+')
    decision = models.CharField(max_length=20)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class ImportPreview(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='+')
    source_sha256 = models.CharField(max_length=64)
    parsed = models.JSONField()
    course = models.ForeignKey('courses.Course', on_delete=models.PROTECT, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
