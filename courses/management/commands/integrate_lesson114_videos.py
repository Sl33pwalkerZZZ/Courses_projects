"""Exact, reviewed local Lesson 114 integration; no generic content overwrite."""
import hashlib
import json
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from courses.attachments import store_attachment, validate_file, validate_metadata
from courses.management.commands.integrate_lesson113_videos import database_health, verified_backup
from courses.models import Course, Lesson, LessonAttachment

PLAN = Path(__file__).resolve().parents[1] / 'lesson114_quality_v2.json'
PLAN_SHA256 = '4ca3f4938ef67abe3749d4287c800d9d02e4e3f5f58ff8a2c0c64fffd159ca5f'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load_plan():
    raw = PLAN.read_bytes()
    if sha(raw) != PLAN_SHA256:
        raise CommandError('Reviewed integration plan checksum differs; stop for review.')
    plan = json.loads(raw)
    change = plan['change']
    text = change['before']
    if sha(text.encode()) != change['before_sha256'] or len(change['edits']) != 8:
        raise CommandError('Invalid original text or paragraph-edit count.')
    for edit in change['edits']:
        if text.count(edit['before']) != 1:
            raise CommandError('Ambiguous approved paragraph edit.')
        text = text.replace(edit['before'], edit['after'], 1)
    if text != change['after'] or sha(text.encode()) != change['after_sha256']:
        raise CommandError('Approved after-text does not match exact edits.')
    if [a['kind'] for a in plan['assets']] != ['video', 'video', 'video', 'vtt', 'vtt']:
        raise CommandError('Expected exactly three approved videos and two spoken-sample tracks.')
    return plan


def target(plan, *, lock=False):
    course = (Course.objects.select_for_update() if lock else Course.objects).get(pk=10)
    if course.slug != 'ai-media-content' or course.is_published:
        raise CommandError('Expected existing unpublished course 10, ai-media-content.')
    lesson = Lesson.objects.select_related('module', 'learning_content').get(pk=114)
    expected = plan['expected']
    learning = lesson.learning_content
    if (lesson.module_id != 39 or lesson.module.course_id != course.pk or lesson.module.order != 5
            or lesson.order != 2 or lesson.title != expected['title'] or learning.pk != 21
            or any(getattr(learning, key) != expected['learning_content'][key]
                   for key in ('objectives', 'source_sections', 'interactions', 'content_language'))
            or list(course.modules.order_by('order').values_list('order', flat=True)) != [1, 2, 3, 4, 5]
            or Lesson.objects.filter(module__course=course).count() != 15
            or list(lesson.module.lessons.order_by('order').values_list('pk', flat=True)) != [113, 114, 115]):
        raise CommandError('Unexpected target structure/learning metadata; nothing overwritten.')
    rows = list(lesson.attachments.all())
    if lesson.text_content == plan['change']['before'] and not rows:
        return lesson, 'BEFORE'
    if lesson.text_content == plan['change']['after'] and len(rows) == 5:
        for order, (row, asset) in enumerate(zip(rows, plan['assets']), 1):
            if (row.order != order or row.filename != Path(asset['path']).name or row.sha256 != asset['sha256']
                    or row.kind != asset['kind'] or row.mime_type != asset['mime_type']
                    or any(getattr(row, k) != v for k, v in asset['metadata'].items())):
                raise CommandError('Completed attachment state conflicts; no overwrite.')
            with row.file.storage.open(row.file.name, 'rb') as stream:
                if sha(stream.read()) != row.sha256:
                    raise CommandError('Stored protected attachment checksum mismatch.')
        return lesson, 'AFTER'
    raise CommandError('Unexpected/mixed lesson text or attachment state; no overwrite.')


def verify_cues(raw, asset):
    # validate_file has already checked WebVTT syntax and ordered, plain-text cues.
    cues = []
    def milliseconds(timestamp):
        hours, minutes, seconds = timestamp.split(':')
        return (int(hours)*3600 + int(minutes)*60)*1000 + round(float(seconds)*1000)
    for block in raw.decode('utf-8-sig').replace('\r\n', '\n').strip().split('\n\n')[1:]:
        lines = block.splitlines()
        if '-->' not in lines[0]:
            lines = lines[1:]
        start, end = lines[0].split(' --> ')
        cues.append({'start_ms': milliseconds(start), 'end_ms': milliseconds(end), 'text': '\n'.join(lines[1:])})
    if cues != asset['expected_cues'] or any(c['end_ms'] > asset['video_seconds']*1000 for c in cues):
        raise CommandError('Spoken-sample WebVTT differs from verified speech boundaries/text.')


