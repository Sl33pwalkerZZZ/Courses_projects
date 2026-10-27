"""Source-pinned, create-only import. Default preview never writes rows or backups."""
import hashlib
import json
import sqlite3
from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from courses.models import Course, CourseImport, Direction, Lesson, LessonLearningContent, Module
from courses.management.commands.import_first_course import curriculum_snapshot, digest
from courses.management.first_course_document import plain_text
from studio.models import CourseSettings
from studio.permissions import instructor
from studio.word import parse_docx

SOURCE_HASH = '2c263201dabc9975c044761ff762247350e726c616bbae1c03407841f6a69e81'
TITLE = 'ИИ для создания медиаконтента: от идеи до публикации'
SLUG = 'ai-media-content'
MODULE = 'Основы ИИ в медиапроизводстве'
TITLES = [
    'Как генеративный ИИ помогает создавать медиаконтент',
    'Бриф, промпт и выбор ИИ-инструмента',
    'Проверка фактов, права и прозрачность использования ИИ',
]


def source_plan(path):
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_HASH:
        raise CommandError('Source differs from the reviewed DOCX; review the mapping before importing.')
    document = parse_docx(raw, path.name)
    blocks = document['blocks']
    starts = [next(i for i, b in enumerate(blocks) if b.get('text') == f'Урок {n}. {title}')
              for n, title in enumerate(TITLES, 1)]
    lessons = []
    for n, start in enumerate(starts):
        section = blocks[start + 1:starts[n + 1] if n < 2 else len(blocks)]
        if section[0].get('text') != 'Цели урока':
            raise CommandError('Unexpected objectives layout.')
        objectives = [b['text'] for b in section[1:4]]
        body = section[4:]
        # Existing SourceParagraph renders text/links, not Markdown tables.
        # Expand each source row to labelled prose at its original position.
        readable = []
        for block in body:
            if block['type'] == 'table':
                for row in block['rows']:
                    readable.append({'type': 'paragraph', 'text': '; '.join(
                        f'{label}: {cell}' for label, cell in zip(block['headers'], row))})
            else:
                readable.append({**block, 'type': 'paragraph'})
        text = plain_text(readable)
        lessons.append({'title': TITLES[n], 'order': n + 1, 'text_content': text,
                        'objectives': objectives, 'source_sections': [b['text'] for b in body if b['type'] == 'heading']})
    return {'description': '\n\n'.join(b['text'] for b in blocks[:starts[0]]
                                      if b.get('text', '').startswith(('Результат модуля:', 'Ориентир по времени:'))),
            'lessons': lessons}


def create_backup(database, directory):
    """SQLite online backup from a read-only source, never overwrite a destination."""
    database = Path(database).resolve()
    if not database.is_file():
        raise CommandError('A file-backed SQLite database is required.')
    directory = Path(directory).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f'media-module-before-{uuid4().hex}.sqlite3'
    target.touch(mode=0o600, exist_ok=False)
    try:
        with sqlite3.connect(database.as_uri() + '?mode=ro', uri=True) as source:
            with sqlite3.connect(target) as backup:
                source.backup(backup)
                if backup.execute('PRAGMA integrity_check').fetchall() != [('ok',)]:
                    raise CommandError('Backup integrity check failed.')
                if backup.execute('PRAGMA foreign_key_check').fetchall():
                    raise CommandError('Backup contains foreign-key violations.')
                if not backup.execute("SELECT 1 FROM sqlite_master WHERE name='courses_course'").fetchone():
                    raise CommandError('Backup does not contain the course database.')
    except sqlite3.Error as exc:
        raise CommandError('SQLite backup failed; import stopped.') from exc
    return target


