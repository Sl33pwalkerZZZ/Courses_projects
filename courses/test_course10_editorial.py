"""C1 scope, canonical consistency, rollback and existing assessment preservation."""
import io
from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TransactionTestCase

from courses.management.course10_editorial import load_corrections
from courses.management.commands.import_media_module import source_plan
from courses.management.commands.import_media_module_6 import load_source
from courses.models import Assignment, Course, Direction, Lesson, LessonLearningContent, Module
from courses.serializers import AssignmentSerializer
from progress.models import Enrollment, AssignmentSubmission
from quizzes.models import Quiz, QuizQuestion, QuizChoice
from quizzes.services import submit_attempt
from studio.presentation import assignment_data


class Course10EditorialTests(TransactionTestCase):
    def setUp(self):
        self.edits = load_corrections()
        user = get_user_model().objects.create_user(username='c1-author', role='author')
        self.student = get_user_model().objects.create_user(username='c1-student', role='student')
        direction = Direction.objects.create(name='C1', slug='c1')
        self.course = Course.objects.create(pk=10, slug='ai-media-content', title='C1', author=user, direction=direction)
        self.other = Course.objects.create(pk=8, slug='preserve', title='Preserve', author=user, direction=direction, is_published=True)
        self.targets = []
        for entry in self.edits['lessons']:
            module = Module.objects.create(course=self.course, order=entry['module_order'], title='Fixture')
            lesson = Lesson.objects.create(module=module, order=entry['lesson_order'], title=entry['title'], text_content=entry['before']['text_content'])
            LessonLearningContent.objects.create(lesson=lesson, source_sections=entry['before']['source_sections'], objectives=['A', 'B', 'C'])
            self.targets.append(lesson)
        self.assignment = Assignment.objects.create(lesson=self.targets[-1], type='text', learning_activity='final_media_project', description=self.edits['assignment']['before'])
        self.submission = AssignmentSubmission.objects.create(assignment=self.assignment, student=self.student, content='Historical work', status='rejected', reviewer_comment='Historical feedback')
        Enrollment.objects.create(student=self.student, course=self.course)
        data, _ = load_source()
        self.quiz = Quiz.objects.create(lesson=self.targets[-1], title=data['quiz']['title'], instructions=data['quiz']['instructions'], passing_percentage=70, is_published=True)
        for n, q in enumerate(data['quiz']['questions'], 1):
            question = QuizQuestion.objects.create(quiz=self.quiz, order=n, text=q['text'], explanation=q['explanation'])
            for order, (text, correct) in enumerate(q['choices'], 1):
                QuizChoice.objects.create(question=question, text=text, is_correct=correct, order=order)

    def run_command(self, *args):
        out = io.StringIO()
        call_command('correct_course10_editorial', *args, stdout=out)
        return out.getvalue()

    def test_default_preview_is_read_only(self):
        with patch('courses.management.commands.correct_course10_editorial.create_backup') as backup:
            output = self.run_command()
        self.assertIn('"mode": "dry-run"', output)
        backup.assert_not_called()
        self.targets[0].refresh_from_db()
        self.assertEqual(self.targets[0].text_content, self.edits['lessons'][0]['before']['text_content'])

    @patch('courses.management.commands.correct_course10_editorial.create_backup', return_value=Path('/tmp/verified-c1-backup'))
    def test_apply_is_exact_idempotent_and_preserves_assessments(self, backup):
        questions = list(QuizQuestion.objects.values())
        choices = list(QuizChoice.objects.values())
        submissions = list(AssignmentSubmission.objects.values())
        self.run_command('--apply')
        self.assertIn('"updates": []', self.run_command('--apply'))
        backup.assert_called_once()
        for lesson, entry in zip(self.targets, self.edits['lessons']):
            lesson.refresh_from_db()
            self.assertEqual(lesson.text_content, entry['after']['text_content'])
            self.assertEqual(lesson.learning_content.source_sections, entry['after']['source_sections'])
            self.assertEqual(lesson.learning_content.objectives, ['A', 'B', 'C'])
        self.assignment.refresh_from_db()
        self.assertEqual(assignment_data(self.assignment), AssignmentSerializer(self.assignment).data)
        self.assertEqual(self.assignment.description, self.edits['assignment']['after'])
        self.assertEqual(list(QuizQuestion.objects.values()), questions)
        self.assertEqual(list(QuizChoice.objects.values()), choices)
        self.assertEqual(list(AssignmentSubmission.objects.values()), submissions)
        self.quiz.refresh_from_db(); self.assertTrue(self.quiz.is_published)
        self.course.refresh_from_db(); self.assertFalse(self.course.is_published)
        self.other.refresh_from_db(); self.assertTrue(self.other.is_published)

    def test_real_studio_and_student_api_instructions_agree(self):
        from rest_framework.test import APIRequestFactory, force_authenticate
        from studio.views import LessonAssignmentsView
        from courses.views import LessonDetailView
        with patch('courses.management.commands.correct_course10_editorial.create_backup'):
            self.run_command('--apply')
        factory = APIRequestFactory()
        request = factory.get('/')
        force_authenticate(request, user=self.course.author)
        studio = LessonAssignmentsView.as_view()(request, pk=self.targets[-1].pk)
        request = factory.get('/')
        force_authenticate(request, user=self.student)
        student = LessonDetailView.as_view()(request, pk=self.targets[-1].pk)
        self.assertEqual(studio.status_code, 200)
        self.assertEqual(student.status_code, 200)
        self.assertEqual(studio.data[0]['description'], student.data['assignments'][0]['description'])
        self.assertEqual(student.data['text_content'], self.edits['lessons'][1]['after']['text_content'])

    def test_published_course_and_referenced_renamed_heading_reject(self):
        from courses.models import LessonAttachment
        self.course.is_published = True
        self.course.save()
        with self.assertRaises(CommandError):
            self.run_command()
        self.course.is_published = False
        self.course.save()
        LessonAttachment.objects.create(lesson=self.targets[0], kind='srt', sha256='a' * 64,
            after_section='Как будет оцениваться работа')
        with patch('courses.management.commands.correct_course10_editorial.create_backup') as backup:
            with self.assertRaises(CommandError):
                self.run_command('--apply')
        backup.assert_not_called()

    def test_conflict_or_mixed_lesson_state_rejected(self):
        self.targets[0].text_content += '\nTeacher edit'
        self.targets[0].save()
        with patch('courses.management.commands.correct_course10_editorial.create_backup') as backup:
            with self.assertRaises(CommandError):
                self.run_command('--apply')
        backup.assert_not_called()
        self.targets[1].refresh_from_db()
        self.assertEqual(self.targets[1].text_content, self.edits['lessons'][1]['before']['text_content'])

    def test_backup_failure_prevents_all_writes(self):
        with patch('courses.management.commands.correct_course10_editorial.create_backup', side_effect=CommandError('Backup failed')):
            with self.assertRaises(CommandError):
                self.run_command('--apply')
        self.targets[0].refresh_from_db()
        self.assertEqual(self.targets[0].text_content, self.edits['lessons'][0]['before']['text_content'])

    def test_mid_write_failure_rolls_back(self):
        from courses.management.commands.correct_course10_editorial import write_plan
        def fail(plan):
            write_plan(plan[:1])
            raise RuntimeError('synthetic failure')
        with patch('courses.management.commands.correct_course10_editorial.create_backup'), patch('courses.management.commands.correct_course10_editorial.write_plan', side_effect=fail):
            with self.assertRaises(RuntimeError):
                self.run_command('--apply')
        self.targets[0].refresh_from_db()
        self.assertEqual(self.targets[0].text_content, self.edits['lessons'][0]['before']['text_content'])

    def test_canonical_sources_and_shared_required_materials(self):
        source = source_plan(Path(settings.BASE_DIR) / 'course_sources/media_module_1.docx')
        self.assertEqual(source['lessons'][2]['text_content'], self.edits['lessons'][0]['after']['text_content'])
        m6, _ = load_source()
        self.assertEqual(m6['lesson']['text_content'], self.edits['lessons'][1]['after']['text_content'])
        self.assertEqual(m6['assignment']['description'], self.edits['assignment']['after'])
        materials = m6['lesson']['text_content'].split('\n\n')[3].split(' Не заявляйте')[0]
        self.assertIn(materials, m6['assignment']['description'])
        rubric = m6['lesson']['text_content'].split('\n\n')[7].split(' Платформа')[0]
        self.assertIn(rubric, m6['assignment']['description'])
        self.assertIn('её отсутствие не снижает оценку ни по одному', materials)
        self.assertIn('Сейчас выдача сертификатов по этому курсу отключена.', m6['lesson']['text_content'])
        self.assertNotIn('Баллы:', source['lessons'][2]['text_content'])
        self.assertNotIn('7 из 10', source['lessons'][2]['text_content'])

    def test_quiz_scoring_and_attempt_snapshots_unchanged_after_c1(self):
        import uuid
        def answers(count):
            return [{'question_id': q.pk, 'choice_ids': [q.choices.get(is_correct=True).pk if i < count else q.choices.filter(is_correct=False).first().pk]} for i, q in enumerate(self.quiz.questions.all())]
        failed, _ = submit_attempt(quiz_id=self.quiz.pk, student=self.student, submission_id=uuid.uuid4(), answers=answers(10))
        passed, _ = submit_attempt(quiz_id=self.quiz.pk, student=self.student, submission_id=uuid.uuid4(), answers=answers(11))
        self.assertFalse(failed.passed); self.assertTrue(passed.passed)
        snapshots = list(passed.answers.values())
        with patch('courses.management.commands.correct_course10_editorial.create_backup'):
            self.run_command('--apply')
        passed.refresh_from_db(); failed.refresh_from_db()
        self.assertTrue(passed.passed); self.assertFalse(failed.passed)
        self.assertEqual(passed.correct_count, 11)
        self.assertEqual(list(passed.answers.values()), snapshots)
