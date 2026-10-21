"""Enrollment decisions use disposable fixtures, never real applications."""
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from courses.models import Assignment, Course, Direction, Lesson, Module
from progress.models import Enrollment, EnrollmentRequest
from quizzes.models import Quiz, QuizChoice, QuizQuestion


class EnrollmentManagementTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.student = User.objects.create_user(username='applicant')
        cls.author = User.objects.create_user(username='teacher', role='author')
        cls.admin = User.objects.create_user(username='administrator', role='admin')
        cls.staff = User.objects.create_user(username='staff-student', is_staff=True)
        cls.superuser = User.objects.create_user(username='super-student', is_staff=True, is_superuser=True)
        cls.inactive = User.objects.create_user(username='inactive-admin', role='admin', is_active=False)
        direction = Direction.objects.create(name='Fixture', slug='fixture')
        cls.course = Course.objects.create(title='Published fixture', slug='published-fixture',
            author=cls.author, direction=direction, is_published=True, enrollment_mode='approval')
        module = Module.objects.create(course=cls.course, title='Module', order=1)
        cls.lesson = Lesson.objects.create(module=module, title='Lesson', text_content='Preserved body', order=1)
        cls.assignment = Assignment.objects.create(lesson=cls.lesson, type='text',
            description='Preserved task', learning_activity='ai_selection_map')
        cls.quiz = Quiz.objects.create(lesson=cls.lesson, title='Published quiz', is_published=True)
        for order in range(1, 16):
            question = QuizQuestion.objects.create(quiz=cls.quiz, text=f'Question {order}', order=order)
            QuizChoice.objects.create(question=question, text='Correct', is_correct=True)
            QuizChoice.objects.create(question=question, text='Alternative')

    def setUp(self):
        self.application = EnrollmentRequest.objects.create(student=self.student, course=self.course,
            message='I would like to study this educational course.')
        self.client = APIClient()
        self.list_url = '/api/studio/enrollment-requests/'
        self.decision_url = f'{self.list_url}{self.application.pk}/decision/'

    def decide(self, decision='approve', **extra):
        return self.client.post(self.decision_url, {'decision': decision, **extra}, format='json')

    def test_roles_and_unsupported_methods_cannot_bypass_permissions(self):
        for user, expected in [(None, 401), (self.student, 403), (self.author, 403),
                               (self.staff, 403), (self.inactive, 403)]:
            self.client.force_authenticate(user)
            for method in ['get', 'post', 'patch', 'put', 'delete']:
                for path in [self.list_url, self.decision_url]:
                    with self.subTest(user=user, method=method, path=path):
                        # Authors pass the common Studio gate, then the method
                        # handler either refuses the role or returns 405.
                        self.assertIn(getattr(self.client, method)(path, {}).status_code,
                                      [expected, 405] if user == self.author else [expected])
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'pending')
        self.assertFalse(Enrollment.objects.exists())

    def test_admin_and_superuser_list_filters_and_safe_fields(self):
        for user in [self.admin, self.superuser]:
            self.client.force_authenticate(user)
            response = self.client.get(self.list_url)
            self.assertEqual(response.status_code, 200)
            row = response.data[0]
            self.assertEqual(row['student'], {'id': self.student.pk, 'username': self.student.username})
            self.assertEqual(row['course']['title'], self.course.title)
            self.assertEqual(row['status'], 'pending')
            self.assertNotIn('email', row['student'])
            self.assertEqual(self.client.get(self.list_url, {'status': 'approved'}).data, [])
            self.assertEqual(len(self.client.get(self.list_url, {'status': 'all'}).data), 1)
            self.assertEqual(self.client.get(self.list_url, {'status': 'invalid'}).status_code, 400)

    def test_approval_unlocks_lesson_assignment_and_published_fifteen_question_quiz(self):
        paths = [f'/api/lessons/{self.lesson.pk}/',
                 f'/api/assignments/{self.assignment.pk}/selection-map/',
                 f'/api/lessons/{self.lesson.pk}/quiz/']
        self.client.force_authenticate(self.student)
        for path in paths:
            self.assertEqual(self.client.get(path).status_code, 403)
        self.client.force_authenticate(self.admin)
        first = self.decide(note='Welcome')
        self.assertEqual(first.status_code, 200)
        self.assertTrue(first.data['changed'])
        self.assertEqual(first.data['status'], 'approved')
        for decision in ['approve', 'reject']:
            retry = self.decide(decision, note='Do not replace original decision')
            self.assertFalse(retry.data['changed'])
            self.assertEqual(retry.data['status'], 'approved')
            self.assertEqual(retry.data['admin_note'], 'Welcome')
        self.assertEqual(Enrollment.objects.count(), 1)
        self.application.refresh_from_db()
        self.assertEqual(self.application.reviewed_by, self.admin)
        self.assertIsNotNone(self.application.reviewed_at)
        self.client.force_authenticate(self.student)
        for path in paths:
            self.assertEqual(self.client.get(path).status_code, 200)
        quiz = self.client.get(paths[-1]).data['quiz']
        self.assertEqual(len(quiz['questions']), 15)
        self.assertNotIn('is_correct', str(quiz))
        self.assertEqual(self.client.get('/api/my/enrollment-requests/').data[0]['status'], 'approved')
        self.assertEqual(Enrollment.objects.get().course_id, self.course.pk)

    def test_rejection_history_reapplication_and_existing_enrollment_reuse(self):
        self.client.force_authenticate(self.superuser)
        rejected = self.decide('reject', note='Please explain your study goals.')
        self.assertEqual(rejected.data['status'], 'rejected')
        self.assertFalse(Enrollment.objects.exists())
        self.assertFalse(self.decide().data['changed'])
        self.client.force_authenticate(self.student)
        self.assertEqual(self.client.get(f'/api/lessons/{self.lesson.pk}/').status_code, 403)
        created = self.client.post(f'/api/courses/{self.course.slug}/enrollment-requests/',
            {'message': 'I have now clarified my goals and wish to reapply.'}, format='json')
        self.assertEqual(created.status_code, 201)
        self.assertEqual(EnrollmentRequest.objects.count(), 2)
        existing = Enrollment.objects.create(student=self.student, course=self.course)
        self.decision_url = f"{self.list_url}{created.data['id']}/decision/"
        self.client.force_authenticate(self.admin)
        self.assertEqual(self.decide().data['status'], 'approved')
        self.assertEqual(Enrollment.objects.get().pk, existing.pk)

    def test_invalid_payload_unknown_id_and_atomic_rollback(self):
        self.client.force_authenticate(self.admin)
        for payload in [{}, {'decision': 'pending'}, {'decision': 'approve', 'student': self.admin.pk},
                        {'decision': 'reject', 'note': 'x' * 10001}]:
            self.assertEqual(self.client.post(self.decision_url, payload, format='json').status_code, 400)
        self.assertEqual(self.client.post(f'{self.list_url}999999/decision/',
            {'decision': 'approve'}, format='json').status_code, 404)
        with patch.object(EnrollmentRequest, 'save', side_effect=RuntimeError('Fixture failure')):
            with self.assertRaises(RuntimeError):
                self.decide()
        self.assertFalse(Enrollment.objects.exists())
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'pending')
