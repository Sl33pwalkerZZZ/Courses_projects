"""Title-anchor moves; caller holds the existing course authoring transaction."""
import re
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class AttachmentPlacementSerializer(serializers.Serializer):
    after_section = serializers.CharField(max_length=255)
    expected_after_section = serializers.CharField(max_length=255, allow_blank=True, trim_whitespace=False)
    expected_sections = serializers.ListField(child=serializers.CharField(max_length=255, trim_whitespace=False), max_length=100)
    expected_subtitle_id = serializers.IntegerField(min_value=1, allow_null=True)

    def to_internal_value(self, data):
        if isinstance(data, dict) and set(data) - set(self.fields):
            raise ValidationError({'placement_error': 'invalid'})
        return super().to_internal_value(data)


def reject(code):
    raise ValidationError({'placement_error': code})


def placement_ids(lesson, asset, data):
    content = getattr(lesson, 'learning_content', None)
    headings = getattr(content, 'source_sections', [])
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', lesson.text_content) if p.strip()]
    target = data['after_section']
    if data['expected_sections'] != headings or data['expected_after_section'] != asset.after_section:
        reject('stale')
    if (not headings or paragraphs[:1] != headings[:1]
            or any(item.get('type') != 'image_placement' for item in getattr(content, 'interactions', [])) or len(set(headings)) != len(headings) or target not in headings
            or any(paragraphs.count(h) != 1 for h in headings)
            or [paragraphs.index(h) for h in headings] != sorted(paragraphs.index(h) for h in headings)):
        reject('invalid')
    # VTT can only move with its uniquely linked video in this slice.
    if asset.kind == 'vtt':
        reject('track')
    ids = [asset.pk]
    expected_subtitle = None
    if asset.kind == 'video':
        source = list(lesson.attachments.filter(after_section=asset.after_section))
        videos = [a for a in source if a.kind == 'video']
        tracks = [a for a in source if a.kind == 'vtt']
        if asset.after_section and (len(videos) != 1 or len(tracks) > 1):
            reject('ambiguous')
        if asset.after_section and len(videos) == 1 and len(tracks) == 1:
            expected_subtitle = tracks[0].pk
            ids.append(expected_subtitle)
        if target != asset.after_section and lesson.attachments.filter(after_section=target, kind__in=['video', 'vtt']).exclude(pk__in=ids).exists():
            reject('ambiguous')
    elif asset.kind not in ('audio', 'srt'):
        reject('invalid')
    if data['expected_subtitle_id'] != expected_subtitle:
        reject('stale')
    return ids
