"""Explicit title-anchor renames within the existing atomic lesson PATCH."""
import re
from rest_framework import serializers


def validate_section_renames(lesson, attrs):
    renames = attrs.get('section_renames', [])
    if not renames:
        return
    def reject():
        raise serializers.ValidationError({'section_renames': 'Section rename is ambiguous or stale. Reload the saved lesson and check unique headings and media placements.'})
    current = getattr(lesson, 'learning_content', None) if lesson else None
    old = getattr(current, 'source_sections', [])
    mapping = {item['from']: item['to'] for item in renames}
    targets = list(mapping.values())
    if (not old or len(set(old)) != len(old) or len(mapping) != len(renames)
            or len(set(targets)) != len(targets) or any(source not in old or source == target or target in old
                                                      or '\n' in target or '\r' in target
                                                      for source, target in mapping.items())):
        reject()
    paragraphs = lambda body: [p.strip() for p in re.split(r'\n\s*\n', body) if p.strip()]
    before = paragraphs(lesson.text_content)
    learning = attrs.get('learning_content', {})
    expected = [mapping.get(heading, heading) for heading in old]
    after = paragraphs(attrs.get('text_content', lesson.text_content))
    if (learning.get('source_sections') != expected
            or any(before.count(source) != 1 or target in before or after.count(target) != 1 or source in after
                   for source, target in mapping.items())
            or any(after.count(heading) != 1 for heading in expected)
            or [after.index(heading) for heading in expected] != sorted(after.index(heading) for heading in expected)):
        reject()
    # An orphan attachment must not silently become attached by a new title.
    if lesson.attachments.filter(after_section__in=targets).exists():
        reject()
    interactions = learning.get('interactions', current.interactions)
    for item in current.interactions:
        if item.get('type') == 'image_placement' and item.get('after_section') in mapping:
            matches = [i for i in interactions if i.get('type') == 'image_placement' and i.get('image_id') == item['image_id']]
            if len(matches) != 1 or matches[0].get('after_section') != mapping[item['after_section']]:
                reject()
    if any(i.get('type') == 'image_placement' and i.get('after_section') in targets
           and not any(old_i.get('type') == 'image_placement' and old_i.get('image_id') == i.get('image_id')
                       and old_i.get('after_section') in mapping for old_i in current.interactions)
           for i in interactions):
        reject()
