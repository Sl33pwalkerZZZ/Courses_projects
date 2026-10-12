from collections.abc import Mapping

from rest_framework import serializers

from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="student.username", read_only=True)

    class Meta:
        model = Review
        fields = ["id", "rating", "text", "created_at", "author"]
        read_only_fields = fields


class OwnReviewSerializer(ReviewSerializer):
    class Meta(ReviewSerializer.Meta):
        fields = ReviewSerializer.Meta.fields + ["status"]
        read_only_fields = fields


class ReviewCreateSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)
    text = serializers.CharField(allow_blank=False, trim_whitespace=True)

    class Meta:
        model = Review
        fields = ["rating", "text"]

    def to_internal_value(self, data):
        # Reject server-controlled and unknown fields rather than silently
        # accepting attempts to set the author or moderation state.
        unexpected = set(data) - set(self.fields) if isinstance(data, Mapping) else set()
        if unexpected:
            raise serializers.ValidationError({
                field: serializers.ErrorDetail("This field cannot be submitted.", code="read_only")
                for field in sorted(unexpected)
            })
        return super().to_internal_value(data)


class ReviewUpdateSerializer(ReviewCreateSerializer):
    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("Provide a rating or review text to update.", code="empty_update")
        return attrs

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        # Update content and moderation state in one write, preserving immutable
        # fields and avoiding insertion if a review was concurrently deleted.
        instance.save(update_fields=list(validated_data))
        return instance
