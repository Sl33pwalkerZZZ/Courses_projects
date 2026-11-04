"""Create only reviewed Module 5 text in existing course 10; default is read-only."""
import hashlib
import json
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q

from courses.management.commands.import_media_module import create_backup
from courses.models import Course, Lesson, LessonLearningContent, Module
from studio.permissions import instructor

COURSE_ID = 10
COURSE_SLUG = 'ai-media-content'
COURSE_TITLE = 'ИИ для создания медиаконтента: от идеи до публикации'
MODULE_TITLE = 'Создание и монтаж видео в CapCut Desktop'
PREVIOUS_MODULES = [
    'Основы ИИ в медиапроизводстве',
    'Тексты и сценарии с помощью ИИ',
    'Создание изображений и графики с помощью ИИ',
    'Создание и обработка аудио с помощью ИИ',
]
TITLES = [
    'Подготовка видеопроекта и организация материалов',
    'Монтаж, озвучка и интеллектуальные инструменты',
    'Экспорт, адаптация и подготовка видео к публикации',
]
CONTENT_PATH = Path(__file__).resolve().parents[1] / 'media_module_5.json'
# Pin the prepared Phase 5B artifact. A later editorial revision requires review
# and an intentional checksum update, never silent changes to existing lessons.
SOURCE_SHA256 = '8e1003838194901cd780bd1ef61d0cd25ef2840a6e0845115d301c73734f3670'


def load_content():
    try:
        raw = CONTENT_PATH.read_bytes()
        if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
            raise ValueError('Source checksum changed; review the source before importing.')
        data = json.loads(raw.decode('utf-8'))
        if not isinstance(data, dict) or set(data) != {'module', 'lessons'} or data['module'] != MODULE_TITLE:
            raise ValueError('Unexpected module schema/title.')
        lessons = data['lessons']
        if not isinstance(lessons, list) or len(lessons) != 3 or [item['title'] for item in lessons] != TITLES:
            raise ValueError('Exactly three expected lessons in order are required.')
        for item in lessons:
            if set(item) != {'title', 'text_content', 'objectives', 'source_sections'}:
                raise ValueError('Unexpected lesson fields; assessments/media are not imported here.')
            if not isinstance(item['text_content'], str) or not item['text_content'].strip():
                raise ValueError('Missing lesson body.')
            for field, count, limit in [('objectives', 3, 1000), ('source_sections', 9, 255)]:
                values = item[field]
                if (not isinstance(values, list) or len(values) != count
                        or any(not isinstance(v, str) or not v.strip() or len(v) > limit for v in values)):
                    raise ValueError(f'Expected {count} bounded {field}.')
            paragraphs = item['text_content'].split('\n\n')
            headings = item['source_sections']
            if (len(set(headings)) != len(headings) or paragraphs[0] != headings[0]
                    or any(paragraphs.count(h) != 1 for h in headings)
                    or [paragraphs.index(h) for h in headings] != sorted(paragraphs.index(h) for h in headings)):
                raise ValueError('Headings must be unique ordered paragraphs matching the reader.')
        return data
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise CommandError(f'Invalid Module 5 content: {exc}') from exc


def target_course(*, lock=False):
    courses = Course.objects.select_for_update() if lock else Course.objects.all()
    course = courses.filter(pk=COURSE_ID).first()
    if course is None or course.slug != COURSE_SLUG or course.title != COURSE_TITLE or course.is_published:
        raise CommandError('Expected existing unpublished course ID 10 with exact slug/title. Nothing changed.')
    author = get_user_model().objects.only('id', 'role', 'is_active', 'is_superuser').get(pk=course.author_id)
    if not instructor(author):
        raise CommandError('The existing course author lacks active instructor authority.')
    if getattr(getattr(course, 'studio_settings', None), 'language', None) != 'ru':
        raise CommandError('Expected existing Russian course settings.')
    if course.publication_requests.filter(status='pending').exists():
        raise CommandError('Resolve pending publication review before extending this draft.')
    for order, title in enumerate(PREVIOUS_MODULES, 1):
        modules = course.modules.filter(order=order)
        if modules.count() != 1 or modules.first().title != title:
            raise CommandError(f'Existing Module {order} title/order conflict. Nothing changed.')
        lessons = list(modules.first().lessons.order_by('order', 'pk'))
        if [lesson.order for lesson in lessons] != [1, 2, 3] or any(not lesson.text_content.strip() for lesson in lessons):
            raise CommandError(f'Existing Module {order} curriculum is incomplete. Nothing changed.')
    return course


