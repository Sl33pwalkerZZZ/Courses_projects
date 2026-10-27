import io
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, SimpleTestCase

from courses.models import Course, Direction, Lesson, Module
from courses.management.commands.import_media_module import SLUG, TITLES, create_backup, source_plan
from courses.management.commands.import_first_course import curriculum_snapshot


class MediaModuleTests(TestCase):
    def setUp(self):
        self.author = get_user_model().objects.create_user(username='author', role='author')
        self.direction = Direction.objects.create(name='Foundations', slug='ai-foundations')
        self.old = Course.objects.create(title='Existing', slug='existing', author=self.author, direction=self.direction)
        module = Module.objects.create(course=self.old, title='Existing module', order=1)
        Lesson.objects.create(module=module, title='Existing lesson', order=1, text_content='Do not change')
        self.before = curriculum_snapshot(self.old)

    def run_import(self, *args):
        output = io.StringIO()
        call_command('import_media_module', '--author-username', 'author', *args, stdout=output)
        return output.getvalue()

    def test_default_preview_has_no_writes_or_backup(self):
        with patch('courses.management.commands.import_media_module.create_backup') as backup:
            self.assertIn('Dry-run', self.run_import())
            backup.assert_not_called()
        self.assertEqual(Course.objects.count(), 1)

    @patch('courses.management.commands.import_media_module.create_backup', return_value=Path('/isolated-test-backup'))
    def test_creation_content_idempotency_and_existing_protection(self, backup):
        self.run_import('--apply')
        course = Course.objects.get(slug=SLUG)
        self.assertFalse(course.is_published)
        self.assertEqual(course.enrollment_mode, 'open')
        self.assertEqual(course.level, 'beginner')
        self.assertEqual(course.studio_settings.language, 'ru')
        self.assertFalse(course.content_import.review_approved)
        lessons = list(Lesson.objects.filter(module__course=course).order_by('order'))
        self.assertEqual([l.title for l in lessons], TITLES)
        self.assertEqual(course.modules.count(), 1)
        plan = source_plan(Path(settings.BASE_DIR) / 'course_sources/media_module_1.docx')
        for lesson, expected in zip(lessons, plan['lessons']):
            self.assertEqual(lesson.text_content, expected['text_content'])
            self.assertGreater(len(lesson.text_content), 3000)
            self.assertEqual(len(lesson.learning_content.objectives), 3)
        self.assertIn('обычную автоматизацию', lessons[0].text_content)
        self.assertIn('Пример улучшенного запроса', lessons[1].text_content)
        self.assertIn('7 из 10', lessons[2].text_content)
        self.assertIn('https://', lessons[2].text_content)
        from studio.word import parse_docx
        path = Path(settings.BASE_DIR) / 'course_sources/media_module_1.docx'
        source = parse_docx(path.read_bytes(), path.name)
        combined = '\n'.join(l.text_content + '\n' + '\n'.join(l.learning_content.objectives) for l in lessons)
        started = False
        for block in source['blocks']:
            text = block.get('text', '')
            if text.startswith('Урок '):
                started = True
                continue
            if not started or text == 'Цели урока':
                continue
            if block['type'] == 'table':
                for row in [block['headers'], *block['rows']]:
                    for cell in row:
                        self.assertIn(cell, combined)
            else:
                self.assertIn(text, combined)
        snapshot = curriculum_snapshot(course)
        self.assertIn('no-op', self.run_import('--apply'))
        self.assertEqual(backup.call_count, 1)
        self.assertEqual(snapshot, curriculum_snapshot(course))
        self.assertEqual(self.before, curriculum_snapshot(self.old))

    @patch('courses.management.commands.import_media_module.create_backup')
    def test_rollback(self, backup):
        with patch('courses.management.commands.import_media_module.LessonLearningContent.objects.create', side_effect=RuntimeError('failure')):
            with self.assertRaises(RuntimeError):
                self.run_import('--apply')
        self.assertFalse(Course.objects.filter(slug=SLUG).exists())
        self.assertEqual(self.before, curriculum_snapshot(self.old))
        self.assertEqual(Module.objects.count(), 1)
        self.assertEqual(Lesson.objects.count(), 1)

    @patch('courses.management.commands.import_media_module.create_backup')
    def test_backup_failure_prevents_writes(self, backup):
        backup.side_effect = CommandError('backup failed')
        with self.assertRaises(CommandError):
            self.run_import('--apply')
        self.assertEqual(Course.objects.count(), 1)

    @patch('courses.management.commands.import_media_module.create_backup')
    def test_conflict_and_modified_import_rejected(self, backup):
        self.run_import('--apply')
        course = Course.objects.get(slug=SLUG)
        lesson = Lesson.objects.filter(module__course=course).first()
        lesson.text_content = 'Teacher edit'
        lesson.save()
        with self.assertRaises(CommandError):
            self.run_import('--apply')
        lesson.refresh_from_db()
        self.assertEqual(lesson.text_content, 'Teacher edit')

    def test_title_collision_rejected(self):
        from courses.management.commands.import_media_module import TITLE
        self.old.title = TITLE
        self.old.save()
        with self.assertRaises(CommandError):
            self.run_import()

    def test_unauthorized_author_rejected(self):
        self.author.role = 'student'
        self.author.is_staff = True
        self.author.save()
        with self.assertRaises(CommandError):
            self.run_import()

    def test_changed_source_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'changed.docx'
            source.write_bytes(b'changed')
            with self.assertRaises(CommandError):
                self.run_import('--source', str(source))


class BackupTests(SimpleTestCase):
    def test_verified_private_backup_preserves_source(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'source.sqlite3'
            with sqlite3.connect(source) as db:
                db.execute('CREATE TABLE courses_course (id INTEGER PRIMARY KEY, title TEXT)')
                db.execute("INSERT INTO courses_course VALUES (8, 'untouched')")
            before = source.read_bytes()
            backup = create_backup(source, Path(directory) / 'backups')
            self.assertEqual(backup.stat().st_mode & 0o777, 0o600)
            with sqlite3.connect(backup) as db:
                self.assertEqual(db.execute('SELECT * FROM courses_course').fetchall(), [(8, 'untouched')])
                self.assertEqual(db.execute('PRAGMA integrity_check').fetchone(), ('ok',))
            self.assertEqual(source.read_bytes(), before)