class Command(BaseCommand):
    help = 'Preview or create the reviewed Russian media module as an unpublished draft.'

    def add_arguments(self, parser):
        mode = parser.add_mutually_exclusive_group()
        mode.add_argument('--dry-run', action='store_true')
        mode.add_argument('--apply', action='store_true')
        parser.add_argument('--author-username', required=True)
        parser.add_argument('--direction-slug', default='ai-foundations')
        parser.add_argument('--source', type=Path, default=Path(settings.BASE_DIR) / 'course_sources/media_module_1.docx')
        parser.add_argument('--backup-dir', type=Path, default=Path(settings.BASE_DIR) / '.local-course-backups')

    def existing(self, plan, author, direction):
        matches = Course.objects.filter(slug=SLUG) | Course.objects.filter(title=TITLE)
        if not matches.exists():
            return False
        if matches.count() != 1:
            raise CommandError('Conflicting target courses; no changes permitted.')
        course = matches.get()
        receipt = getattr(course, 'content_import', None)
        language = getattr(getattr(course, 'studio_settings', None), 'language', None)
        if (not receipt or receipt.source_sha256 != SOURCE_HASH or receipt.manifest_sha256 != digest(plan)
                or course.slug != SLUG or course.author_id != author.pk or course.direction_id != direction.pk
                or language != 'ru' or digest(curriculum_snapshot(course)) != receipt.content_sha256):
            raise CommandError('Existing course/content conflicts with this import; nothing overwritten.')
        self.stdout.write('Already imported and unchanged: no-op.')
        return True

    def handle(self, *args, **options):
        try:
            plan = source_plan(options['source'])
        except (OSError, ValueError, StopIteration, KeyError) as exc:
            raise CommandError('Unable to map the reviewed source document.') from exc
        author = get_user_model().objects.filter(username=options['author_username']).first()
        if author is None or not instructor(author):
            raise CommandError('Select an existing active authorized instructor or administrator.')
        direction = Direction.objects.filter(slug=options['direction_slug']).first()
        if direction is None:
            raise CommandError('Select an existing category; categories are never created.')
        if self.existing(plan, author, direction):
            return
        self.stdout.write(json.dumps({'mode': 'apply' if options['apply'] else 'dry-run',
            'course': TITLE, 'slug': SLUG, 'author_id': author.pk, 'category': direction.slug,
            'language': 'ru', 'level': 'beginner', 'enrollment_mode': 'open', 'published': False,
            'module': MODULE, 'lessons': [{'title': l['title'], 'order': l['order'],
                'body_characters': len(l['text_content']), 'objectives': len(l['objectives'])} for l in plan['lessons']],
            'create': {'courses': 1, 'modules': 1, 'lessons': 3, 'learning_contents': 3,
                       'course_settings': 1, 'course_imports': 1}, 'updates': 0}, ensure_ascii=False))
        if not options['apply']:
            self.stdout.write('Dry-run: no database or backup writes. No quizzes or assignment records created.')
            return
        if settings.DATABASES['default']['ENGINE'] != 'django.db.backends.sqlite3':
            raise CommandError('This backup workflow supports SQLite only.')
        backup = create_backup(settings.DATABASES['default']['NAME'], options['backup_dir'])
        self.stdout.write(f'Verified backup: {backup}')
        with transaction.atomic():
            author.refresh_from_db()
            if not instructor(author):
                raise CommandError('Author is no longer authorized.')
            if self.existing(plan, author, direction):
                return
            course = Course.objects.create(title=TITLE, slug=SLUG, description=plan['description'],
                author=author, direction=direction, level='beginner', enrollment_mode='open', is_published=False)
            CourseSettings.objects.create(course=course, language='ru')
            module = Module.objects.create(course=course, title=MODULE, order=1)
            for item in plan['lessons']:
                lesson = Lesson.objects.create(module=module, **{k: item[k] for k in ('title', 'order', 'text_content')})
                LessonLearningContent.objects.create(lesson=lesson, content_language='ru',
                    objectives=item['objectives'], source_sections=item['source_sections'], interactions=[])
            CourseImport.objects.create(course=course, source_name='media_module_1.docx', source_sha256=SOURCE_HASH,
                manifest_sha256=digest(plan), content_sha256=digest(curriculum_snapshot(course)),
                version='media-module-1-v1', content_language='ru', review_approved=False)
        self.stdout.write(f'Created draft course {course.pk}. No existing records changed.')