def valid_image_placements(lesson, interactions):
    """Allow later authored images without treating media as a text conflict."""
    if not isinstance(interactions, list):
        return False
    seen = set()
    image_ids = set(lesson.images.values_list('pk', flat=True))
    for item in interactions:
        if (not isinstance(item, dict) or set(item) != {'type', 'image_id', 'after_section', 'caption'}
                or item['type'] != 'image_placement' or type(item['image_id']) is not int
                or item['image_id'] not in image_ids or item['image_id'] in seen
                or item['after_section'] not in lesson.learning_content.source_sections
                or not isinstance(item['caption'], str) or not item['caption'].strip()
                or len(item['caption']) > 2000):
            return False
        seen.add(item['image_id'])
    return True


def check_existing(course, data):
    matches = course.modules.filter(Q(order=5) | Q(title=MODULE_TITLE))
    if matches.count() > 1:
        raise CommandError('Conflicting Module 5 records; no overwrite permitted.')
    module = matches.first()
    elsewhere = Lesson.objects.filter(module__course=course, title__in=TITLES)
    if module:
        elsewhere = elsewhere.exclude(module=module)
    if elsewhere.exists():
        raise CommandError('Module 5 lesson titles already occur elsewhere; nothing changed.')
    if module is None:
        return False
    if module.title != MODULE_TITLE or module.order != 5:
        raise CommandError('Module 5 title/order conflict; nothing changed.')
    lessons = list(module.lessons.order_by('order', 'pk'))
    if len(lessons) != 3:
        raise CommandError('Existing Module 5 has a conflicting lesson count.')
    for order, (lesson, expected) in enumerate(zip(lessons, data['lessons']), 1):
        content = getattr(lesson, 'learning_content', None)
        if (lesson.order != order or lesson.title != expected['title'] or lesson.text_content != expected['text_content']
                or content is None or content.content_language != 'ru'
                or content.objectives != expected['objectives'] or content.source_sections != expected['source_sections']
                or not valid_image_placements(lesson, content.interactions)
                or lesson.assignments.exists() or hasattr(lesson, 'quiz')):
            raise CommandError('Existing Module 5 content conflicts; no overwrite permitted.')
    # Later protected video/VTT/audio attachments are independent of lesson text.
    # Never create, replace or delete them in this command, including on repeats.
    return True


class Command(BaseCommand):
    help = 'Preview or explicitly import Module 5 text into existing draft course 10 only.'

    def add_arguments(self, parser):
        modes = parser.add_mutually_exclusive_group()
        modes.add_argument('--dry-run', action='store_true')
        modes.add_argument('--apply', action='store_true')
        parser.add_argument('--backup-dir', type=Path, default=Path(settings.BASE_DIR) / '.local-course-backups')

    def handle(self, *args, **options):
        data = load_content()
        course = target_course()
        if check_existing(course, data):
            self.stdout.write('Module 5 already exists unchanged: no-op, no writes or backup.')
            return
        self.stdout.write(json.dumps({
            'mode': 'apply' if options['apply'] else 'dry-run', 'course_id': course.pk,
            'course_slug': course.slug, 'source_sha256': SOURCE_SHA256,
            'module': MODULE_TITLE, 'module_order': 5,
            'lessons': [{'course_lesson': i+12, 'lesson_order': i, 'title': entry['title'],
                         'objectives': len(entry['objectives']), 'sections': len(entry['source_sections']),
                         'body_characters': len(entry['text_content'])}
                        for i, entry in enumerate(data['lessons'], 1)],
            'create': {'courses': 0, 'modules': 1, 'lessons': 3, 'lesson_learning_contents': 3},
            'updates': 0, 'deletes': 0, 'quizzes': 0, 'assignments': 0,
            'images': 0, 'attachments': 0, 'publication_requests': 0, 'published': False,
            'media': {'planned_videos': 9, 'planned_vtt': 9, 'status': 'not_recorded_not_imported'},
        }, ensure_ascii=False))
        if not options['apply']:
            self.stdout.write('Dry-run only: no database, media or backup writes.')
            return
        if settings.DATABASES['default']['ENGINE'] != 'django.db.backends.sqlite3':
            raise CommandError('Verified backup workflow requires SQLite.')
        backup = create_backup(settings.DATABASES['default']['NAME'], options['backup_dir'])
        self.stdout.write(f'Verified SQLite backup: {backup}')
        with transaction.atomic():
            course = target_course(lock=True)
            if check_existing(course, data):
                self.stdout.write('Module 5 already exists unchanged: no-op.')
                return
            module = Module(course=course, title=MODULE_TITLE, order=5)
            module.full_clean()
            module.save()
            for order, entry in enumerate(data['lessons'], 1):
                lesson = Lesson(module=module, title=entry['title'], order=order, text_content=entry['text_content'])
                lesson.full_clean()
                lesson.save()
                content = LessonLearningContent(lesson=lesson, content_language='ru', objectives=entry['objectives'],
                                                source_sections=entry['source_sections'], interactions=[])
                content.full_clean()
                content.save()
        self.stdout.write(f'Created draft Module 5 ({module.pk}) with three text lessons. No existing records or media updated.')
