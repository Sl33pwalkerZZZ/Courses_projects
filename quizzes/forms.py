from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from .validation import validate_choices


class ChoiceInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors) or not self.instance.quiz_id:
            return
        choices = []
        for form in self.forms:
            data = form.cleaned_data
            if not data or data.get("DELETE"):
                continue
            # Published questions have read-only inline fields.
            if self.instance.quiz.is_published:
                choices.append({"text": form.instance.text, "is_correct": form.instance.is_correct})
            else:
                choices.append({"text": data["text"], "is_correct": data.get("is_correct", False)})
        validate_choices(self.instance.type, choices)


class QuestionInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors) or not self.instance.is_published:
            return
        questions = [form.instance for form in self.forms if form.cleaned_data and not form.cleaned_data.get("DELETE")]
        if not questions:
            raise ValidationError("A published quiz needs at least one question.")
        for question in questions:
            validate_choices(question.type, [
                {"text": choice.text, "is_correct": choice.is_correct}
                for choice in question.choices.all()
            ] if question.pk else [])
