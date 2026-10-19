from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Assignment, Course, Direction, Lesson, LessonImage, LessonLearningContent, CourseImport, Module


class LessonImageInline(admin.TabularInline):
    model = LessonImage
    extra = 1


class LessonLearningContentInline(admin.StackedInline):
    model = LessonLearningContent
    extra = 0
    max_num = 1


class AssignmentInline(admin.TabularInline):
    model = Assignment
    extra = 0


class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 0


class ModuleInline(admin.StackedInline):
    model = Module
    extra = 0


@admin.register(Direction)
class DirectionAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "direction", "level", "author", "is_published", "enrollment_mode")
    list_filter = ("direction", "level", "is_published", "enrollment_mode")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ModuleInline]
    readonly_fields = ("draft_preview",)

    @admin.display(description="Authorized draft preview")
    def draft_preview(self, obj):
        if not obj.pk:
            return "Save the course first."
        url = reverse("instructor-course-preview", kwargs={"slug": obj.slug})
        return format_html('<a href="{}">Preview course API (staff only)</a>', url)


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order")
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "module", "order")
    inlines = [LessonImageInline, AssignmentInline, LessonLearningContentInline]


@admin.register(CourseImport)
class CourseImportAdmin(admin.ModelAdmin):
    list_display = ("course", "version", "content_language", "review_approved", "created_at")
    readonly_fields = ("course", "source_name", "source_sha256", "manifest_sha256", "content_sha256", "version", "content_language", "created_at")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
