from django.contrib import admin

from .forms import ChoiceInlineFormSet, QuestionInlineFormSet
from .models import Quiz, QuizAnswer, QuizAttempt, QuizChoice, QuizQuestion


class QuestionInline(admin.TabularInline):
    model = QuizQuestion
    formset = QuestionInlineFormSet
    fields = ("text", "type", "order")
    extra = 0
    show_change_link = True

    def get_readonly_fields(self, request, obj=None):
        return self.fields if obj and obj.is_published else ()

    def has_add_permission(self, request, obj=None):
        return not (obj and obj.is_published) and super().has_add_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return not (obj and obj.is_published) and super().has_delete_permission(request, obj)


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "lesson", "passing_percentage", "is_published")
    list_filter = ("is_published",)
    search_fields = ("title", "lesson__title")
    list_select_related = ("lesson",)
    raw_id_fields = ("lesson",)
    inlines = (QuestionInline,)
    actions = None

    def get_readonly_fields(self, request, obj=None):
        return ("lesson",) if obj and obj.attempts.exists() else ()

    def has_delete_permission(self, request, obj=None):
        return not (obj and obj.attempts.exists()) and super().has_delete_permission(request, obj)


class ChoiceInline(admin.TabularInline):
    model = QuizChoice
    formset = ChoiceInlineFormSet
    fields = ("text", "order", "is_correct")
    extra = 2

    def get_readonly_fields(self, request, obj=None):
        return self.fields if obj and obj.quiz.is_published else ()

    def has_add_permission(self, request, obj=None):
        return not (obj and obj.quiz.is_published) and super().has_add_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return not (obj and obj.quiz.is_published) and super().has_delete_permission(request, obj)


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "quiz", "type", "order")
    list_filter = ("type", "quiz")
    search_fields = ("text", "quiz__title")
    list_select_related = ("quiz",)
    inlines = (ChoiceInline,)
    actions = None

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.quiz.is_published:
            return ("quiz", "text", "type", "order", "explanation")
        return ()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "quiz":
            kwargs["queryset"] = Quiz.objects.filter(is_published=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def has_delete_permission(self, request, obj=None):
        return not (obj and obj.quiz.is_published) and super().has_delete_permission(request, obj)


class AnswerInline(admin.TabularInline):
    model = QuizAnswer
    fields = ("snapshot", "selected_choice_ids", "is_correct")
    readonly_fields = fields
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("student", "quiz", "score", "passed", "submitted_at")
    list_filter = ("passed", "quiz", "submitted_at")
    search_fields = ("student__username", "quiz__title")
    list_select_related = ("student", "quiz")
    readonly_fields = tuple(field.name for field in QuizAttempt._meta.fields)
    inlines = (AnswerInline,)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
