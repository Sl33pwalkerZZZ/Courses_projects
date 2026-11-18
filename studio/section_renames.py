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
    if (learning.get('source_sections', [])[:len(expected)] != expected
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


def validate_section_additions(lesson, attrs):
    """Only new exact title anchors get stricter checks; unchanged legacy stays editable."""
    learning = attrs.get('learning_content', {})
    if 'source_sections' not in learning:
        return
    current = getattr(lesson, 'learning_content', None) if lesson else None
    old = getattr(current, 'source_sections', [])
    mapping = {item['from']: item['to'] for item in attrs.get('section_renames', [])}
    expected = [mapping.get(heading, heading) for heading in old]
    headings = learning['source_sections']
    if headings == expected:
        return
    # Existing legacy metadata is not retroactively normalized. Any new anchor
    # must be an append, preserving saved section order (and explicit renames).
    if len(headings) <= len(expected) and all(h in expected for h in headings):
        return
    def reject():
        raise serializers.ValidationError({'section_additions': 'Add unique section headings in order with their text. Preserve existing sections and resolve conflicting media anchors.'})
    if headings[:len(expected)] != expected or len(headings) <= len(expected):
        reject()
    added = headings[len(expected):]
    before_body = getattr(lesson, 'text_content', '') if lesson else ''
    paragraphs = lambda body: [p.strip() for p in re.split(r'\n\s*\n', body) if p.strip()]
    before = paragraphs(before_body)
    after = paragraphs(attrs.get('text_content', before_body))
    interactions = learning.get('interactions', getattr(current, 'interactions', []))
    if (len(set(headings)) != len(headings)
            or any(not h.strip() or h != h.strip() or '\n' in h or '\r' in h for h in headings)
            or any(after.count(h) != 1 for h in headings)
            or not after or after[0] != headings[0]
            or any(h in before for h in added)
            or any(item.get('type') != 'image_placement' for item in interactions)):
        reject()
    positions = [after.index(h) for h in headings]
    if positions != sorted(positions):
        reject()
    for heading in added:
        index = headings.index(heading)
        end = positions[index + 1] if index + 1 < len(headings) else len(after)
        if end <= positions[index] + 1:
            reject()
    if lesson and lesson.attachments.filter(after_section__in=added).exists():
        reject()
    if any(i.get('type') == 'image_placement' and i.get('after_section') in added
           for i in getattr(current, 'interactions', [])):
        reject()
