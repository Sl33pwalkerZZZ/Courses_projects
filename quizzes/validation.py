from django.core.exceptions import ValidationError
from django.db.models import prefetch_related_objects


def validate_choices(question_type, choices):
    """Used for saved questions and the prospective choices in an Admin form."""
    if question_type not in {"single", "multiple"}:
        raise ValidationError("Choose a supported question type.")
    if len(choices) < 2:
        raise ValidationError("Each question needs at least two choices.")
    if any(not choice["text"].strip() for choice in choices):
        raise ValidationError("Choice text cannot be empty.")
    correct = sum(choice["is_correct"] for choice in choices)
    if question_type == "single" and correct != 1:
        raise ValidationError("Single-choice questions need exactly one correct choice.")
    if question_type == "multiple" and correct < 1:
        raise ValidationError("Multiple-select questions need at least one correct choice.")


def validate_quiz(quiz, questions=None):
    if not 0 <= quiz.passing_percentage <= 100:
        raise ValidationError("Passing percentage must be between 0 and 100.")
    if questions is None:
        questions = list(quiz.questions.all()) if quiz.pk else []
        # Reuse existing caches; otherwise fetch every question's choices together.
        prefetch_related_objects(questions, "choices")
    if not questions:
        raise ValidationError("A published quiz needs at least one question.")
    for question in questions:
        if not question.text.strip():
            raise ValidationError("Question text cannot be empty.")
        validate_choices(question.type, [
            {"text": choice.text, "is_correct": choice.is_correct}
            for choice in question.choices.all()
        ])
    return questions
