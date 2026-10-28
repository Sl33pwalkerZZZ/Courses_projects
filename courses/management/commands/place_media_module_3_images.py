"""Associate existing private images with section anchors; never edit theory."""
import json
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from courses.management.commands.import_media_module import create_backup
from courses.models import Course
from studio.serializers import LessonWriteSerializer


def placement_plan(manifest, *, lock=False):
    try:
        data = json.loads(Path(manifest).read_text(encoding='utf-8'))
        if data['course_slug'] != 'ai-media-content' or data['module_order'] != 3 or len(data['assets']) != 6:
            raise ValueError('Expected six Module 3 manifest entries.')
        courses = Course.objects.select_for_update() if lock else Course.objects.all()
        course = courses.get(slug=data['course_slug'])
        if course.is_published or course.publication_requests.filter(status='pending').exists():
            raise ValueError('Course must remain a draft without pending publication.')
        module = course.modules.get(order=3, title='Создание изображений и графики с помощью ИИ')
        lessons = list(module.lessons.order_by('order', 'pk'))
        if [lesson.order for lesson in lessons] != [1, 2, 3]:
            raise ValueError('Expected three existing ordered lessons.')
        result, seen = [], set()
        for lesson in lessons:
            entries = [a for a in data['assets'] if a['lesson_order'] == lesson.order]
            if len(entries) != 2:
                raise ValueError('Exactly two placements per lesson required.')
            learning = lesson.learning_content
            placements = []
            for entry in entries:
                filename = entry['filename']
                if (not isinstance(filename, str) or Path(filename).name != filename or '\\' in filename
                        or filename in seen or entry['lesson_title'] != lesson.title):
                    raise ValueError('Conflicting filename or lesson association.')
                seen.add(filename)
                image = lesson.images.get(image__endswith='/' + filename)
                if not image.image.storage.exists(image.image.name):
                    raise ValueError('Registered image file is missing.')
                placements.append({'type': 'image_placement', 'image_id': image.pk,
                    'after_section': entry['placement']['after_section'], 'caption': entry['caption_ru']})
            existing = [i for i in learning.interactions if i.get('type') == 'image_placement']
            if existing and existing != placements:
                raise ValueError('Existing placements conflict; no overwrite permitted.')
            updated = [i for i in learning.interactions if i.get('type') != 'image_placement'] + placements
            serializer = LessonWriteSerializer(instance=lesson,
                data={'learning_content': {'interactions': updated}}, partial=True)
            if not serializer.is_valid():
                raise ValueError(str(serializer.errors))
            result.append((lesson, learning, updated, existing == placements))
        return result
    except (OSError, ValueError, TypeError, KeyError, AttributeError, ObjectDoesNotExist, MultipleObjectsReturned) as exc:
        raise CommandError(f'Cannot associate placements: {exc}') from exc


class Command(BaseCommand):
    help = 'Preview or associate six existing Module 3 images with section anchors.'

    def add_arguments(self, parser):
        mode = parser.add_mutually_exclusive_group()
        mode.add_argument('--dry-run', action='store_true')
        mode.add_argument('--apply', action='store_true')
        parser.add_argument('--manifest', type=Path, default=Path(settings.BASE_DIR) / 'docs/courses/media-module-3-assets.json')
        parser.add_argument('--backup-dir', type=Path, default=Path(settings.BASE_DIR) / '.local-course-backups')

    def handle(self, *args, **options):
        plan = placement_plan(options['manifest'])
        self.stdout.write(json.dumps({'mode': 'apply' if options['apply'] else 'dry-run',
            'learning_content_updates': sum(not same for _, _, _, same in plan),
            'placements': [{'lesson_id': lesson.pk, 'lesson_title': lesson.title,
                'images': [i for i in updated if i['type'] == 'image_placement']}
                for lesson, _, updated, _ in plan], 'theory_updates': 0, 'new_images': 0}, ensure_ascii=False))
        if not options['apply'] or all(same for _, _, _, same in plan):
            self.stdout.write('No writes (dry-run or unchanged no-op).')
            return
        if settings.DATABASES['default']['ENGINE'] != 'django.db.backends.sqlite3':
            raise CommandError('Verified backup workflow requires SQLite.')
        backup = create_backup(settings.DATABASES['default']['NAME'], options['backup_dir'])
        self.stdout.write(f'Verified backup: {backup}')
        with transaction.atomic():
            for _, learning, updated, same in placement_plan(options['manifest'], lock=True):
                if not same:
                    learning.interactions = updated
                    learning.save(update_fields=['interactions'])
        self.stdout.write('Associated placements only. Theory, files and publication state unchanged.')
