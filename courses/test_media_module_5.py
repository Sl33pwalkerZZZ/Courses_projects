"""Isolated safety regressions for the create-only Module 5 importer."""
import io
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from courses.management.commands import import_media_module_5 as importer
from courses.management.commands.import_first_course import curriculum_snapshot
from courses.models import Assignment, Course, Direction, Lesson, LessonAttachment, LessonLearningContent, Module
from quizzes.models import Quiz
from studio.models import CourseSettings


class MediaModule5Tests(TestCase):
    def setUp(self):
        self.author = get_user_model().objects.create_user(username='fixture-owner', role='author')
        direction = Direction.objects.create(name='Fixture', slug='fixture')
        self.course = Course.objects.create(pk=10, title=importer.COURSE_TITLE, slug=importer.COURSE_SLUG,
                                            author=self.author, direction=direction)
        CourseSettings.objects.create(course=self.course, language='ru')
        for order, title in enumerate(importer.PREVIOUS_MODULES, 1):
            module = Module.objects.create(course=self.course, title=title, order=order)
            for position in range(1, 4):
                Lesson.objects.create(module=module, title=f'Existing {order}/{position}',
                                      text_content='Original educational content', order=position)
        self.other = Course.objects.create(pk=8, title='Preserved', slug='preserved', author=self.author,
                                           direction=direction, is_published=True)
        self.before = curriculum_snapshot(self.course)
        self.other_before = curriculum_snapshot(self.other)

    def run_import(self, *args):
        output = io.StringIO()
        call_command('import_media_module_5', *args, stdout=output)
        return output.getvalue()

    def assert_preserved(self):
        current = curriculum_snapshot(self.course)
        current['modules'] = [m for m in current['modules'] if m['order'] != 5]
        self.assertEqual(current, self.before)
        self.assertEqual(curriculum_snapshot(self.other), self.other_before)

    def test_default_and_explicit_dry_run(self):
        with patch.object(importer, 'create_backup') as backup:
            for args in [(), ('--dry-run',)]:
                output = self.run_import(*args)
                self.assertIn('Dry-run only', output)
                self.assertIn('"attachments": 0', output)
            backup.assert_not_called()
        self.assertEqual(Module.objects.count(), 4)
        self.assertEqual(Lesson.objects.count(), 12)
        self.assert_preserved()

    @patch.object(importer, 'create_backup', return_value=Path('/isolated-backup'))
    def test_exact_creation_and_idempotency(self, backup):
        self.run_import('--apply')
        lessons = list(self.course.modules.get(order=5).lessons.order_by('order'))
        self.assertEqual(len(lessons), 3)
        for order, (lesson, expected) in enumerate(zip(lessons, importer.load_content()['lessons']), 1):
            self.assertEqual(lesson.order, order)
            self.assertEqual(lesson.title, expected['title'])
            self.assertEqual(lesson.text_content, expected['text_content'])
            self.assertEqual(lesson.learning_content.objectives, expected['objectives'])
            self.assertEqual(lesson.learning_content.source_sections, expected['source_sections'])
            self.assertEqual(lesson.learning_content.interactions, [])
        snapshot = curriculum_snapshot(self.course)
        self.assertIn('no-op', self.run_import('--apply'))
        self.assertIn('no-op', self.run_import('--dry-run'))
        self.assertEqual(backup.call_count, 1)
        self.assertEqual(snapshot, curriculum_snapshot(self.course))
        self.assertEqual(Course.objects.count(), 2)
        self.assertEqual(Assignment.objects.count(), 0)
        self.assertEqual(Quiz.objects.count(), 0)
        self.assertEqual(LessonAttachment.objects.count(), 0)
        self.assertFalse(Course.objects.get(pk=10).is_published)
        self.assert_preserved()

    @patch.object(importer, 'create_backup', return_value=Path('/isolated-backup'))
    def test_later_media_do_not_break_idempotency(self, backup):
        self.run_import('--apply')
        lesson = self.course.modules.get(order=5).lessons.first()
        attachment = LessonAttachment.objects.create(lesson=lesson, kind='video', file='lessons/later.mp4')
        self.assertIn('no-op', self.run_import('--apply'))
        self.assertTrue(LessonAttachment.objects.filter(pk=attachment.pk, file='lessons/later.mp4').exists())
        self.assertEqual(backup.call_count, 1)

    def test_conflicting_partial_module_rejected_before_backup(self):
        Module.objects.create(course=self.course, order=5, title=importer.MODULE_TITLE)
        with patch.object(importer, 'create_backup') as backup, self.assertRaises(CommandError):
            self.run_import('--apply')
        backup.assert_not_called()
        self.assertEqual(Lesson.objects.count(), 12)

    @patch.object(importer, 'create_backup', return_value=Path('/isolated-backup'))
    def test_changed_existing_content_is_not_overwritten(self, backup):
        self.run_import('--apply')
        lesson = self.course.modules.get(order=5).lessons.first()
        lesson.text_content = 'Editorial change must survive'
        lesson.save(update_fields=['text_content'])
        with self.assertRaises(CommandError):
            self.run_import('--apply')
        lesson.refresh_from_db()
        self.assertEqual(lesson.text_content, 'Editorial change must survive')
        self.assertEqual(backup.call_count, 1)

    def test_target_identity_publication_and_author_guards(self):
        for field, value in [('slug', 'wrong'), ('title', 'wrong'), ('is_published', True)]:
            with self.subTest(field=field):
                original = getattr(self.course, field)
                Course.objects.filter(pk=10).update(**{field: value})
                with self.assertRaises(CommandError):
                    self.run_import()
                Course.objects.filter(pk=10).update(**{field: original})
        self.author.role = 'student'
        self.author.save(update_fields=['role'])
        with self.assertRaises(CommandError):
            self.run_import()
        self.assertEqual(Module.objects.count(), 4)

    def test_incomplete_previous_module_rejected(self):
        lesson = self.course.modules.get(order=2).lessons.first()
        lesson.order = 7
        lesson.save(update_fields=['order'])
        with self.assertRaises(CommandError):
            self.run_import()

    def test_source_checksum_rejects_unreviewed_source(self):
        with patch.object(importer, 'SOURCE_SHA256', 'unexpected'), self.assertRaises(CommandError):
            self.run_import()

    def test_backup_failure_prevents_writes(self):
        with patch.object(importer, 'create_backup', side_effect=CommandError('backup failed')):
            with self.assertRaises(CommandError):
                self.run_import('--apply')
        self.assertEqual(Module.objects.count(), 4)
        self.assert_preserved()

    @patch.object(importer, 'create_backup', return_value=Path('/isolated-backup'))
    def test_partial_failure_rolls_back(self, backup):
        original = LessonLearningContent.save
        calls = 0

        def fail_second(instance, *args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise RuntimeError('isolated failure')
            return original(instance, *args, **kwargs)

        with patch.object(LessonLearningContent, 'save', fail_second), self.assertRaises(RuntimeError):
            self.run_import('--apply')
        self.assertEqual(Module.objects.count(), 4)
        self.assertEqual(Lesson.objects.count(), 12)
        self.assert_preserved()


class Module5BackupTests(TestCase):
    def test_backup_verifies_isolated_sqlite_and_preserves_source(self):
        import hashlib
        import sqlite3
        import tempfile
        from courses.management.commands.import_media_module import create_backup

        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'fixture.sqlite3'
            with sqlite3.connect(source) as db:
                db.execute('CREATE TABLE courses_course (id INTEGER PRIMARY KEY, title TEXT)')
                db.execute("INSERT INTO courses_course VALUES (10, 'Isolated fixture')")
            original = hashlib.sha256(source.read_bytes()).hexdigest()
            backup = create_backup(source, Path(directory) / 'backups')
            with sqlite3.connect(f'file:{backup}?mode=ro', uri=True) as db:
                self.assertEqual(db.execute('PRAGMA integrity_check').fetchall(), [('ok',)])
                self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(), [])
                self.assertEqual(db.execute('SELECT id FROM courses_course').fetchall(), [(10,)])
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), original)
