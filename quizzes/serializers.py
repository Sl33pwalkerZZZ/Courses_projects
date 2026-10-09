from rest_framework import serializers

from .models import Quiz, QuizAttempt, QuizChoice, QuizQuestion


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizChoice
        fields = ("id", "text", "order")


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = QuizQuestion
        fields = ("id", "text", "type", "order", "choices")


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ("id", "lesson_id", "title", "instructions", "passing_percentage", "questions")


class StrictSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        if isinstance(data, dict) and set(data) - set(self.fields):
            raise serializers.ValidationError({"non_field_errors": ["Unexpected submission fields."]})
        return super().to_internal_value(data)


class PositiveIDField(serializers.IntegerField):
    def to_internal_value(self, data):
        if type(data) is not int or data < 1:
            raise serializers.ValidationError("Use a positive integer ID.")
        return data


class SubmittedAnswerSerializer(StrictSerializer):
    question_id = PositiveIDField()
    choice_ids = serializers.ListField(child=PositiveIDField(), allow_empty=False)

    def validate_choice_ids(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Choice IDs cannot be repeated.")
        return value


class SubmissionSerializer(StrictSerializer):
    submission_id = serializers.UUIDField()
    answers = SubmittedAnswerSerializer(many=True, allow_empty=False)

    def validate_answers(self, value):
        ids = [answer["question_id"] for answer in value]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError("Question IDs cannot be repeated.")
        return value


class AttemptSummarySerializer(serializers.ModelSerializer):
    score = serializers.DecimalField(max_digits=5, decimal_places=2, coerce_to_string=False)

    class Meta:
        model = QuizAttempt
        fields = ("id", "quiz_id", "score", "passed", "correct_count", "question_count", "passing_percentage", "submitted_at")


class AttemptDetailSerializer(AttemptSummarySerializer):
    answers = serializers.SerializerMethodField()

    class Meta(AttemptSummarySerializer.Meta):
        fields = AttemptSummarySerializer.Meta.fields + ("submission_id", "answers")

    def get_answers(self, attempt):
        return [{
            "question_id": answer.snapshot["id"],
            "text": answer.snapshot["text"],
            "type": answer.snapshot["type"],
            "choices": answer.snapshot["choices"],
            "correct_choice_ids": answer.snapshot["correct_choice_ids"],
            "explanation": answer.snapshot["explanation"],
            "selected_choice_ids": answer.selected_choice_ids,
            "is_correct": answer.is_correct,
        } for answer in attempt.answers.all()]
