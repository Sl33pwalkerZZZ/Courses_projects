"""Authorization matrix uses temporary fixtures, never the existing almas account."""
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Permission
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from courses.models import Assignment, Course, Direction, Lesson, LessonImage, Module
from progress.models import AssignmentSubmission, Enrollment
from quizzes.models import Quiz, QuizChoice, QuizQuestion
from .models import PublicationRequest
from .permissions import effective_permissions
from .services import owned_courses


class RoleSecurityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.student = User.objects.create_user(username='role-student')
        cls.staff = User.objects.create_user(username='role-staff', is_staff=True)
        cls.staff.user_permissions.add(*Permission.objects.filter(content_type__app_label='courses'))
        cls.author = User.objects.create_user(username='role-author-a', role='author')
        cls.other = User.objects.create_user(username='role-author-b', role='author')
        cls.admin = User.objects.create_user(username='role-admin', role='admin')
        cls.super_student = User.objects.create_user(username='role-super', role='student', is_staff=True, is_superuser=True)
        cls.inactive = User.objects.create_user(username='role-inactive', role='admin', is_superuser=True, is_active=False)
        direction = Direction.objects.create(name='Role fixtures', slug='role-fixtures')
        cls.own = Course.objects.create(title='Own', slug='role-own', description='Private A', author=cls.author, direction=direction)
        cls.foreign = Course.objects.create(title='Other', slug='role-other', description='Private B', author=cls.other, direction=direction)
        cls.module = Module.objects.create(course=cls.foreign, title='Private module', order=1)
        cls.lesson = Lesson.objects.create(module=cls.module, title='Private lesson', text_content='Private body', order=1)
        cls.quiz = Quiz.objects.create(lesson=cls.lesson, title='Private answer key')
        question = QuizQuestion.objects.create(quiz=cls.quiz, text='Which?', type='single')
        QuizChoice.objects.create(question=question, text='Private correct answer', is_correct=True)
        QuizChoice.objects.create(question=question, text='Alternative')
        cls.assignment = Assignment.objects.create(lesson=cls.lesson, type='text', description='Private task')
        cls.submission = AssignmentSubmission.objects.create(assignment=cls.assignment, student=cls.student, content='Private work')
        cls.image = LessonImage.objects.create(lesson=cls.lesson, image='lessons/role-fixture.png')
        cls.review = PublicationRequest.objects.create(course=cls.foreign, requested_by=cls.other, fingerprint='a' * 64)

    def client_for(self, user):
        client = APIClient()
        if user is not None:
            client.force_authenticate(user)
        return client

    def paths(self):
        return [
            'meta/', 'dashboard/', 'courses/', f'courses/{self.foreign.pk}/',
            f'courses/{self.foreign.pk}/modules/', f'courses/{self.foreign.pk}/reorder/',
            f'modules/{self.module.pk}/', f'modules/{self.module.pk}/lessons/', f'modules/{self.module.pk}/reorder/',
            f'lessons/{self.lesson.pk}/', f'lessons/{self.lesson.pk}/quiz/',
            f'lessons/{self.lesson.pk}/assignments/', f'lessons/{self.lesson.pk}/images/',
            f'assignments/{self.assignment.pk}/', f'courses/{self.foreign.pk}/submissions/',
            f'submissions/{self.submission.pk}/review/', f'submissions/{self.submission.pk}/file/',
            f'courses/{self.foreign.pk}/publication/', 'reviews/', f'reviews/{self.review.pk}/decision/',
            'instructors/', f'instructors/{self.author.pk}/',
            'enrollment-requests/', 'enrollment-requests/999999/decision/',
            'imports/preview/', f'imports/{uuid4()}/confirm/',
        ]

    def test_anonymous_students_staff_students_and_inactive_denied_all_management_verbs(self):
        for user, status in [(None, 401), (self.student, 403), (self.staff, 403), (self.inactive, 403)]:
            client = self.client_for(user)
            for path in self.paths():
                for method in ['get', 'post', 'patch', 'put', 'delete']:
                    with self.subTest(role=user.role if user else 'anonymous', path=path, method=method):
                        response = getattr(client, method)('/api/studio/' + path, {}, format='json')
                        self.assertEqual(response.status_code, status)
        self.assertEqual(Course.objects.count(), 2)
        self.assertFalse(self.foreign.is_published)

    def test_identity_is_safe_discovery_and_all_other_verbs_are_read_only(self):
        for user in [self.student, self.staff, self.author, self.other, self.admin, self.super_student, self.inactive]:
            client = self.client_for(user)
            identity = client.get('/api/studio/me/')
            self.assertEqual(identity.status_code, 200)
            expected = effective_permissions(user)
            for key, value in expected.items():
                self.assertEqual(identity.data[key], value)
            profile = client.get('/api/auth/me/')
            for key, value in expected.items():
                self.assertEqual(profile.data[key], value)
            for path in ['/api/studio/me/', '/api/auth/me/']:
                for method in ['post', 'patch', 'put', 'delete']:
                    self.assertEqual(getattr(client, method)(path, {'role': 'admin'}, format='json').status_code, 405)
        self.assertEqual(self.client_for(None).get('/api/studio/me/').status_code, 401)

    def test_author_foreign_nested_ids_denied_for_every_verb_without_mutation(self):
        client = self.client_for(self.author)
        paths = [path for path in self.paths() if path not in ['meta/', 'dashboard/', 'courses/', 'imports/preview/'] and not path.startswith('imports/')]
        snapshots = {model: list(model.objects.values()) for model in [Course, Module, Lesson, Quiz, QuizQuestion, QuizChoice, Assignment, AssignmentSubmission, PublicationRequest]}
        for path in paths:
            for method in ['get', 'post', 'patch', 'put', 'delete']:
                with self.subTest(path=path, method=method):
                    response = getattr(client, method)('/api/studio/' + path, {'role': 'admin', 'title': 'Injected', 'ids': [self.module.pk]}, format='json')
                    self.assertIn(response.status_code, [403, 404, 405], response.data)
        for model, before in snapshots.items():
            self.assertEqual(list(model.objects.values()), before)
        self.assertEqual([course['id'] for course in client.get('/api/studio/courses/').data], [self.own.pk])

    def test_admin_and_superuser_student_have_explicit_administrative_authority(self):
        for user in [self.admin, self.super_student]:
            client = self.client_for(user)
            self.assertEqual({course['id'] for course in client.get('/api/studio/courses/').data}, {self.own.pk, self.foreign.pk})
            self.assertEqual(client.get(f'/api/studio/courses/{self.foreign.pk}/').status_code, 200)
            self.assertEqual(client.get('/api/studio/reviews/').status_code, 200)
            self.assertEqual(client.get('/api/studio/instructors/').status_code, 200)
            identity = client.get('/api/studio/me/').data
            self.assertEqual(identity['effective_role'], 'admin')
            self.assertEqual(identity['authority_source'], 'superuser' if user.is_superuser else 'role')
        self.super_student.refresh_from_db()
        self.assertEqual(self.super_student.role, 'student')

    def test_service_scope_and_legacy_preview_follow_the_same_policy(self):
        for user in [AnonymousUser(), self.student, self.staff, self.inactive]:
            self.assertFalse(owned_courses(user).exists())
        for user, expected in [(None, 401), (self.student, 403), (self.staff, 403), (self.author, 403), (self.other, 200), (self.admin, 200), (self.super_student, 200)]:
            client = self.client_for(user)
            self.assertEqual(client.get(f'/api/instructor/courses/{self.foreign.slug}/preview/').status_code, expected)

    def test_admin_can_manage_authors_but_no_self_service_elevation(self):
        for user in [self.student, self.staff, self.author, self.other]:
            response = self.client_for(user).post(f'/api/studio/instructors/{user.pk}/', {'role': 'admin'}, format='json')
            self.assertEqual(response.status_code, 403)
        client = self.client_for(self.admin)
        for data in [{'role': 'admin'}, {'role': 'author', 'is_superuser': True}, {'role': 'author', 'is_staff': True}]:
            self.assertEqual(client.post(f'/api/studio/instructors/{self.student.pk}/', data, format='json').status_code, 400)
        self.assertEqual(client.post(f'/api/studio/instructors/{self.student.pk}/', {'role': 'author'}, format='json').status_code, 200)
        self.student.refresh_from_db()
        self.assertEqual(self.student.role, 'author')
        self.assertFalse(self.student.is_superuser or self.student.is_staff)
        self.assertEqual(client.post(f'/api/studio/instructors/{self.super_student.pk}/', {'role': 'student'}, format='json').status_code, 400)

    def test_same_jwt_uses_current_database_role_and_ignores_role_claims(self):
        client = APIClient()
        token = AccessToken.for_user(self.author)
        token['role'] = 'admin'
        token['is_superuser'] = True
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual([row['id'] for row in client.get('/api/studio/courses/').data], [self.own.pk])
        get_user_model().objects.filter(pk=self.author.pk).update(role='student')
        self.assertEqual(client.get('/api/studio/courses/').status_code, 403)
        self.assertFalse(client.get('/api/studio/me/').data['can_access_studio'])
        # Another account's valid token must get only that account's scope.
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {AccessToken.for_user(self.other)}')
        self.assertEqual([row['id'] for row in client.get('/api/studio/courses/').data], [self.foreign.pk])

    def test_refresh_preserves_identity_but_does_not_restore_revoked_authority(self):
        refresh = RefreshToken.for_user(self.author)
        get_user_model().objects.filter(pk=self.author.pk).update(role='student')
        client = APIClient()
        response = client.post('/api/auth/token/refresh/', {'refresh': str(refresh)}, format='json')
        self.assertEqual(response.status_code, 200)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        self.assertEqual(client.get('/api/studio/courses/').status_code, 403)

    def test_authors_and_staff_students_can_still_study_as_enrolled_learners(self):
        self.foreign.is_published = True
        self.foreign.enrollment_mode = 'open'
        self.foreign.save()
        for user in [self.student, self.staff, self.author]:
            client = self.client_for(user)
            self.assertEqual(client.get('/api/courses/').status_code, 200)
            self.assertIn(client.post(f'/api/courses/{self.foreign.slug}/enroll/').status_code, [200, 201])
            self.assertTrue(Enrollment.objects.filter(student=user, course=self.foreign).exists())
            self.assertEqual(client.get(f'/api/lessons/{self.lesson.pk}/').status_code, 200)
        self.assertEqual(self.client_for(self.author).get(f'/api/studio/courses/{self.foreign.pk}/').status_code, 404)
