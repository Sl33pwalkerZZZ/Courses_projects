from django.contrib import admin

from .models import Assignment, Course, Direction, Lesson, LessonImage, Module


class LessonImageInline(admin.TabularInline):
    model = LessonImage
    extra = 1


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


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order")
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "module", "order")
    inlines = [LessonImageInline, AssignmentInline]