def prevalidate(plan, lesson):
    assets = []
    root = Path(settings.BASE_DIR).resolve()
    lesson.text_content = plan['change']['after']  # Validate proposed anchors without saving.
    for index, asset in enumerate(plan['assets']):
        path = (root / asset['path']).resolve()
        directory = 'out/final' if asset['kind'] == 'video' else 'content'
        if not path.is_relative_to(root / 'video-production/lesson-114-production' / directory):
            raise CommandError('Approved asset path escapes its production directory.')
        raw = path.read_bytes()
        if sha(raw) != asset['sha256']:
            raise CommandError(f'Approved asset checksum differs: {path.name}')
        if validate_file(path.name, raw) != (asset['kind'], asset['mime_type']):
            raise CommandError('Unexpected protected attachment type.')
        validate_metadata(lesson, asset['kind'], asset['metadata'])
        if asset['metadata']['after_section'] != lesson.learning_content.source_sections[[2, 4, 6, 4, 6][index]]:
            raise CommandError('Expected exact sections 3/5/7 and paired tracks 5/7.')
        if asset['kind'] == 'vtt':
            verify_cues(raw, asset)
        assets.append((path, raw, asset['metadata']))
    return assets


def integrate(plan, assets):
    created_files = []
    try:
        with transaction.atomic():
            lesson, state = target(plan, lock=True)
            if state == 'AFTER':
                return list(lesson.attachments.values_list('pk', flat=True))
            lesson.text_content = plan['change']['after']
            lesson.full_clean()
            lesson.save(update_fields=['text_content'])
            for path, raw, metadata in assets:
                store_attachment(lesson, path.name, raw, metadata, created_files)
            result, state = target(plan)
            if state != 'AFTER':
                raise CommandError('Post-write state verification failed.')
            return list(result.attachments.values_list('pk', flat=True))
    except Exception as exc:
        failures = []
        for storage, name in reversed(created_files):
            try:
                storage.delete(name)
            except Exception:
                failures.append(name)
        if failures:
            raise CommandError('Database rolled back; newly created files need manual cleanup: ' + ', '.join(failures)) from exc
        raise


class Command(BaseCommand):
    help = 'Integrate the three approved Quality V2 videos, two scoped VTT tracks and exact eight edits into existing Lesson 114 only.'

    def add_arguments(self, parser):
        modes = parser.add_mutually_exclusive_group()
        modes.add_argument('--dry-run', action='store_true')
        modes.add_argument('--apply', action='store_true')
        parser.add_argument('--backup-dir', type=Path, default=Path(settings.BASE_DIR)/'.local-course-backups')

    def handle(self, *args, **options):
        try:
            plan = load_plan()
            lesson, state = target(plan)
            assets = prevalidate(plan, lesson)
            # Restore in-memory text for an accurate before-state backup.
            lesson.refresh_from_db(fields=['text_content'])
            if state == 'AFTER':
                self.stdout.write('KEEP 5 (3 videos + 2 VTT);  approved text unchanged; no-op, no backup or writes.')
                return
            database_health()
            for path, _, metadata in assets:
                self.stdout.write(f'CREATE attachment: {path.name} -> {metadata["after_section"]}')
            self.stdout.write('UPDATE Lesson 114 text: exactly eight approved edits; preserve 3 objectives/9 headings.')
            if not options['apply']:
                self.stdout.write('Dry-run: no database/media/backup writes.')
                return
            folder = verified_backup(options['backup_dir'], lesson, assets, prefix='lesson114-phase5k')
            self.stdout.write(f'Verified SQLite/media/source backup: {folder}')
            ids = integrate(plan, assets)
            self.stdout.write(f'Integrated lesson114; attachment IDs {ids}; course remains unpublished.')
        except (OSError, ValidationError, Course.DoesNotExist, Lesson.DoesNotExist) as exc:
            raise CommandError(f'Integration stopped: {exc}') from exc
