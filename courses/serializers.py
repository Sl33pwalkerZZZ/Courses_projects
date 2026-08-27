from rest_framework import serializers

from .models import Assignment, Course, Direction, Lesson, LessonImage, Module


class DirectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direction
        fields = ["id", "name", "slug"]


class CourseListSerializer(serializers.ModelSerializer):
    direction = DirectionSerializer(read_only=True)
    author = serializers.StringRelatedField()

    class Meta:
        model = Course
        fields = ["id", "title", "slug", "description", "direction", "level", "author"]


class LessonSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "title", "order"]


class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSummarySerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ["id", "title", "order", "lessons"]


class CourseDetailSerializer(serializers.ModelSerializer):
    direction = DirectionSerializer(read_only=True)
    author = serializers.StringRelatedField()
    modules = ModuleSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ["id", "title", "slug", "description", "direction", "level", "author", "modules"]


class LessonImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonImage
        fields = ["id", "image", "order"]


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ["id", "type", "description"]


class LessonDetailSerializer(serializers.ModelSerializer):
    images = LessonImageSerializer(many=True, read_only=True)
    assignments = AssignmentSerializer(many=True, read_only=True)
    course_slug = serializers.CharField(source="module.course.slug", read_only=True)

    class Meta:
        model = Lesson
        fields = ["id", "title", "order", "text_content", "images", "assignments", "course_slug"]
