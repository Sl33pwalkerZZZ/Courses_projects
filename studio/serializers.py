from rest_framework import serializers
from courses.models import Course, Module, Lesson, Assignment
from quizzes.validation import validate_choices
from django.core.exceptions import ValidationError as DjangoValidationError


class CourseWriteSerializer(serializers.ModelSerializer):
    language = serializers.ChoiceField(choices=['ru', 'kk', 'en'], default='ru')

    class Meta:
        model = Course
        fields = ['title', 'description', 'direction', 'level', 'enrollment_mode', 'language']
        extra_kwargs = {'title': {'allow_blank': False}, 'description': {'allow_blank': False}}

    def validate(self, attrs):
        unknown = set(self.initial_data) - set(self.fields)
        if unknown:
            raise serializers.ValidationError({field: 'This field cannot be edited.' for field in unknown})
        return attrs


class ModuleWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['title']


class LearningContentSerializer(serializers.Serializer):
    content_language = serializers.ChoiceField(choices=['ru', 'kk', 'en'])
    source_sections = serializers.ListField(child=serializers.CharField(max_length=255), max_length=100, required=False)
    objectives = serializers.ListField(child=serializers.CharField(max_length=1000), max_length=30, required=False)
    interactions = serializers.JSONField(required=False)

    def validate_interactions(self, value):
        # Editing supports bounded declarative teaching sections, never scripts/HTML.
        import json
        if not isinstance(value, list) or len(value) > 50 or len(json.dumps(value)) > 150000:
            raise serializers.ValidationError('Provide at most 50 bounded teaching sections.')
        allowed = {'concept_hierarchy', 'llm_steps', 'model_service', 'categories', 'service_overview', 'selection_steps', 'image_placement'}
        for item in value:
            if not isinstance(item, dict) or item.get('type') not in allowed:
                raise serializers.ValidationError('Unsupported teaching section type.')
        def strings(values):
            return isinstance(values, list) and len(values) <= 100 and all(isinstance(v, str) and len(v) <= 20000 for v in values)
        for item in value:
            if item['type'] == 'image_placement':
                if (set(item) != {'type', 'image_id', 'after_section', 'caption'}
                        or type(item['image_id']) is not int or item['image_id'] <= 0
                        or any(not isinstance(item[k], str) or not item[k].strip() or len(item[k]) > limit
                               for k, limit in [('after_section', 255), ('caption', 2000)])):
                    raise serializers.ValidationError('Invalid image placement.')
                continue
            for key, field in item.items():
                if key in ('items', 'steps', 'cards', 'services'):
                    if not isinstance(field, list) or len(field) > 100:
                        raise serializers.ValidationError('Teaching items must be a bounded list.')
                    for entry in field:
                        if isinstance(entry, str) and len(entry) <= 20000:
                            continue
                        if not isinstance(entry, dict) or any(k not in ('title', 'name', 'label', 'text', 'description', 'body', 'url', 'details', 'examples') for k in entry):
                            raise serializers.ValidationError('Invalid teaching item.')
                        for k, v in entry.items():
                            if not (strings(v) if k == 'examples' else isinstance(v, str) and len(v) <= 20000):
                                raise serializers.ValidationError('Teaching item text must be plain text.')
                elif key == 'rows':
                    if not isinstance(field, list) or len(field) > 100 or not all(strings(row) for row in field):
                        raise serializers.ValidationError('Table rows must contain plain text cells.')
                elif key in ('headers', 'criteria'):
                    if not strings(field):
                        raise serializers.ValidationError('Table headers and criteria must be plain text lists.')
                elif not isinstance(field, str) or len(field) > 20000:
                    raise serializers.ValidationError('Teaching content must be plain text.')
        return value


class LessonWriteSerializer(serializers.ModelSerializer):
    learning_content = LearningContentSerializer(required=False)

    def validate(self, attrs):
        learning = attrs.get('learning_content', {})
        placements = [i for i in learning.get('interactions', []) if i.get('type') == 'image_placement']
        if placements:
            ids = [i['image_id'] for i in placements]
            allowed = set(self.instance.images.values_list('pk', flat=True)) if self.instance else set()
            current = getattr(self.instance, 'learning_content', None) if self.instance else None
            sections = learning.get('source_sections', getattr(current, 'source_sections', []))
            body = attrs.get('text_content', getattr(self.instance, 'text_content', ''))
            paragraphs = body.split('\n\n')
            if (len(ids) != len(set(ids)) or not set(ids).issubset(allowed)
                    or any(i['after_section'] not in sections or paragraphs.count(i['after_section']) != 1 for i in placements)):
                raise serializers.ValidationError('Image placements must reference this lesson and unique existing section anchors.')
        return attrs

    class Meta:
        model = Lesson
        fields = ['title', 'text_content', 'learning_content']
        extra_kwargs = {'text_content': {'allow_blank': True}}


class AssignmentWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['type', 'description', 'learning_activity']

    def validate_learning_activity(self, value):
        if value not in ('', 'ai_selection_map'):
            raise serializers.ValidationError('Unsupported learning activity.')
        return value

    def validate(self, data):
        activity = data.get('learning_activity', getattr(self.instance, 'learning_activity', ''))
        assignment_type = data.get('type', getattr(self.instance, 'type', 'text'))
        if activity == 'ai_selection_map' and assignment_type != 'text':
            raise serializers.ValidationError('Selection maps use text assignments.')
        return data


class ChoiceWriteSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=10000)
    is_correct = serializers.BooleanField()


class QuestionWriteSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=20000)
    type = serializers.ChoiceField(choices=['single', 'multiple'])
    explanation = serializers.CharField(max_length=20000, allow_blank=True, required=False, default='')
    choices = ChoiceWriteSerializer(many=True, min_length=2, max_length=20)

    def validate(self, attrs):
        try:
            validate_choices(attrs['type'], attrs['choices'])
        except DjangoValidationError as error:
            raise serializers.ValidationError(error.messages)
        return attrs


class QuizWriteSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    instructions = serializers.CharField(max_length=20000, allow_blank=True, required=False, default='')
    passing_percentage = serializers.IntegerField(min_value=0, max_value=100)
    questions = QuestionWriteSerializer(many=True, min_length=1, max_length=100)


class ReviewWriteSerializer(serializers.Serializer):
    revision = serializers.IntegerField(min_value=0)
    status = serializers.ChoiceField(choices=['approved', 'rejected'])
    reviewer_comment = serializers.CharField(max_length=10000, allow_blank=True, required=False, default='')

    def validate(self, attrs):
        if attrs['status'] == 'rejected' and not attrs['reviewer_comment'].strip():
            raise serializers.ValidationError({'reviewer_comment': 'Explain what the student should improve.'})
        return attrs


class EnrollmentDecisionSerializer(serializers.Serializer):
    decision = serializers.ChoiceField(choices=['approve', 'reject'])
    note = serializers.CharField(max_length=10000, allow_blank=True, required=False, default='')

    def validate(self, attrs):
        unknown = set(self.initial_data) - set(self.fields)
        if unknown:
            raise serializers.ValidationError({field: 'This field cannot be edited.' for field in unknown})
        return attrs
