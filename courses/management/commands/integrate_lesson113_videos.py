"""Exact, reviewed local Lesson 113 integration; no generic content overwrite."""
import hashlib
import json
import shutil
import tarfile
from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.utils import timezone

from courses.attachments import store_attachment, validate_file, validate_metadata
from courses.management.commands.import_media_module import create_backup
from courses.models import Course, Lesson, LessonAttachment

PLAN = Path(__file__).resolve().parents[1] / 'lesson113_quality_v2.json'
PLAN_SHA256 = '054b65629f4a41ec33684f57dce47c32c7035591014dfce530a82b276352911a'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load_plan():
    raw = PLAN.read_bytes()
    if sha(raw) != PLAN_SHA256:
        raise CommandError('Reviewed integration plan checksum differs; stop for review.')
    plan = json.loads(raw)
    change = plan['change']
    text = change['before']
    if sha(text.encode()) != plan['expected_before']['text_sha256'] or len(change['edits']) != 10:
        raise CommandError('Invalid original text or paragraph-edit count.')
    for edit in change['edits']:
        if text.count(edit['before']) != 1:
            raise CommandError('Ambiguous approved paragraph edit.')
        text = text.replace(edit['before'], edit['after'], 1)
    if text != change['after'] or sha(text.encode()) != change['after_sha256']:
        raise CommandError('Approved after-text does not match exact edits.')
    if len(plan['assets']) != 3:
        raise CommandError('Expected exactly three approved videos.')
    return plan


def target(plan, *, lock=False):
    course = (Course.objects.select_for_update() if lock else Course.objects).get(pk=10)
    if course.slug != 'ai-media-content' or course.is_published:
        raise CommandError('Expected existing unpublished course 10, ai-media-content.')
    lesson = Lesson.objects.select_related('module', 'learning_content').get(pk=113)
    expected = plan['expected_before']
    learning = lesson.learning_content
    if (lesson.module_id != 39 or lesson.module.course_id != course.pk or lesson.module.order != 5
            or lesson.order != 1 or lesson.title != expected['title'] or learning.pk != 20
            or learning.objectives != expected['objectives'] or learning.source_sections != expected['source_sections']
            or learning.interactions != expected['interactions'] or learning.content_language != 'ru'
            or list(course.modules.order_by('order').values_list('order', flat=True)) != [1, 2, 3, 4, 5]
            or Lesson.objects.filter(module__course=course).count() != 15
            or list(lesson.module.lessons.order_by('order').values_list('pk', flat=True)) != [113, 114, 115]):
        raise CommandError('Unexpected target structure/learning metadata; nothing overwritten.')
    rows = list(lesson.attachments.all())
    if lesson.text_content == plan['change']['before'] and not rows:
        return lesson, 'BEFORE'
    if lesson.text_content == plan['change']['after'] and len(rows) == 3:
        for order, (row, asset) in enumerate(zip(rows, plan['assets']), 1):
            if (row.order != order or row.filename != Path(asset['path']).name or row.sha256 != asset['sha256']
                    or row.kind != 'video' or row.mime_type != 'video/mp4'
                    or any(getattr(row, k) != v for k, v in asset['metadata'].items())):
                raise CommandError('Completed attachment state conflicts; no overwrite.')
            with row.file.storage.open(row.file.name, 'rb') as stream:
                if sha(stream.read()) != row.sha256:
                    raise CommandError('Stored protected video checksum mismatch.')
        return lesson, 'AFTER'
    raise CommandError('Unexpected/mixed lesson text or attachment state; no overwrite.')


def prevalidate(plan, lesson):
    assets = []
    root = Path(settings.BASE_DIR).resolve()
    # Validate against the proposed text without saving it.
    lesson.text_content = plan['change']['after']
    for index, asset in enumerate(plan['assets']):
        path = (root / asset['path']).resolve()
        if not path.is_relative_to(root / 'video-production/lesson-113-production/out/quality-v2'):
            raise CommandError('Approved video path escapes its production directory.')
        raw = path.read_bytes()
        if sha(raw) != asset['sha256']:
            raise CommandError(f'Approved video checksum differs: {path.name}')
        if validate_file(path.name, raw) != ('video', 'video/mp4'):
            raise CommandError('Expected a valid protected MP4.')
        validate_metadata(lesson, 'video', asset['metadata'])
        if asset['metadata']['after_section'] != lesson.learning_content.source_sections[[2, 4, 6][index]]:
            raise CommandError('Expected exact sections 3/5/7.')
        assets.append((path, raw, asset['metadata']))
    return assets


