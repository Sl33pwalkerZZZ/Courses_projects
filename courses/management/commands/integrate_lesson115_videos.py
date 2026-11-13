"""Create-only, source-pinned integration of the three approved Lesson 115 videos."""
import hashlib
import json
import shutil
import sqlite3
import subprocess
import tarfile
from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.utils import timezone

from courses.attachments import attachments_ready, store_attachment, validate_file, validate_metadata
from courses.management.commands.import_media_module import create_backup
from courses.models import Course, Lesson, LessonAttachment, LessonPlaybackGrant

PLAN = Path(__file__).resolve().parents[1] / 'lesson115_final_video_integration.json'
PLAN_SHA256 = '1c2a3e10705a5441bfcf24bc6d82e910c2afb7c1d109f9cdc5955488780b57e1'
KINDS_AND_KEYS = [
    ('video', 'm5-l15-v1-export-check'), ('vtt', 'm5-l15-v1-export-check'),
    ('video', 'm5-l15-v2-vertical-adaptation'), ('vtt', 'm5-l15-v2-vertical-adaptation'),
    ('video', 'm5-l15-v3-final-review'), ('vtt', 'm5-l15-v3-final-review'),
]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def hash_file(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def load_plan():
    raw = PLAN.read_bytes()
    if sha(raw) != PLAN_SHA256:
        raise CommandError('Lesson 115 integration plan checksum differs; stop for review.')
    data = json.loads(raw)
    if [(x.get('kind'), x.get('pair_key')) for x in data.get('assets', [])] != KINDS_AND_KEYS:
        raise CommandError('Plan must contain exactly the approved video/WebVTT sequence.')
    if len(data['assets']) != 6:
        raise CommandError('Expected exactly six Lesson 15 attachments.')
    return data


def target(plan, *, lock=False):
    expected = plan['expected']
    course_qs = Course.objects.select_for_update() if lock else Course.objects
    course = course_qs.get(pk=expected['course']['id'])
    if (course.slug != expected['course']['slug'] or course.title != expected['course']['title']
            or course.is_published is not False
            or list(course.modules.order_by('order').values_list('order', flat=True)) != expected['course']['module_orders']
            or Lesson.objects.filter(module__course=course).count() != expected['course']['total_lessons']):
        raise CommandError('Course identity/state differs from the approved target; nothing changed.')

    lesson = Lesson.objects.select_related('module', 'learning_content').get(pk=expected['lesson']['id'])
    module, learning = lesson.module, lesson.learning_content
    if (module.course_id != course.pk or module.pk != expected['module']['id']
            or module.order != expected['module']['order'] or module.title != expected['module']['title']
            or lesson.order != expected['lesson']['order'] or lesson.title != expected['lesson']['title']
            or sha(lesson.text_content.encode('utf-8')) != expected['lesson']['text_sha256']
            or learning.pk != expected['learning_content']['id']
            or learning.content_language != expected['learning_content']['content_language']
            or learning.objectives != expected['learning_content']['objectives']
            or learning.source_sections != expected['learning_content']['source_sections']
            or learning.interactions != expected['learning_content']['interactions']
            or list(module.lessons.order_by('order').values_list('pk', flat=True)) != expected['course']['lesson_ids_in_module_5']):
        raise CommandError('Lesson 15 text, order, sections or metadata conflict; nothing changed.')
    if learning.source_sections[2] != plan['placement_sections'][0] or learning.source_sections[4] != plan['placement_sections'][1] or learning.source_sections[6] != plan['placement_sections'][2]:
        raise CommandError('Approved placement anchors no longer match sections 3, 5 and 7.')
    if LessonPlaybackGrant.objects.filter(attachment__lesson=lesson).exists():
        raise CommandError('Unexpected existing playback grants for the target lesson.')

    rows = list(lesson.attachments.order_by('order', 'pk'))
    if not rows:
        return lesson, 'BEFORE'
    if len(rows) != 6:
        raise CommandError('Lesson 15 has a partial or unexpected attachment set; nothing changed.')
    for order, (row, asset) in enumerate(zip(rows, plan['assets']), 1):
        if (row.order != order or row.kind != asset['kind'] or row.filename != asset['filename']
                or row.sha256 != asset['sha256'] or row.mime_type != asset['mime_type']
                or any(getattr(row, field) != value for field, value in asset['metadata'].items())):
            raise CommandError('Existing Lesson 15 attachments conflict with the approved plan; nothing changed.')
        if not row.file.storage.exists(row.file.name):
            raise CommandError('An existing Lesson 15 protected file is missing.')
        with row.file.storage.open(row.file.name, 'rb') as stream:
            if sha(stream.read()) != row.sha256:
                raise CommandError('An existing Lesson 15 protected file checksum conflicts.')
    return lesson, 'AFTER'


def vtt_cues(raw):
    text = raw.decode('utf-8-sig').replace('\r\n', '\n')
    blocks = text.strip().split('\n\n')[1:]
    cues = []

    def seconds(stamp):
        hours, minutes, rest = stamp.split(':')
        return int(hours) * 3600 + int(minutes) * 60 + float(rest)

    for block in blocks:
        lines = block.splitlines()
        if '-->' not in lines[0]:
            lines = lines[1:]
        start, end = lines[0].split(' --> ')
        cues.append((seconds(start), seconds(end), ' '.join(lines[1:]).strip()))
    return cues


def validate_final_video(path, asset, raw):
    validate_file(path.name, raw)
    result = subprocess.run([
        'ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path),
    ], capture_output=True, text=True, timeout=30, check=True)
    info = json.loads(result.stdout)
    streams = info['streams']
    videos = [stream for stream in streams if stream['codec_type'] == 'video']
    audios = [stream for stream in streams if stream['codec_type'] == 'audio']
    duration = float(info['format']['duration'])
    if (len(videos) != 1 or len(audios) != 1 or len(streams) != 2
            or videos[0]['codec_name'] != 'h264' or videos[0].get('pix_fmt') != 'yuv420p'
            or (videos[0]['width'], videos[0]['height']) != (1920, 1080)
            or videos[0].get('avg_frame_rate') != '30/1'
            or audios[0]['codec_name'] != 'aac' or audios[0].get('profile') != 'LC'
            or int(audios[0].get('sample_rate', 0)) != 48000 or int(audios[0].get('channels', 0)) != 2
            or int(videos[0].get('nb_frames', 0)) != asset['duration_frames']
            or abs(duration - asset['duration_seconds']) > 0.002):
        raise CommandError(f'Final MP4 profile/duration differs from approved Lesson 15 spec: {path.name}')
    return duration


def prevalidate(plan, lesson):
    project_root = Path(settings.BASE_DIR).resolve()
    approved_root = (project_root / 'video-production/lesson-115-production/out/final-bgm').resolve()
    prepared = []
    durations = {}
    transcripts = {}
    for asset in plan['assets']:
        path = (project_root / asset['path']).resolve()
        if not path.is_relative_to(approved_root) or path.name != asset['filename'] or not path.is_file():
            raise CommandError(f'Approved media path missing or outside final-bgm directory: {asset["filename"]}')
        raw = path.read_bytes()
        if sha(raw) != asset['sha256']:
            raise CommandError(f'Approved media checksum differs: {asset["filename"]}')
        if validate_file(path.name, raw) != (asset['kind'], asset['mime_type']):
            raise CommandError(f'Attachment type/signature mismatch: {asset["filename"]}')
        validate_metadata(lesson, asset['kind'], asset['metadata'])
        if asset['metadata']['after_section'] != asset['after_section']:
            raise CommandError('Placement metadata conflicts with its plan.')
        if asset['kind'] == 'video':
            duration = validate_final_video(path, asset, raw)
            durations[asset['key']] = duration
            transcripts[asset['key']] = asset['metadata']['transcript']
        else:
            cues = vtt_cues(raw)
            if not cues or any(end <= start for start, end, _ in cues):
                raise CommandError(f'Invalid empty WebVTT cue set: {asset["filename"]}')
            video_key = asset['pair_key']
            if video_key not in durations:
                raise CommandError('A WebVTT must follow its matching video in the approved sequence.')
            if any(index and start < cues[index - 1][1] for index, (start, _, _) in enumerate(cues)):
                raise CommandError(f'Overlapping WebVTT cues: {asset["filename"]}')
            if max(end for _, end, _ in cues) > durations[video_key] + 0.001:
                raise CommandError(f'WebVTT cue exceeds paired MP4 duration: {asset["filename"]}')
            spoken = ' '.join(text for _, _, text in cues)
            if spoken != transcripts.get(video_key) or asset['after_section'] != next(
                    video_asset['after_section'] for video_asset in plan['assets']
                    if video_asset['key'] == video_key and video_asset['kind'] == 'video'):
                raise CommandError(f'WebVTT text/placement does not match paired video: {asset["filename"]}')
        prepared.append((path, raw, asset))
    for anchor in plan['placement_sections']:
        pair = [a for a in plan['assets'] if a['after_section'] == anchor]
        if [a['kind'] for a in pair] != ['video', 'vtt']:
            raise CommandError(f'Expected exactly one video and one WebVTT after {anchor}.')
    if len(prepared) != 6:
        raise CommandError('Exactly six attachments must be prepared.')
    return prepared


def database_health():
    if connection.vendor != 'sqlite':
        raise CommandError('Lesson 115 verified backup workflow requires SQLite.')
    if not attachments_ready():
        raise CommandError('Protected LessonAttachment schema is unavailable; no writes permitted.')
    with connection.cursor() as cursor:
        cursor.execute('PRAGMA integrity_check')
        if cursor.fetchall() != [('ok',)]:
            raise CommandError('Live SQLite integrity check failed.')
        cursor.execute('PRAGMA foreign_key_check')
        if cursor.fetchall():
            raise CommandError('Live SQLite foreign-key check failed.')


def verified_backup(directory, lesson, plan, prepared):
    database_health()
    database = Path(connection.settings_dict['NAME']).resolve()
    media_root = Path(settings.MEDIA_ROOT).resolve()
    storage = LessonAttachment._meta.get_field('file').storage
    if Path(storage.location).resolve() != media_root:
        raise CommandError('Protected attachment storage path is not the configured MEDIA_ROOT.')
    media_files = sorted(p for p in media_root.rglob('*') if p.is_file()) if media_root.exists() else []
    if any(p.is_symlink() for p in media_root.rglob('*')):
        raise CommandError('Protected media contains a symlink; manual backup review required.')

    root = Path(settings.BASE_DIR).resolve()
    source_paths = [root / item for item in plan['backup_source_paths']]
    if any(not p.is_file() for p in source_paths):
        raise CommandError('A relevant manifest/source document for the backup is missing.')
    attachment_bytes = sum(len(raw) for _, raw, _ in prepared)
    required_bytes = (database.stat().st_size + sum(p.stat().st_size for p in media_files)
                      + attachment_bytes + sum(p.stat().st_size for p in source_paths) + 64 * 1024**2)
    directory = Path(directory).resolve()
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    if min(shutil.disk_usage(directory).free, shutil.disk_usage(media_root.parent).free) < required_bytes:
        raise CommandError('Insufficient disk space to back up SQLite, protected media and lesson assets.')
    folder = directory / ('lesson115-final-integration-' + timezone.localtime().strftime('%Y%m%d-%H%M%S') + '-' + uuid4().hex[:8])
    folder.mkdir(mode=0o700, exist_ok=False)
    database_backup = create_backup(database, folder)

    inventory = {}
    media_archive = folder / 'protected-media.tar'
    with tarfile.open(media_archive, 'x') as archive:
        media_archive.chmod(0o600)
        for path in media_files:
            name = 'protected-media/' + path.relative_to(media_root).as_posix()
            inventory[name] = hash_file(path)
            archive.add(path, arcname=name, recursive=False)
    input_archive = folder / 'lesson115-inputs.tar'
    with tarfile.open(input_archive, 'x') as archive:
        input_archive.chmod(0o600)
        for path in source_paths:
            name = 'source/' + path.relative_to(root).as_posix()
            inventory[name] = hash_file(path)
            archive.add(path, arcname=name, recursive=False)
        for path, raw, _ in prepared:
            name = 'approved-final-media/' + path.name
            inventory[name] = sha(raw)
            archive.add(path, arcname=name, recursive=False)
    for archive_path, expected_prefix in ((media_archive, 'protected-media/'), (input_archive, None)):
        with tarfile.open(archive_path, 'r') as archive:
            names = archive.getnames()
            expected = {name for name in inventory if name.startswith(expected_prefix)} if expected_prefix else {
                name for name in inventory if name.startswith('source/') or name.startswith('approved-final-media/')}
            if set(names) != expected:
                raise CommandError(f'Backup archive inventory mismatch: {archive_path.name}')
            for name in names:
                with archive.extractfile(name) as stream:
                    if sha(stream.read()) != inventory[name]:
                        raise CommandError(f'Backup archive checksum mismatch: {name}')
    with sqlite3.connect(database_backup.as_uri() + '?mode=ro', uri=True) as db:
        if db.execute('PRAGMA integrity_check').fetchall() != [('ok',)] or db.execute('PRAGMA foreign_key_check').fetchall():
            raise CommandError('Fresh SQLite backup integrity/foreign-key verification failed.')
        course_row = db.execute('SELECT slug, is_published FROM courses_course WHERE id=10').fetchone()
        lesson_row = db.execute('SELECT title, text_content FROM courses_lesson WHERE id=115').fetchone()
        if course_row != ('ai-media-content', 0) or not lesson_row or sha(lesson_row[1].encode()) != plan['expected']['lesson']['text_sha256']:
            raise CommandError('SQLite backup does not contain the expected unpublished Course 10/Lesson 15 state.')

    snapshot = {
        'scope': plan['scope'],
        'course': {'id': 10, 'slug': 'ai-media-content', 'is_published': False},
        'module': {'id': lesson.module_id, 'order': lesson.module.order, 'title': lesson.module.title},
        'lesson': {'id': lesson.pk, 'title': lesson.title, 'order': lesson.order,
                   'text_content': lesson.text_content,
                   'learning_content': {'id': lesson.learning_content.pk,
                       'content_language': lesson.learning_content.content_language,
                       'objectives': lesson.learning_content.objectives,
                       'source_sections': lesson.learning_content.source_sections,
                       'interactions': lesson.learning_content.interactions},
                   'attachments': list(lesson.attachments.values(
                       'id', 'kind', 'filename', 'mime_type', 'sha256', 'label', 'caption', 'transcript',
                       'provenance', 'after_section', 'order', 'file'))},
        'live_sqlite_integrity_and_foreign_keys': 'PASS',
        'sqlite_backup_integrity_and_foreign_keys': 'PASS',
        'sqlite_backup': database_backup.name,
        'archives': {'protected_media': media_archive.name, 'lesson115_inputs': input_archive.name},
        'sha256': {database_backup.name: hash_file(database_backup), media_archive.name: hash_file(media_archive),
                   input_archive.name: hash_file(input_archive), **inventory},
    }
    snapshot_path = folder / 'before-state.json'
    with snapshot_path.open('x', encoding='utf-8') as stream:
        snapshot_path.chmod(0o600)
        json.dump(snapshot, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    return folder


def apply_plan(plan, prepared):
    created_files = []
    try:
        with transaction.atomic():
            lesson, state = target(plan, lock=True)
            if state == 'AFTER':
                return list(lesson.attachments.order_by('order').values_list('pk', flat=True))
            ids = []
            for path, raw, asset in prepared:
                row, created = store_attachment(lesson, asset['filename'], raw, asset['metadata'], created_files)
                if not created:
                    raise CommandError('Unexpected pre-existing attachment encountered during create-only apply.')
                ids.append(row.pk)
            result, state = target(plan)
            if state != 'AFTER' or result.text_content != lesson.text_content:
                raise CommandError('Post-integration Lesson 15 verification failed.')
            return ids
    except Exception:
        for file_storage, name in reversed(created_files):
            try:
                file_storage.delete(name)
            except Exception:
                pass
        raise


class Command(BaseCommand):
    help = 'Back up, preview, or attach exactly three approved video/WebVTT pairs to existing Course 10 Lesson 15.'

    def add_arguments(self, parser):
        modes = parser.add_mutually_exclusive_group()
        modes.add_argument('--backup-only', action='store_true')
        modes.add_argument('--dry-run', action='store_true')
        modes.add_argument('--apply', action='store_true')
        parser.add_argument('--backup-dir', type=Path, default=Path(settings.BASE_DIR) / '.local-course-backups')

    def handle(self, *args, **options):
        try:
            plan = load_plan()
            lesson, state = target(plan)
            if state == 'AFTER':
                self.stdout.write('KEEP 6 (3 MP4 + 3 WebVTT); exact Lesson 15 state verified; no changes.')
                return
            prepared = prevalidate(plan, lesson)
            database_health()
            for path, _, asset in prepared:
                self.stdout.write(f"CREATE {asset['kind']}: {path.name} -> {asset['after_section']}")
            self.stdout.write('SCOPE: Course 10 / Module 5 / Lesson 15 only; lesson text and nine anchors unchanged.')
            if options['backup_only']:
                folder = verified_backup(options['backup_dir'], lesson, plan, prepared)
                self.stdout.write(f'Verified preflight backup: {folder}')
                return
            if not options['apply']:
                self.stdout.write('Dry-run: six creates only; no database or protected-media writes.')
                return
            folder = verified_backup(options['backup_dir'], lesson, plan, prepared)
            self.stdout.write(f'Verified immediate pre-write backup: {folder}')
            ids = apply_plan(plan, prepared)
            self.stdout.write(f'Integrated exactly six Lesson 15 attachments in order; IDs: {ids}. Course remains unpublished.')
        except (OSError, ValidationError, Course.DoesNotExist, Lesson.DoesNotExist, subprocess.SubprocessError, ValueError, KeyError, TypeError) as exc:
            raise CommandError(f'Lesson 15 video integration stopped safely: {exc}') from exc
