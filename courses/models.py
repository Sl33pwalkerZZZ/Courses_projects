from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError


class Direction(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Course(models.Model):
    class EnrollmentMode(models.TextChoices):
        APPROVAL = "approval", "Approval required"
        OPEN = "open", "Open enrollment"

    class Level(models.TextChoices):
        BEGINNER = "beginner", "Начинающий"
        INTERMEDIATE = "intermediate", "Средний"
        ADVANCED = "advanced", "Продвинутый"

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    direction = models.ForeignKey(Direction, on_delete=models.PROTECT, related_name="courses")
    level = models.CharField(max_length=20, choices=Level.choices, default=Level.BEGINNER)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="authored_courses")
    is_published = models.BooleanField(default=False)
    enrollment_mode = models.CharField(
        max_length=20, choices=EnrollmentMode.choices, default=EnrollmentMode.APPROVAL,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()
        imported = getattr(self, "content_import", None) if self.pk else None
        if self.is_published and imported and not imported.review_approved:
            raise ValidationError({"is_published": "Review and approve the imported source and assessment before publication."})

    def __str__(self):
        return self.title


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.course.title} / {self.title}"


class Lesson(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=255)
    text_content = models.TextField()
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title


class LessonImage(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="lessons/")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]


class Assignment(models.Model):
    class Type(models.TextChoices):
        TEXT_ANSWER = "text", "Текстовый ответ"
        FILE_UPLOAD = "file", "Загрузка файла"
        QUIZ = "quiz", "Тест с выбором ответа"

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="assignments")
    type = models.CharField(max_length=20, choices=Type.choices)
    description = models.TextField()
    learning_activity = models.CharField(max_length=40, blank=True, default="")

    def __str__(self):
        return f"{self.lesson.title}: {self.get_type_display()}"


class CourseImport(models.Model):
    """Provenance and ownership for this explicitly imported draft, not legacy data."""
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name="content_import")
    source_name = models.CharField(max_length=255)
    source_sha256 = models.CharField(max_length=64)
    manifest_sha256 = models.CharField(max_length=64)
    content_sha256 = models.CharField(max_length=64)
    version = models.CharField(max_length=40)
    content_language = models.CharField(max_length=10, default="ru")
    review_approved = models.BooleanField(default=False, help_text="Confirm source facts, lessons and quiz answers were reviewed before publication.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course}: {self.version}"


class LessonLearningContent(models.Model):
    """Additive structured teaching material; existing lesson records are untouched."""
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name="learning_content")
    content_language = models.CharField(max_length=10, default="ru")
    source_sections = models.JSONField(default=list, blank=True)
    objectives = models.JSONField(default=list, blank=True)
    interactions = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.lesson.title


class LessonAttachment(models.Model):
    """Private authored audio/subtitles; independent of assignments/progress."""
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='attachments')
    kind = models.CharField(max_length=10, choices=[('audio', 'Audio'), ('srt', 'Subtitles')])
    file = models.FileField(upload_to='lessons/attachments/', max_length=255)
    filename = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=80)
    sha256 = models.CharField(max_length=64)
    label = models.CharField(max_length=255)
    caption = models.TextField(blank=True, max_length=2000)
    transcript = models.TextField(blank=True, max_length=20000)
    provenance = models.TextField(max_length=4000)
    after_section = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order', 'pk']
        constraints = [models.UniqueConstraint(fields=['lesson', 'sha256'], name='unique_lesson_attachment_bytes')]
