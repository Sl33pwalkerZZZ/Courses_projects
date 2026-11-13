"""Admin reads remain available while disabled-mode mutations are blocked."""
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase, override_settings
from django.utils import timezone
from django.urls import reverse

from courses.models import Course, Direction, Lesson, Module
from .admin import IssueForm, PolicyForm
from .models import Certificate, CourseCertificatePolicy


@override_settings(CERTIFICATES_ENABLED=False)
class CertificateAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        # A superuser's stored application role can still be "student".
        cls.superuser = User.objects.create_user(
            username='superuser', is_staff=True, is_superuser=True, role='student',
        )
        cls.administrator = User.objects.create_user(
            username='administrator', is_staff=True, role='admin',
        )
        cls.student = User.objects.create_user(username='student', is_staff=True)
        cls.author = User.objects.create_user(username='author', is_staff=True, role='author')
        cls.nonstaff = User.objects.create_user(username='nonstaff', role='admin')
        cls.inactive = User.objects.create_user(
            username='inactive', is_staff=True, is_superuser=True, is_active=False,
        )
        direction = Direction.objects.create(name='Test', slug='admin-test')
        cls.course = Course.objects.create(
            title='Test course', slug='admin-test', author=cls.author, direction=direction,
            is_published=True,
        )
        # Isolated fixture only, not service issuance or a development DB record.
        cls.certificate = Certificate.objects.create(
            student=cls.student, course=cls.course, learner_name='Test Learner',
            course_title=cls.course.title, issuer_name='Test issuer',
        )

    def request(self, user):
        request = RequestFactory().get('/admin/')
        request.user = user
        return request

    def certificate_app(self, user):
        return next((app for app in admin.site.get_app_list(self.request(user))
                     if app['app_label'] == 'certificates'), None)

    def test_real_app_list_and_permissions_with_issuance_disabled(self):
        for user in (self.superuser, self.administrator):
            with self.subTest(user=user.username):
                models = {item['object_name']: item for item in self.certificate_app(user)['models']}
                self.assertEqual(set(models), {'Certificate', 'CourseCertificatePolicy'})
                self.assertEqual(models['Certificate']['perms'], {
                    'add': False, 'change': False, 'delete': False, 'view': True,
                })
                self.assertEqual(models['CourseCertificatePolicy']['perms'], {
                    'add': False, 'change': False, 'delete': False, 'view': True,
                })
                self.client.force_login(user)
                self.assertEqual(self.client.get('/admin/').status_code, 200)
                self.assertNotContains(self.client.get(reverse('admin:certificates_certificate_changelist')), reverse('admin:certificates_certificate_issue'))
                for name in ('certificate', 'coursecertificatepolicy'):
                    url = reverse(f'admin:certificates_{name}_changelist')
                    self.assertEqual(self.client.get(url).status_code, 200)

    def test_student_author_nonstaff_and_inactive_cannot_see_models(self):
        for user in (self.student, self.author, self.nonstaff, self.inactive):
            with self.subTest(user=user.username):
                self.assertIsNone(self.certificate_app(user))
                for model in (Certificate, CourseCertificatePolicy):
                    model_admin = admin.site._registry[model]
                    for method in ('has_view_permission', 'has_add_permission', 'has_change_permission'):
                        self.assertFalse(getattr(model_admin, method)(self.request(user)))

    def test_staff_students_and_teachers_cannot_open_or_post_admin_workflows(self):
        for user in (self.student, self.author):
            self.client.force_login(user)
            for name in ('certificate', 'coursecertificatepolicy'):
                self.assertEqual(self.client.get(reverse(f'admin:certificates_{name}_changelist')).status_code, 403)
            self.assertEqual(self.client.get(reverse('admin:certificates_coursecertificatepolicy_add')).status_code, 403)
            self.assertEqual(self.client.get(reverse('admin:certificates_certificate_issue')).status_code, 403)
            response = self.client.post(reverse('admin:certificates_certificate_changelist'), {
                'action': 'revoke_selected', '_selected_action': [self.certificate.pk],
            })
            self.assertEqual(response.status_code, 403)
        self.certificate.refresh_from_db()
        self.assertIsNone(self.certificate.revoked_at)

    @override_settings(CERTIFICATES_ENABLED=True)
    def test_policy_creation_editing_and_safe_defaults(self):
        self.client.force_login(self.administrator)
        add = reverse('admin:certificates_coursecertificatepolicy_add')
        response = self.client.get(add)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['adminform'].form['enabled'].value())
        self.assertFalse(response.context['adminform'].form['issuer_approved'].value())
        response = self.client.post(add, {
            'course': self.course.pk, 'require_all_lessons': 'on', 'issuer_name': 'Test issuer',
            '_save': 'Save',
        })
        self.assertEqual(response.status_code, 302)
        policy = CourseCertificatePolicy.objects.get(course=self.course)
        self.assertFalse(policy.enabled)
        self.assertFalse(policy.issuer_approved)
        change = reverse('admin:certificates_coursecertificatepolicy_change', args=[policy.pk])
        response = self.client.post(change, {
            'course': self.course.pk, 'require_all_lessons': 'on', 'issuer_name': 'Confirmed test issuer',
            'issuer_approved': 'on', '_save': 'Save',
        })
        self.assertEqual(response.status_code, 302)
        policy.refresh_from_db()
        self.assertEqual(policy.issuer_name, 'Confirmed test issuer')
        self.assertTrue(policy.issuer_approved)
        self.assertFalse(policy.enabled)

    def test_policy_form_rejects_required_lessons_from_another_course(self):
        foreign = Course.objects.create(
            title='Foreign course', slug='foreign-admin-course', author=self.author,
            direction=self.course.direction,
        )
        foreign_lesson = Lesson.objects.create(
            module=Module.objects.create(course=foreign, title='Foreign module', order=0),
            title='Foreign lesson', order=0,
        )
        form = PolicyForm(data={
            'course': self.course.pk,
            'required_lessons': [foreign_lesson.pk],
            'issuer_name': 'Test issuer',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('required_lessons', form.errors)

    def test_superuser_can_only_view_existing_certificates_not_add_or_change(self):
        self.client.force_login(self.superuser)
        detail = reverse('admin:certificates_certificate_change', args=[self.certificate.pk])
        response = self.client.get(detail)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['has_change_permission'])
        self.assertEqual(set(response.context['adminform'].readonly_fields),
                         {field.name for field in Certificate._meta.fields})
        self.assertEqual(self.client.post(detail, {'learner_name': 'Forged Name'}).status_code, 403)
        add = reverse('admin:certificates_certificate_add')
        self.assertEqual(self.client.get(add).status_code, 403)
        self.assertEqual(self.client.post(add, {'student': self.student.pk, 'course': self.course.pk}).status_code, 403)
        self.certificate.refresh_from_db()
        self.assertEqual(self.certificate.learner_name, 'Test Learner')
        self.assertEqual(Certificate.objects.count(), 1)

    def test_validated_issue_form_remains_gated_by_issuance_switch(self):
        self.client.force_login(self.superuser)
        self.author.certificate_name = 'Автор Тексері'
        self.author.certificate_name_confirmed_at = timezone.now()
        self.author.save(update_fields=['certificate_name', 'certificate_name_confirmed_at'])
        url = reverse('admin:certificates_certificate_issue')
        self.assertEqual(self.client.get(url).status_code, 403)
        # Even direct form POST is denied while issuance is disabled.
        response = self.client.post(url, {
            'student': self.author.pk, 'course': self.course.pk,
            'learner_name': 'Test Learner', 'confirmation': 'on',
        })
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Certificate.objects.count(), 1)

    def test_issue_form_uses_read_only_student_confirmed_name(self):
        self.author.certificate_name = 'Автор Тексері'
        self.author.certificate_name_confirmed_at = timezone.now()
        self.author.save(update_fields=['certificate_name', 'certificate_name_confirmed_at'])
        form = IssueForm(data={
            'student': self.author.pk, 'course': self.course.pk,
            'learner_name': 'Administrator Override', 'confirmation': 'on',
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['learner_name'], 'Автор Тексері')

    @override_settings(CERTIFICATES_ENABLED=True)
    def test_revocation_action_available_without_manual_change_permission(self):
        self.client.force_login(self.administrator)
        model_admin = admin.site._registry[Certificate]
        self.assertFalse(model_admin.has_change_permission(self.request(self.administrator)))
        self.assertIn('revoke_selected', model_admin.get_actions(self.request(self.administrator)))
        response = self.client.post(reverse('admin:certificates_certificate_changelist'), {
            'action': 'revoke_selected', '_selected_action': [self.certificate.pk],
        })
        self.assertEqual(response.status_code, 302)
        self.certificate.refresh_from_db()
        self.assertEqual(self.certificate.revoked_by_id, self.administrator.pk)
        self.assertIsNotNone(self.certificate.revoked_at)
        self.assertEqual(self.certificate.learner_name, 'Test Learner')
