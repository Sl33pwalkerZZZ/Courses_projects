"""Create only Module 3 in the existing draft media course; preview by default."""
import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q

from courses.management.commands.import_media_module import create_backup
from courses.models import Course, Lesson, LessonLearningContent, Module

COURSE_ID = 10
COURSE_SLUG = 'ai-media-content'
MODULE_TITLE = 'Создание изображений и графики с помощью ИИ'
TITLES = [
    'Генерация изображений с помощью ИИ',
    'Создание обложек, карточек и инфографики',
    'Единый визуальный стиль медиапроекта',
]
CONTENT_PATH = Path(__file__).resolve().parents[1] / 'media_module_3.json'


def load_content():
    try:
        data = json.loads(CONTENT_PATH.read_text(encoding='utf-8'))
        if set(data) != {'module', 'lessons'} or data['module'] != MODULE_TITLE:
            raise ValueError('Unexpected module content.')
        lessons = data['lessons']
        if [item['title'] for item in lessons] != TITLES:
            raise ValueError('Exactly three expected lessons are required.')
        for item in lessons:
            if set(item) != {'title', 'text_content', 'objectives', 'source_sections'}:
                raise ValueError('Unexpected lesson fields.')
            if not isinstance(item['text_content'], str) or not item['text_content'].strip():
                raise ValueError('Missing lesson body.')
            for field in ('objectives', 'source_sections'):
                values = item[field]
                if not isinstance(values, list) or not values or any(not isinstance(v, str) or not v.strip() for v in values):
                    raise ValueError(f'Invalid {field}.')
            if len(item['objectives']) != 3:
                raise ValueError('Exactly three objectives are required.')
            paragraphs = item['text_content'].split('\n\n')
            headings = item['source_sections']
            if (len(set(headings)) != len(headings) or paragraphs[0] != headings[0]
                    or any(paragraphs.count(heading) != 1 for heading in headings)
                    or [paragraphs.index(h) for h in headings] != sorted(paragraphs.index(h) for h in headings)):
                raise ValueError('Headings must match the renderer metadata contract.')
        return data
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise CommandError(f'Invalid Module 3 content: {exc}') from exc


def target_course(*, lock=False):
    courses = Course.objects.select_for_update() if lock else Course.objects.all()
    course = courses.filter(pk=COURSE_ID, slug=COURSE_SLUG).first()
    if course is None or course.is_published:
        raise CommandError('Expected existing unpublished course 10 / ai-media-content. Nothing changed.')
    if getattr(getattr(course, 'studio_settings', None), 'language', None) != 'ru':
        raise CommandError('Expected existing Russian course settings.')
    if not course.modules.filter(order=1, title='Основы ИИ в медиапроизводстве').exists():
        raise CommandError('Existing Module 1 is required; it will not be recreated.')
    if not course.modules.filter(order=2, title='Тексты и сценарии с помощью ИИ').exists():
        raise CommandError('Existing Module 2 is required; it will not be recreated.')
    if course.publication_requests.filter(status='pending').exists():
        raise CommandError('Resolve the pending publication request before extending this draft.')
    return course


def check_existing(course, data):
    targets = course.modules.filter(Q(order=3) | Q(title=MODULE_TITLE))
    if targets.count() > 1:
        raise CommandError('Conflicting Module 3 records. No overwrite permitted.')
    module = targets.first()
    # Reject the same target lessons misplaced in another module as well.
    elsewhere = Lesson.objects.filter(module__course=course, title__in=TITLES)
    if module:
        elsewhere = elsewhere.exclude(module=module)
    if elsewhere.exists():
        raise CommandError('Target lesson titles already exist elsewhere. Nothing changed.')
    if module is None:
        return False
    if module.title != MODULE_TITLE or module.order != 3:
        raise CommandError('Module 3 title/order conflict. Nothing changed.')
    lessons = list(module.lessons.order_by('order', 'pk'))
    if len(lessons) != 3:
        raise CommandError('Existing Module 3 has a conflicting lesson count.')
    for order, (lesson, expected) in enumerate(zip(lessons, data['lessons']), 1):
        learning = getattr(lesson, 'learning_content', None)
        if (lesson.order != order or lesson.title != expected['title']
                or lesson.text_content != expected['text_content'] or learning is None
                or learning.content_language != 'ru' or learning.interactions != []
                or learning.objectives != expected['objectives']
                or learning.source_sections != expected['source_sections']
                or lesson.images.exists() or lesson.assignments.exists() or hasattr(lesson, 'quiz')):
            raise CommandError('Existing Module 3 content conflicts. No overwrite permitted.')
    return True


class Command(BaseCommand):
    help = 'Preview or explicitly add Module 3 to draft media course 10 (no assessments).'

    def add_arguments(self, parser):
        mode = parser.add_mutually_exclusive_group()
        mode.add_argument('--dry-run', action='store_true')
        mode.add_argument('--apply', action='store_true')
        parser.add_argument('--backup-dir', type=Path, default=Path(settings.BASE_DIR) / '.local-course-backups')

    def handle(self, *args, **options):
        data = load_content()
        course = target_course()
        if check_existing(course, data):
            self.stdout.write('Module 3 already exists unchanged: no-op, no writes or backup.')
            return
        self.stdout.write(json.dumps({
            'mode': 'apply' if options['apply'] else 'dry-run', 'course_id': course.pk,
            'module': MODULE_TITLE, 'module_order': 3,
            'lessons': [{'course_lesson': i + 6, 'module_order': i, 'title': item['title'],
                         'objectives': len(item['objectives']), 'body_characters': len(item['text_content'])}
                        for i, item in enumerate(data['lessons'], 1)],
            'create': {'modules': 1, 'lessons': 3, 'lesson_learning_contents': 3},
            'updates': 0, 'quizzes': 0, 'assignments': 0, 'lesson_images': 0, 'published': False,
            'visual_assets': '6 planned; awaiting creation and approval; not imported',
        }, ensure_ascii=False))
        if not options['apply']:
            self.stdout.write('Dry-run only: no database or backup writes.')
            return
        if settings.DATABASES['default']['ENGINE'] != 'django.db.backends.sqlite3':
            raise CommandError('Verified backup workflow requires SQLite.')
        backup = create_backup(settings.DATABASES['default']['NAME'], options['backup_dir'])
        self.stdout.write(f'Verified SQLite backup: {backup}')
        with transaction.atomic():
            course = target_course(lock=True)
            if check_existing(course, data):
                self.stdout.write('Module 3 already exists unchanged: no-op.')
                return
            module = Module(course=course, title=MODULE_TITLE, order=3)
            module.full_clean()
            module.save()
            for order, item in enumerate(data['lessons'], 1):
                lesson = Lesson(module=module, title=item['title'], order=order, text_content=item['text_content'])
                lesson.full_clean()
                lesson.save()
                learning = LessonLearningContent(lesson=lesson, content_language='ru',
                    source_sections=item['source_sections'], objectives=item['objectives'], interactions=[])
                learning.full_clean()
                learning.save()
        self.stdout.write(f'Created draft Module 3 ({module.pk}) with three lessons. No existing records updated.')
