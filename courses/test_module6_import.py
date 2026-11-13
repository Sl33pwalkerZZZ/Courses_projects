import io
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from certificates.models import CourseCertificatePolicy
from courses.models import Assignment, Course, Direction, Lesson, Module
from quizzes.models import Quiz


class Module6ImportTests(TestCase):
    def setUp(self):
        self.author = get_user_model().objects.create_user(username='module-six-author', role='author')
        direction = Direction.objects.create(name='Module six fixtures', slug='module-six-fixtures')
        self.course = Course.objects.create(pk=10, title='ИИ для создания медиаконтента: от идеи до публикации',
            slug='ai-media-content', author=self.author, direction=direction, is_published=False)
        for module_order in range(1, 6):
            module = Module.objects.create(course=self.course, title=f'Preserved module {module_order}', order=module_order)
            for lesson_order in range(1, 4):
                Lesson.objects.create(module=module, title=f'Preserved lesson {module_order}-{lesson_order}', order=lesson_order, text_content='Preserved source.')

    def command(self, *args):
        output = io.StringIO()
        with tempfile.TemporaryDirectory() as directory:
            call_command('import_media_module_6', *args, '--backup-dir', directory, stdout=output)
        return output.getvalue()

    def test_dry_run_describes_exact_draft_assessment_without_writes(self):
        result = self.command('--dry-run')
        self.assertIn('"questions": 15', result)
        self.assertIn('Dry-run only', result)
        self.assertEqual(self.course.modules.count(), 5)
        self.assertEqual(Lesson.objects.filter(module__course=self.course).count(), 15)
        self.assertFalse(Assignment.objects.exists())
        self.assertFalse(Quiz.objects.exists())
        self.assertFalse(CourseCertificatePolicy.objects.exists())

    @patch('courses.management.commands.import_media_module_6.create_backup')
    def test_apply_creates_one_draft_assessment_and_is_idempotent(self, backup):
        backup.return_value = Path('/tmp/module-6-fixture-backup.sqlite3')
        result = self.command('--apply')
        self.assertIn('Created draft Module 6', result)
        module = self.course.modules.get(order=6)
        lesson = module.lessons.get(order=1)
        self.assertEqual(module.title, 'Итоговая аттестация и получение сертификата')
        self.assertEqual(lesson.learning_content.objectives.__len__(), 3)
        self.assertEqual(lesson.learning_content.source_sections.__len__(), 6)
        assignment = lesson.assignments.get(learning_activity='final_media_project')
        self.assertEqual(assignment.type, 'text')
        quiz = lesson.quiz
        self.assertFalse(quiz.is_published)
        self.assertEqual(quiz.passing_percentage, 70)
        self.assertEqual(quiz.questions.count(), 15)
        self.assertTrue(all(question.type == 'single' and question.choices.count() == 4 and question.choices.filter(is_correct=True).count() == 1 for question in quiz.questions.all()))
        policy = self.course.certificate_policy
        self.assertFalse(policy.enabled)
        self.assertFalse(policy.issuer_approved)
        self.assertEqual(policy.required_lessons.count(), 15)
        self.assertFalse(policy.required_lessons.filter(module=module).exists())
        self.assertEqual(list(policy.required_assignments.values_list('pk', flat=True)), [assignment.pk])
        self.assertFalse(self.course.is_published)
        self.assertIn('no-op', self.command('--apply'))
        backup.assert_called_once()

    def test_conflicting_target_stops_without_overwrite(self):
        Module.objects.create(course=self.course, title='Unexpected final module', order=6)
        with self.assertRaises(CommandError):
            self.command('--dry-run')
        self.assertEqual(self.course.modules.count(), 6)
        self.assertFalse(Assignment.objects.exists())
