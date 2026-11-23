"""Exact C1 content update only. Never edits a quiz, review or certificate policy."""
import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction

from courses.management.course10_editorial import load_corrections
from courses.management.commands.import_media_module import create_backup
from courses.models import Course


def correction_plan():
    source = load_corrections()
    course = Course.objects.filter(pk=source['course_id'], slug=source['slug'], is_published=False).first()
    if course is None:
        raise CommandError('Expected unpublished Course 10; nothing changed.')
    plan = []
    targets = []
    for edit in source['lessons']:
        lessons = course.modules.filter(order=edit['module_order'])
        if lessons.count() != 1:
            raise CommandError('Ambiguous target module; nothing changed.')
        lessons = lessons.get().lessons.filter(order=edit['lesson_order'], title=edit['title'])
        if lessons.count() != 1:
            raise CommandError('Missing or ambiguous target lesson; nothing changed.')
        lesson = lessons.get()
        learning = getattr(lesson, 'learning_content', None)
        if learning is None or learning.interactions:
            raise CommandError('Unexpected structured content; manual review required.')
        current = {'text_content': lesson.text_content, 'source_sections': learning.source_sections}
        if current not in (edit['before'], edit['after']):
            raise CommandError(f'Conflicting lesson {lesson.pk}; no overwrite permitted.')
        # No media may silently lose an old title anchor. C1 has no media writes.
        changed = set(edit['before']['source_sections']) - set(edit['after']['source_sections'])
        if lesson.attachments.filter(after_section__in=changed).exists():
            raise CommandError('Renamed heading has media references; manual review required.')
        if current != edit['after']:
            plan.append((lesson, 'text_content', lesson.text_content, edit['after']['text_content']))
            if learning.source_sections != edit['after']['source_sections']:
                plan.append((learning, 'source_sections', learning.source_sections, edit['after']['source_sections']))
        targets.append(lesson)
    edit = source['assignment']
    assignments = targets[-1].assignments.filter(learning_activity=edit['learning_activity'])
    if assignments.count() != 1:
        raise CommandError('Expected exactly one final media project.')
    assignment = assignments.get()
    if assignment.type != 'text' or assignment.description not in (edit['before'], edit['after']):
        raise CommandError('Conflicting final assignment; no overwrite permitted.')
    if assignment.description != edit['after']:
        plan.append((assignment, 'description', assignment.description, edit['after']))
    return plan


def write_plan(plan):
    for row, field, before, after in plan:
        if type(row).objects.filter(pk=row.pk, **{field: before}).update(**{field: after}) != 1:
            raise CommandError('Concurrent content change; transaction rolled back.')


class Command(BaseCommand):
    help = 'Preview/apply only approved Course 10 C1 text corrections after verified SQLite backup. No quiz changes.'

    def add_arguments(self, parser):
        mode = parser.add_mutually_exclusive_group()
        mode.add_argument('--dry-run', action='store_true')
        mode.add_argument('--apply', action='store_true')
        parser.add_argument('--backup-dir', type=Path, default=Path(settings.BASE_DIR) / '.local-course-backups')

    def handle(self, *args, **options):
        plan = correction_plan()
        self.stdout.write(json.dumps({'mode': 'apply' if options['apply'] else 'dry-run',
            'updates': [{'model': row._meta.label, 'id': row.pk, 'field': field} for row, field, _, _ in plan],
            'quiz_changes': 0, 'publication_changes': 0, 'certificate_changes': 0}, ensure_ascii=False))
        if not options['apply'] or not plan:
            return
        if connection.vendor != 'sqlite' or connection.in_atomic_block:
            raise CommandError('A standalone SQLite transaction is required.')
        # Acquire the SQLite write reservation before validating and backing up.
        previous = connection.transaction_mode
        try:
            connection.transaction_mode = 'IMMEDIATE'
            with transaction.atomic():
                plan = correction_plan()
                if not plan:
                    return
                backup = create_backup(settings.DATABASES['default']['NAME'], options['backup_dir'])
                self.stdout.write(f'Verified SQLite backup: {backup}')
                write_plan(plan)
                if correction_plan():
                    raise CommandError('Editorial post-validation failed; rolled back.')
        finally:
            connection.transaction_mode = previous
