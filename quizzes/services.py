import hashlib
import json
from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError as ModelValidationError
from django.db import IntegrityError, transaction
from rest_framework.exceptions import APIException, ValidationError

from .models import Quiz, QuizAnswer, QuizAttempt
from .validation import validate_quiz


class QuizUnavailable(APIException):
    status_code = 409
    default_detail = "The quiz is being prepared. Try again later."
    default_code = "quiz_unavailable"


class SubmissionConflict(APIException):
    status_code = 409
    default_detail = "This submission ID was already used for different answers."
    default_code = "submission_conflict"


def usable_questions(quiz):
    try:
        return validate_quiz(quiz)
    except ModelValidationError:
        raise QuizUnavailable()


def submission_digest(answers):
    normalized = sorted(
        [(answer["question_id"], sorted(answer["choice_ids"])) for answer in answers],
        key=lambda answer: answer[0],
    )
    return hashlib.sha256(json.dumps(normalized).encode()).hexdigest()


def existing_submission(quiz, student, submission_id, digest):
    attempt = QuizAttempt.objects.filter(quiz=quiz, student=student, submission_id=submission_id).first()
    if attempt and attempt.request_digest != digest:
        raise SubmissionConflict()
    return attempt


def submit_attempt(*, quiz_id, student, submission_id, answers):
    """A client UUID makes retries idempotent; a new UUID starts a new attempt."""
    digest = submission_digest(answers)
    try:
        with transaction.atomic():
            quiz = Quiz.objects.select_for_update().get(pk=quiz_id)
            previous = existing_submission(quiz, student, submission_id, digest)
            if previous:
                return previous, False
            if not quiz.is_published:
                raise QuizUnavailable()
            questions = usable_questions(quiz)
            submitted = {answer["question_id"]: set(answer["choice_ids"]) for answer in answers}
            if set(submitted) != {question.pk for question in questions}:
                raise ValidationError({"answers": "Answer each question in this quiz exactly once."})
            graded = []
            for question in questions:
                choices = list(question.choices.all())
                selected = submitted[question.pk]
                if not selected.issubset({choice.pk for choice in choices}):
                    raise ValidationError({"answers": "A selected choice does not belong to its question."})
                if question.type == "single" and len(selected) != 1:
                    raise ValidationError({"answers": "Single-choice questions require one choice."})
                correct = {choice.pk for choice in choices if choice.is_correct}
                graded.append((question, choices, selected, correct, selected == correct))
            correct_count = sum(item[4] for item in graded)
            question_count = len(questions)
            score = (Decimal(correct_count) * 100 / question_count).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            attempt = QuizAttempt.objects.create(
                quiz=quiz, student=student, submission_id=submission_id, request_digest=digest,
                score=score, correct_count=correct_count, question_count=question_count,
                passing_percentage=quiz.passing_percentage,
                passed=correct_count * 100 >= quiz.passing_percentage * question_count,
            )
            QuizAnswer.objects.bulk_create([QuizAnswer(
                attempt=attempt, question=question, selected_choice_ids=sorted(selected), is_correct=is_correct,
                snapshot={
                    "id": question.pk, "text": question.text, "type": question.type, "order": question.order,
                    "choices": [{"id": choice.pk, "text": choice.text, "order": choice.order} for choice in choices],
                    "correct_choice_ids": sorted(correct), "explanation": question.explanation,
                },
            ) for question, choices, selected, correct, is_correct in graded])
            return attempt, True
    except IntegrityError:
        # Database uniqueness is the final guard against concurrent double-clicks.
        previous = existing_submission(quiz_id, student, submission_id, digest)
        if previous:
            return previous, False
        raise
