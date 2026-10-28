from rest_framework import serializers
from django.urls import reverse

from progress.models import LessonProgress
from reviews.summaries import display_average

from .models import Assignment, Course, Direction, Lesson, LessonImage, LessonLearningContent, LessonAttachment, Module
from .image_descriptions import image_alt_text, load_image_descriptions


class DirectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direction
        fields = ["id", "name", "slug"]


class CourseListSerializer(serializers.ModelSerializer):
    direction = DirectionSerializer(read_only=True)
    author = serializers.StringRelatedField()
    content_language = serializers.SerializerMethodField()

    def get_content_language(self, course):
        studio_settings = getattr(course, 'studio_settings', None)
        if studio_settings:
            return studio_settings.language
        imported = getattr(course, "content_import", None)
        return imported.content_language if imported else None

    class Meta:
        model = Course
        fields = ["id", "title", "slug", "description", "direction", "level", "author", "enrollment_mode", "content_language"]


class RatedCourseListSerializer(CourseListSerializer):
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.IntegerField(read_only=True)

    class Meta(CourseListSerializer.Meta):
        fields = CourseListSerializer.Meta.fields + ["average_rating", "review_count"]

    def get_average_rating(self, course):
        return display_average(course.average_rating)


class LessonSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "title", "order"]


class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSummarySerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ["id", "title", "order", "lessons"]


class CourseDetailSerializer(RatedCourseListSerializer):
    modules = ModuleSerializer(many=True, read_only=True)

    class Meta(RatedCourseListSerializer.Meta):
        fields = RatedCourseListSerializer.Meta.fields + ["modules"]


class LessonImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    alt_text = serializers.SerializerMethodField()

    def get_image(self, image):
        # Never expose FileField/storage URLs in the student API.
        return reverse("lesson-image", args=[image.pk])

    def get_alt_text(self, image):
        description = getattr(image, 'studio_description', None) if not image._state.adding else None
        if description is not None:
            return {} if description.decorative else description.alt_text
        # Nested images share the lesson serializer's context: one read per response.
        if "image_descriptions" not in self.context:
            self.context["image_descriptions"] = load_image_descriptions()
        return image_alt_text(self.context["image_descriptions"], image.pk)

    class Meta:
        model = LessonImage
        fields = ["id", "image", "order", "alt_text"]


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ["id", "type", "description", "learning_activity"]


class LessonLearningContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonLearningContent
        fields = ["content_language", "source_sections", "objectives", "interactions"]


class LessonAttachmentSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, attachment):
        return reverse('lesson-attachment', args=[attachment.pk])

    class Meta:
        model = LessonAttachment
        fields = ['id', 'kind', 'filename', 'mime_type', 'label', 'caption', 'transcript', 'after_section', 'order', 'url']


def lesson_attachments(lesson):
    from .attachments import attachments_ready
    return LessonAttachmentSerializer(lesson.attachments.all(), many=True).data if attachments_ready() else []


class LessonDetailSerializer(serializers.ModelSerializer):
    images = LessonImageSerializer(many=True, read_only=True)
    assignments = AssignmentSerializer(many=True, read_only=True)
    course_slug = serializers.CharField(source="module.course.slug", read_only=True)
    completed_at = serializers.SerializerMethodField()
    attachments = serializers.SerializerMethodField()

    def get_attachments(self, lesson):
        return lesson_attachments(lesson)
    learning_content = LessonLearningContentSerializer(read_only=True)

    def get_completed_at(self, lesson):
        completed_at = LessonProgress.objects.filter(
            lesson=lesson,
            enrollment__student=self.context["request"].user,
            enrollment__course_id=lesson.module.course_id,
        ).values_list("completed_at", flat=True).first()
        return serializers.DateTimeField().to_representation(completed_at) if completed_at else None

    class Meta:
        model = Lesson
        fields = ["id", "title", "order", "text_content", "images", "assignments", "course_slug", "completed_at", "learning_content", "attachments"]
