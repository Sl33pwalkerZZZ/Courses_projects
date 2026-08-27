from django.conf import settings
from django.db import models


class Direction(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Course(models.Model):
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
    created_at = models.DateTimeField(auto_now_add=True)

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

    def __str__(self):
        return f"{self.lesson.title}: {self.get_type_display()}"
