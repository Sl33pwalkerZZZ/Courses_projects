from rest_framework import serializers

from courses.serializers import CourseListSerializer

from .models import Enrollment, LessonProgress


class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseListSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ["id", "course", "granted_at"]


class EnrollmentProgressSerializer(EnrollmentSerializer):
    total_lessons = serializers.SerializerMethodField()
    completed_lessons = serializers.SerializerMethodField()
    progress_percent = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()
    next_lesson_id = serializers.SerializerMethodField()
    next_lesson_title = serializers.SerializerMethodField()

    class Meta(EnrollmentSerializer.Meta):
        fields = EnrollmentSerializer.Meta.fields + [
            "total_lessons", "completed_lessons", "progress_percent", "is_completed",
            "next_lesson_id", "next_lesson_title",
        ]

    def to_representation(self, enrollment):
        # MyEnrollmentsView prefetches the curriculum in module/lesson order.
        lessons = [
            lesson
            for module in enrollment.course.modules.all()
            for lesson in module.lessons.all()
        ]
        completed_ids = {
            progress.lesson_id
            for progress in enrollment.lesson_progress.all()
            if progress.completed_at is not None
        }
        # Intersect with this curriculum: a malformed progress row for another
        # course must not increase this enrollment's completion count.
        total = len(lessons)
        completed = sum(lesson.id in completed_ids for lesson in lessons)
        next_lesson = next((lesson for lesson in lessons if lesson.id not in completed_ids), None)
        self._summary = {
            "total_lessons": total,
            "completed_lessons": completed,
            "progress_percent": completed / total * 100 if total else 0.0,
            "is_completed": total > 0 and completed == total,
            "next_lesson_id": next_lesson.id if next_lesson else None,
            "next_lesson_title": next_lesson.title if next_lesson else None,
        }
        return super().to_representation(enrollment)

    def get_total_lessons(self, enrollment):
        return self._summary["total_lessons"]

    def get_completed_lessons(self, enrollment):
        return self._summary["completed_lessons"]

    def get_progress_percent(self, enrollment):
        return self._summary["progress_percent"]

    def get_is_completed(self, enrollment):
        return self._summary["is_completed"]

    def get_next_lesson_id(self, enrollment):
        return self._summary["next_lesson_id"]

    def get_next_lesson_title(self, enrollment):
        return self._summary["next_lesson_title"]


class LessonProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonProgress
        fields = ["id", "lesson", "completed_at"]
