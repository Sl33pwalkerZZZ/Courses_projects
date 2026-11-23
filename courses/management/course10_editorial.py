"""Owner-approved C1 overlay; the historical DOCX and quiz remain byte-exact."""
import json
from pathlib import Path

from django.core.management.base import CommandError

PATCH = Path(__file__).with_name('media_course10_editorial.json')


def load_corrections():
    data = json.loads(PATCH.read_text(encoding='utf-8'))
    if (data['course_id'], data['slug']) != (10, 'ai-media-content') or [(entry['module_order'], entry['lesson_order']) for entry in data['lessons']] != [(1, 3), (6, 1)]:
        raise CommandError('C1 is restricted to Course 10 lessons 102/116 by curriculum position.')
    return data


def apply_module1_overlay(lesson):
    edit = load_corrections()['lessons'][0]
    if lesson['title'] != edit['title']:
        raise CommandError('Unexpected Module 1 editorial target.')
    current = {key: lesson[key] for key in edit['before']}
    if current == edit['after']:
        return lesson
    if current != edit['before']:
        raise CommandError('Module 1 source conflicts with the approved C1 baseline.')
    return {**lesson, **edit['after']}
