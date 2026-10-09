import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validation import validate_choices, validate_quiz


class Quiz(models.Model):
    lesson = models.OneToOneField("courses.Lesson", on_delete=models.CASCADE, related_name="quiz")
    title = models.CharField(max_length=255)
    instructions = models.TextField(blank=True)
    passing_percentage = models.PositiveSmallIntegerField(
        default=70, validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    is_published = models.BooleanField(default=False)

    class Meta:
        constraints = [models.CheckConstraint(
            condition=models.Q(passing_percentage__gte=0, passing_percentage__lte=100),
            name="quiz_passing_percentage_range",
        )]

    def clean(self):
        super().clean()
        if self.pk and self.attempts.exists():
            original_lesson = type(self).objects.values_list("lesson_id", flat=True).get(pk=self.pk)
            if self.lesson_id != original_lesson:
                raise ValidationError({"lesson": "A quiz with attempts cannot be moved to another lesson."})
        if self.is_published:
            validate_quiz(self)

    def __str__(self):
        return self.title


class QuizQuestion(models.Model):
    class Type(models.TextChoices):
        SINGLE = "single", "Single choice"
        MULTIPLE = "multiple", "Multiple select"

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    type = models.CharField(max_length=10, choices=Type.choices, default=Type.SINGLE)
    order = models.PositiveIntegerField(default=0)
    explanation = models.TextField(blank=True)

    class Meta:
        ordering = ["order", "pk"]
        constraints = [models.CheckConstraint(
            condition=models.Q(type__in=["single", "multiple"]), name="quiz_question_valid_type",
        )]

    def clean(self):
        super().clean()
        # Drafts can be assembled in stages; published questions must be usable.
        if self.quiz_id and self.quiz.is_published:
            validate_choices(self.type, [
                {"text": choice.text, "is_correct": choice.is_correct}
                for choice in self.choices.all()
            ] if self.pk else [])

    def __str__(self):
        return self.text[:100]


class QuizChoice(models.Model):
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name="choices")
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_correct = models.BooleanField(default=False)

    class Meta:
        ordering = ["order", "pk"]

    def __str__(self):
        return self.text[:100]


class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="quiz_attempts")
    submission_id = models.UUIDField(default=uuid.uuid4, editable=False)
    request_digest = models.CharField(max_length=64, editable=False)
    score = models.DecimalField(max_digits=5, decimal_places=2, editable=False)
    correct_count = models.PositiveIntegerField(editable=False)
    question_count = models.PositiveIntegerField(editable=False)
    passing_percentage = models.PositiveSmallIntegerField(editable=False)
    passed = models.BooleanField(editable=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-submitted_at", "-pk"]
        constraints = [
            models.UniqueConstraint(fields=["student", "quiz", "submission_id"], name="quiz_unique_submission"),
            models.CheckConstraint(condition=models.Q(score__gte=0, score__lte=100), name="quiz_score_range"),
            models.CheckConstraint(
                condition=models.Q(question_count__gte=1, correct_count__lte=models.F("question_count")),
                name="quiz_attempt_valid_counts",
            ),
            models.CheckConstraint(
                condition=models.Q(passing_percentage__gte=0, passing_percentage__lte=100),
                name="quiz_attempt_passing_range",
            ),
        ]

    def __str__(self):
        return f"{self.student} / {self.quiz}: {self.score}%"


class QuizAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name="answers")
    # Snapshots keep old feedback meaningful when an administrator edits/deletes a question.
    question = models.ForeignKey(QuizQuestion, on_delete=models.SET_NULL, null=True, related_name="answers")
    snapshot = models.JSONField(editable=False)
    selected_choice_ids = models.JSONField(editable=False)
    is_correct = models.BooleanField(editable=False)

    class Meta:
        ordering = ["pk"]
        constraints = [models.UniqueConstraint(fields=["attempt", "question"], name="quiz_one_answer_per_question")]
