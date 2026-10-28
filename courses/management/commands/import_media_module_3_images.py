"""Attach six validated local PNGs using existing private lesson storage."""
import hashlib
import json
import warnings
from io import BytesIO
from pathlib import Path

from PIL import Image, PngImagePlugin, UnidentifiedImageError
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from courses.management.commands.import_media_module import create_backup
from courses.models import Course, LessonImage
from studio.models import LessonImageDescription

SLUG = 'ai-media-content'
MODULE_TITLE = 'Создание изображений и графики с помощью ИИ'
MAX_BYTES = 5 * 1024 * 1024
PREFIX = f'lessons/{SLUG}/module-3/'


def prepare_assets(manifest, directory):
    try:
        data = json.loads(Path(manifest).read_text(encoding='utf-8'))
        if data['course_slug'] != SLUG or data['module_order'] != 3 or len(data['assets']) != 6:
            raise ValueError('Expected six Module 3 assets.')
        assets, seen = [], set()
        root = Path(directory).resolve()
        for entry in data['assets']:
            filename = entry['filename']
            if (not isinstance(filename, str) or Path(filename).name != filename or '/' in filename
                    or '\\' in filename or not filename.endswith('.png') or filename in seen):
                raise ValueError('Unsafe or duplicate filename.')
            seen.add(filename)
            order = entry['lesson_order']
            if type(order) is not int or order not in (1, 2, 3) or entry.get('decorative') is not False:
                raise ValueError('Expected informative images for lesson orders 1–3.')
            alt = entry['alt_text']
            if (not isinstance(alt, dict) or not alt.get('ru', '').strip() or set(alt) - {'ru', 'kk', 'en'}
                    or any(not isinstance(v, str) or not v.strip() or len(v) > 1000 for v in alt.values())):
                raise ValueError('Invalid informative alternative text.')
            if not isinstance(entry['caption_ru'], str) or not entry['caption_ru'].strip():
                raise ValueError('Missing caption.')
            source = (root / filename).resolve()
            if not source.is_relative_to(root) or not source.is_file() or not 0 < source.stat().st_size <= MAX_BYTES:
                raise ValueError(f'Missing, unsafe or oversized PNG: {filename}')
            raw = source.read_bytes()
            if len(raw) > MAX_BYTES:
                raise ValueError('Image exceeds size limit.')
            with warnings.catch_warnings():
                warnings.simplefilter('error', Image.DecompressionBombWarning)
                with Image.open(BytesIO(raw)) as image:
                    if image.format != 'PNG' or image.width * image.height > 16000000 or getattr(image, 'n_frames', 1) != 1:
                        raise ValueError('Expected a single-frame PNG up to 16 million pixels.')
                    image.verify()
                with Image.open(BytesIO(raw)) as image:
                    image.load()
                    clean = BytesIO()
                    metadata = PngImagePlugin.PngInfo()
                    # Caption has no model/figure field. Retain the authored value
                    # in the private file, not as lesson prose or alternative text.
                    metadata.add_itxt('Description', entry['caption_ru'])
                    image.convert('RGB').save(clean, format='PNG', pnginfo=metadata)
                    dimensions = image.size
            payload = clean.getvalue()
            if len(payload) > MAX_BYTES:
                raise ValueError('Sanitized PNG exceeds size limit.')
            assets.append({**entry, 'alt_text': dict(alt), 'payload': payload,
                           'dimensions': dimensions, 'storage_name': PREFIX + filename})
        if [sum(a['lesson_order'] == i for a in assets) for i in (1, 2, 3)] != [2, 2, 2]:
            raise ValueError('Exactly two images per lesson are required.')
        return assets
    except (OSError, ValueError, KeyError, TypeError, AttributeError, UnidentifiedImageError,
            Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise CommandError(f'Invalid assets/manifest: {exc}') from exc


def plan(assets, *, lock=False):
    courses = Course.objects.select_for_update() if lock else Course.objects.all()
    course = courses.get(slug=SLUG)
    if course.is_published or course.publication_requests.filter(status='pending').exists():
        raise CommandError('Only an unpublished draft without pending publication may be changed.')
    modules = course.modules.filter(order=3)
    if modules.count() != 1 or modules.get().title != MODULE_TITLE:
        raise CommandError('Expected exactly one existing Module 3.')
    lessons = list(modules.get().lessons.order_by('order', 'pk'))
    if [l.order for l in lessons] != [1, 2, 3]:
        raise CommandError('Expected three existing lessons ordered 1–3.')
    storage = LessonImage._meta.get_field('image').storage
    result = []
    for lesson in lessons:
        group = [a for a in assets if a['lesson_order'] == lesson.order]
        if any(a['lesson_title'] != lesson.title for a in group):
            raise CommandError('Manifest lesson title does not match the stored lesson.')
        existing = list(lesson.images.order_by('order', 'pk'))
        names = {a['storage_name'] for a in group}
        if any(row.image.name not in names for row in existing) or len(existing) > 2:
            raise CommandError('Existing lesson images conflict; nothing overwritten.')
        for order, asset in enumerate(group, 1):
            matches = list(LessonImage.objects.filter(image=asset['storage_name']))
            if len(matches) > 1 or any(row.lesson_id != lesson.pk for row in matches):
                raise CommandError('Storage path is already attached elsewhere or duplicated.')
            row = matches[0] if matches else None
            if row:
                description = getattr(row, 'studio_description', None)
                if (row.order != order or description is None or description.decorative
                        or description.alt_text != asset['alt_text'] or not storage.exists(asset['storage_name'])):
                    raise CommandError('Existing attachment metadata/file conflicts.')
                with storage.open(asset['storage_name'], 'rb') as stored:
                    actual = hashlib.sha256(stored.read()).digest()
                if actual != hashlib.sha256(asset['payload']).digest():
                    raise CommandError('Existing attachment bytes conflict.')
            elif storage.exists(asset['storage_name']):
                raise CommandError('Unregistered destination file exists; refusing overwrite.')
            result.append((lesson, order, asset, row is not None))
    return result


class Command(BaseCommand):
    help = 'Preview or safely attach existing Module 3 PNG assets (private gallery).'

    def add_arguments(self, parser):
        mode = parser.add_mutually_exclusive_group()
        mode.add_argument('--dry-run', action='store_true')
        mode.add_argument('--apply', action='store_true')
        parser.add_argument('--assets-dir', type=Path, default=Path(settings.BASE_DIR) / 'course_assets/module_3')
        parser.add_argument('--manifest', type=Path, default=Path(settings.BASE_DIR) / 'docs/courses/media-module-3-assets.json')
        parser.add_argument('--backup-dir', type=Path, default=Path(settings.BASE_DIR) / '.local-course-backups')

    def handle(self, *args, **options):
        assets = prepare_assets(options['manifest'], options['assets_dir'])
        try:
            proposed = plan(assets)
        except Course.DoesNotExist as exc:
            raise CommandError('Existing ai-media-content course not found.') from exc
        self.stdout.write(json.dumps({'mode': 'apply' if options['apply'] else 'dry-run',
            'create': sum(not exists for _, _, _, exists in proposed),
            'unchanged': sum(exists for _, _, _, exists in proposed),
            'captions': 'PNG Description metadata; no visible figure caption field',
            'images': [{'lesson_id': lesson.pk, 'lesson_title': lesson.title, 'gallery_order': order,
                        'filename': asset['filename'], 'dimensions': asset['dimensions'],
                        'caption_ru': asset['caption_ru'], 'alt_text': asset['alt_text']}
                       for lesson, order, asset, _ in proposed]}, ensure_ascii=False))
        if not options['apply'] or all(exists for _, _, _, exists in proposed):
            self.stdout.write('No writes (dry-run or unchanged no-op).')
            return
        if settings.DATABASES['default']['ENGINE'] != 'django.db.backends.sqlite3':
            raise CommandError('Verified backup workflow requires SQLite.')
        backup = create_backup(settings.DATABASES['default']['NAME'], options['backup_dir'])
        self.stdout.write(f'Verified backup: {backup}')
        storage = LessonImage._meta.get_field('image').storage
        created_files = []
        try:
            with transaction.atomic():
                for lesson, order, asset, exists in plan(assets, lock=True):
                    if exists:
                        continue
                    name = storage.save(asset['storage_name'], ContentFile(asset['payload']))
                    created_files.append(name)
                    if name != asset['storage_name']:
                        raise CommandError('Storage filename changed; refusing collision.')
                    row = LessonImage.objects.create(lesson=lesson, order=order, image=name)
                    LessonImageDescription.objects.create(image=row, decorative=False, alt_text=asset['alt_text'])
        except Exception:
            # Storage is outside the DB transaction. Remove only files saved by
            # this attempt; never delete pre-existing images or source PNGs.
            for name in created_files:
                storage.delete(name)
            raise
        self.stdout.write('Module 3 protected gallery attachments created. Source files and lesson text unchanged.')
