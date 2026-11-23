"""C2 mutation tests run exclusively in disposable databases."""
import io
import uuid
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TransactionTestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from courses.management.commands.reorder_course10_quiz5 import load_map, plan_reorder, write_orders
from courses.models import Course, Direction, Lesson, Module
from progress.models import Enrollment
from quizzes.models import Quiz, QuizQuestion, QuizChoice, QuizAttempt, QuizAnswer
from quizzes.services import submit_attempt
from quizzes.views import LessonQuizView


class Quiz5OrderTests(TransactionTestCase):
    def setUp(self):
        self.data = load_map()
        author = get_user_model().objects.create_user(username='c2-author', role='author')
        self.student = get_user_model().objects.create_user(username='c2-student', role='student')
        direction = Direction.objects.create(name='C2', slug='c2')
        self.course = Course.objects.create(pk=10, slug='ai-media-content', title='C2 draft', author=author, direction=direction)
        self.other = Course.objects.create(pk=8, slug='preserve-eight', title='Preserve', author=author, direction=direction, is_published=True)
        module = Module.objects.create(course=self.course, order=6, title='Final')
        Lesson.objects.create(pk=116, module=module, order=1, title='Final', text_content='Preserved')
        self.quiz = Quiz.objects.create(**self.data['quiz'])
        for entry in self.data['questions']:
            QuizQuestion.objects.create(**entry['question'])
            for choice in entry['choices']:
                QuizChoice.objects.create(**choice['before'])
        Enrollment.objects.create(student=self.student, course=self.course)

    def command(self, *args):
        out = io.StringIO()
        call_command('reorder_course10_quiz5', *args, stdout=out)
        return out.getvalue()

    def api(self):
        request = APIRequestFactory().get('/')
        force_authenticate(request, user=self.student)
        response = LessonQuizView.as_view()(request, lesson_id=116)
        self.assertEqual(response.status_code, 200)
        return response.data['quiz']

    def answers(self, correct_count):
        return [{'question_id': q.pk, 'choice_ids': [q.choices.get(is_correct=True).pk if i < correct_count else q.choices.filter(is_correct=False).first().pk]}
                for i, q in enumerate(self.quiz.questions.all())]

    def test_default_dry_run_never_writes_or_backs_up(self):
        before = list(QuizChoice.objects.order_by('pk').values())
        with patch('courses.management.commands.reorder_course10_quiz5.create_backup') as backup:
            output = self.command()
        self.assertIn('"mode": "dry-run"', output)
        self.assertEqual(list(QuizChoice.objects.order_by('pk').values()), before)
        backup.assert_not_called()

    @patch('courses.management.commands.reorder_course10_quiz5.create_backup', return_value=Path('/verified-test-backup'))
    def test_exact_permutation_ids_keys_and_student_api(self, backup):
        before = list(QuizChoice.objects.order_by('pk').values())
        questions = list(QuizQuestion.objects.values())
        quiz = list(Quiz.objects.values())
        courses = list(Course.objects.order_by('pk').values())
        api_before = self.api()
        self.command('--apply')
        after = list(QuizChoice.objects.order_by('pk').values())
        self.assertEqual([{k: v for k, v in row.items() if k != 'order'} for row in before],
                         [{k: v for k, v in row.items() if k != 'order'} for row in after])
        self.assertEqual(list(QuizQuestion.objects.values()), questions)
        self.assertEqual(list(Quiz.objects.values()), quiz)
        self.assertEqual(list(Course.objects.order_by('pk').values()), courses)
        self.assertNotEqual(api_before, self.api())
        correct = []
        for actual, expected in zip(self.api()['questions'], self.data['questions']):
            self.assertEqual([v['id'] for v in actual['choices']],
                             [v['before']['id'] for v in sorted(expected['choices'], key=lambda v: v['after_order'])])
            self.assertTrue(all('is_correct' not in v for v in actual['choices']))
            correct.append(self.quiz.questions.get(pk=actual['id']).choices.get(is_correct=True).order)
        self.assertEqual(sorted(correct.count(i) for i in range(1, 5)), [3, 4, 4, 4])
        self.assertIn('"status": "KEEP"', self.command('--apply'))
        backup.assert_called_once()

    def test_text_key_and_partial_order_conflicts_refuse_before_backup(self):
        row = QuizChoice.objects.order_by('pk').first()
        for field, value in [('text', 'unexpected'), ('is_correct', not row.is_correct), ('order', 99)]:
            original = getattr(row, field)
            QuizChoice.objects.filter(pk=row.pk).update(**{field: value})
            with patch('courses.management.commands.reorder_course10_quiz5.create_backup') as backup:
                with self.assertRaises(CommandError):
                    self.command('--apply')
            backup.assert_not_called()
            QuizChoice.objects.filter(pk=row.pk).update(**{field: original})

    def test_new_attempts_block_without_changing_history(self):
        attempt, _ = submit_attempt(quiz_id=5, student=self.student, submission_id=uuid.uuid4(), answers=self.answers(10))
        before = (list(QuizAttempt.objects.values()), list(QuizAnswer.objects.values()), list(QuizChoice.objects.values()))
        with patch('courses.management.commands.reorder_course10_quiz5.create_backup') as backup:
            with self.assertRaisesMessage(CommandError, 'Attempts now exist'):
                self.command('--apply')
        backup.assert_not_called()
        self.assertEqual(before, (list(QuizAttempt.objects.values()), list(QuizAnswer.objects.values()), list(QuizChoice.objects.values())))
        self.assertFalse(attempt.passed)

    @patch('courses.management.commands.reorder_course10_quiz5.create_backup', return_value=Path('/verified-test-backup'))
    def test_scoring_10_fails_11_passes_and_noop_preserves_new_history(self, backup):
        ten, eleven = self.answers(10), self.answers(11)
        self.command('--apply')
        failed, _ = submit_attempt(quiz_id=5, student=self.student, submission_id=uuid.uuid4(), answers=ten)
        passed, _ = submit_attempt(quiz_id=5, student=self.student, submission_id=uuid.uuid4(), answers=eleven)
        self.assertFalse(failed.passed); self.assertEqual(failed.correct_count, 10)
        self.assertTrue(passed.passed); self.assertEqual(passed.correct_count, 11)
        self.assertEqual(str(failed.score), '66.67'); self.assertEqual(str(passed.score), '73.33')
        before = (list(QuizAttempt.objects.values()), list(QuizAnswer.objects.values()))
        self.assertIn('"status": "KEEP"', self.command('--apply'))
        self.assertEqual(before, (list(QuizAttempt.objects.values()), list(QuizAnswer.objects.values())))
        backup.assert_called_once()

    def test_failed_backup_never_updates(self):
        before = list(QuizChoice.objects.values())
        with patch('courses.management.commands.reorder_course10_quiz5.create_backup', side_effect=CommandError('Backup failed')):
            with self.assertRaises(CommandError):
                self.command('--apply')
        self.assertEqual(before, list(QuizChoice.objects.values()))

    def test_mid_write_failure_rolls_back_all_orders(self):
        before = list(QuizChoice.objects.values())
        def fail(plan):
            write_orders(plan[:1])
            raise RuntimeError('synthetic failure')
        with patch('courses.management.commands.reorder_course10_quiz5.create_backup'), patch('courses.management.commands.reorder_course10_quiz5.write_orders', side_effect=fail):
            with self.assertRaises(RuntimeError):
                self.command('--apply')
        self.assertEqual(before, list(QuizChoice.objects.values()))

    def test_wrong_publication_or_threshold_refused(self):
        Quiz.objects.filter(pk=5).update(passing_percentage=71)
        with self.assertRaises(CommandError):
            plan_reorder()
        Quiz.objects.filter(pk=5).update(passing_percentage=70)
        self.course.is_published = True
        self.course.save()
        with self.assertRaises(CommandError):
            plan_reorder()