def database_health():
    if connection.vendor != 'sqlite':
        raise CommandError('This reviewed backup workflow requires SQLite.')
    with connection.cursor() as cursor:
        cursor.execute('PRAGMA integrity_check')
        if cursor.fetchall() != [('ok',)]:
            raise CommandError('Live SQLite integrity failed.')
        cursor.execute('PRAGMA foreign_key_check')
        if cursor.fetchall():
            raise CommandError('Live SQLite foreign-key check failed.')


def verified_backup(directory, lesson, assets, *, prefix='lesson113-phase5i'):
    database_health()
    database = Path(connection.settings_dict['NAME']).resolve()
    media = Path(settings.MEDIA_ROOT).resolve()
    storage = LessonAttachment._meta.get_field('file').storage
    if Path(storage.location).resolve() != media:
        raise CommandError('Unexpected storage location; stop before writes.')
    media_files = sorted(p for p in media.rglob('*') if p.is_file()) if media.exists() else []
    if media.exists() and any(p.is_symlink() for p in media.rglob('*')):
        raise CommandError('Symlink in protected media; manual backup review required.')
    required = database.stat().st_size + sum(p.stat().st_size for p in media_files) + sum(len(raw) for _, raw, _ in assets) * 2 + 64*1024**2
    directory = directory.resolve()
    directory.mkdir(parents=True, exist_ok=True)
    if min(shutil.disk_usage(directory).free, shutil.disk_usage(media.parent).free) < required:
        raise CommandError('Insufficient backup/media disk space.')
    folder = directory / (prefix + '-' + timezone.localtime().strftime('%Y%m%d-%H%M%S') + '-' + uuid4().hex[:8])
    folder.mkdir(mode=0o700)
    backup = create_backup(database, folder)
    inventory = {}
    archive = folder / 'protected-media-and-approved-sources.tar'
    with tarfile.open(archive, 'x') as tar:
        archive.chmod(0o600)
        for path in media_files:
            name = 'protected-media/' + str(path.relative_to(media))
            inventory[name] = sha(path.read_bytes()); tar.add(path, arcname=name, recursive=False)
        for path, raw, _ in assets:
            name = 'approved-sources/' + path.name
            inventory[name] = sha(raw); tar.add(path, arcname=name, recursive=False)
    with tarfile.open(archive, 'r') as tar:
        if set(tar.getnames()) != set(inventory):
            raise CommandError('Media backup inventory differs.')
        for name, digest in inventory.items():
            with tar.extractfile(name) as stream:
                if sha(stream.read()) != digest:
                    raise CommandError('Media backup checksum mismatch.')
    snapshot = {'lesson': {'id': lesson.pk, 'title': lesson.title, 'module_id': lesson.module_id,
                           'order': lesson.order, 'text_content': lesson.text_content},
                'learning_content': {'id': lesson.learning_content.pk, **{key: getattr(lesson.learning_content, key) for key in ('objectives', 'source_sections', 'interactions', 'content_language')}},
                'attachments': list(lesson.attachments.values()), 'media_sha256': inventory,
                'sqlite_backup': str(backup), 'verified_integrity_and_foreign_keys': True}
    with (folder / 'before-state.json').open('x') as stream:
        (folder / 'before-state.json').chmod(0o600)
        json.dump(snapshot, stream, ensure_ascii=False, indent=2, default=str)
    return folder


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
    help = 'Integrate the three approved Quality V2 videos and exact ten edits into existing Lesson 113 only.'

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
                self.stdout.write('KEEP 3; approved text unchanged; no-op, no backup or writes.')
                return
            database_health()
            for path, _, metadata in assets:
                self.stdout.write(f'CREATE video: {path.name} -> {metadata["after_section"]}')
            self.stdout.write('UPDATE Lesson 113 text: exactly ten approved edits; preserve 3 objectives/9 headings.')
            if not options['apply']:
                self.stdout.write('Dry-run: no database/media/backup writes.')
                return
            folder = verified_backup(options['backup_dir'], lesson, assets)
            self.stdout.write(f'Verified SQLite/media/source backup: {folder}')
            ids = integrate(plan, assets)
            self.stdout.write(f'Integrated lesson113; attachment IDs {ids}; course remains unpublished.')
        except (OSError, ValidationError, Course.DoesNotExist, Lesson.DoesNotExist) as exc:
            raise CommandError(f'Integration stopped: {exc}') from exc
