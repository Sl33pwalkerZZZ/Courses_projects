from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as ModelValidationError
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework.exceptions import ValidationError, PermissionDenied

from courses.models import Assignment, Course, Direction, Lesson, Module
from progress.models import AssignmentSubmission, Enrollment, LessonProgress
from quizzes.models import Quiz, QuizAttempt
from .models import Certificate, CourseCertificatePolicy
from .services import eligibility, issue_certificate, revoke_certificate, valid_name


@override_settings(CERTIFICATES_ENABLED=True)
class CertificateTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(username='administrator', role='admin')
        self.author = User.objects.create_user(username='author', role='author')
        self.student = User.objects.create_user(username='student', first_name='Айгерім', last_name='Әбілова')
        self.student.certificate_name = 'Айгерім Әбілова'
        self.student.certificate_name_confirmed_at = timezone.now()
        self.student.save(update_fields=['certificate_name', 'certificate_name_confirmed_at'])
        self.other = User.objects.create_user(username='other')
        self.course = Course.objects.create(title='Курс ИИ', slug='course', author=self.author, direction=Direction.objects.create(name='AI', slug='ai'), is_published=True)
        self.lesson = Lesson.objects.create(module=Module.objects.create(course=self.course, title='Module', order=0), title='Lesson', order=0)
        self.enrollment = Enrollment.objects.create(student=self.student, course=self.course)
        LessonProgress.objects.create(enrollment=self.enrollment, lesson=self.lesson, completed_at=timezone.now())
        self.quiz = Quiz.objects.create(lesson=self.lesson, title='Final', is_published=True)
        self.attempt = QuizAttempt.objects.create(student=self.student, quiz=self.quiz, request_digest='x'*64, score=80, correct_count=8, question_count=10, passing_percentage=70, passed=True)
        self.assignment = Assignment.objects.create(lesson=self.lesson, type='text', description='Practice')
        reviewed = timezone.now()
        self.submission = AssignmentSubmission.objects.create(student=self.student, assignment=self.assignment, status='approved', reviewed_at=reviewed, revision=1, review_history=[{'reviewer_id':self.author.pk, 'status':'approved', 'reviewed_at':reviewed.isoformat(), 'revision':1}])
        self.policy = CourseCertificatePolicy.objects.create(course=self.course, enabled=True, issuer_name='Approved test issuer', issuer_approved=True, final_quiz=self.quiz)
        self.policy.required_assignments.add(self.assignment)
        self.client = APIClient()

    def issue(self):
        return issue_certificate(administrator=self.admin, student=self.student, course_id=self.course.pk)

    def test_eligible_atomic_idempotent_and_opaque(self):
        self.assertTrue(eligibility(self.student, self.course)['eligible'])
        certificate, created = self.issue()
        self.assertTrue(created)
        self.assertEqual(len(certificate.verification_code), 32)
        again, created = self.issue()
        self.assertFalse(created)
        self.assertEqual(again.pk, certificate.pk)
        self.assertEqual(Certificate.objects.count(), 1)

    def test_missing_or_unreliable_assignment_review_blocks(self):
        self.submission.review_history = []
        self.submission.save()
        self.assertFalse(eligibility(self.student, self.course)['eligible'])
        with self.assertRaises(ValidationError): self.issue()
        self.assertFalse(Certificate.objects.exists())

    def test_failed_quiz_and_incomplete_lesson_block(self):
        self.attempt.passed = False
        self.attempt.save()
        self.assertFalse(eligibility(self.student, self.course)['eligible'])
        self.attempt.passed = True
        self.attempt.save()
        LessonProgress.objects.update(completed_at=None)
        self.assertFalse(eligibility(self.student, self.course)['eligible'])

    def test_empty_scope_preserves_all_lessons_behavior(self):
        additional = Lesson.objects.create(module=self.lesson.module, title='Another required lesson', order=1)
        result = eligibility(self.student, self.course)
        self.assertFalse(result['eligible'])
        self.assertIn({'key': 'all_lessons', 'met': False}, result['requirements'])

        LessonProgress.objects.create(enrollment=self.enrollment, lesson=additional, completed_at=timezone.now())
        self.assertTrue(eligibility(self.student, self.course)['eligible'])

    def test_explicit_scope_requires_each_selected_lesson_but_ignores_unselected(self):
        selected = Lesson.objects.create(module=self.lesson.module, title='Selected lesson', order=1)
        unselected = Lesson.objects.create(module=self.lesson.module, title='Unselected assessment lesson', order=2)
        self.policy.required_lessons.add(self.lesson, selected)
        LessonProgress.objects.create(enrollment=self.enrollment, lesson=selected, completed_at=timezone.now())

        result = eligibility(self.student, self.course)
        self.assertTrue(result['eligible'])
        self.assertIn({'key': 'required_lessons', 'met': True}, result['requirements'])
        self.assertNotIn({'key': 'all_lessons', 'met': False}, result['requirements'])
        self.assertNotIn(unselected.pk, result['evidence']['required_lesson_ids'])

        LessonProgress.objects.filter(enrollment=self.enrollment, lesson=selected).update(completed_at=None)
        result = eligibility(self.student, self.course)
        self.assertFalse(result['eligible'])
        self.assertIn({'key': 'required_lessons', 'met': False}, result['requirements'])

    def test_fifteen_instructional_lessons_can_exclude_future_assessment_lesson(self):
        instructional = [self.lesson]
        for order in (1, 2):
            instructional.append(Lesson.objects.create(module=self.lesson.module, title=f'Instructional {order}', order=order))
        for module_order in range(1, 5):
            module = Module.objects.create(course=self.course, title=f'Instructional module {module_order + 1}', order=module_order)
            for lesson_order in range(3):
                instructional.append(Lesson.objects.create(module=module, title=f'Module {module_order + 1} lesson {lesson_order + 1}', order=lesson_order))
        assessment_module = Module.objects.create(course=self.course, title='Final assessment', order=5)
        assessment_lesson = Lesson.objects.create(module=assessment_module, title='Assessment lesson', order=0)
        for lesson in instructional[1:]:
            LessonProgress.objects.create(enrollment=self.enrollment, lesson=lesson, completed_at=timezone.now())
        self.policy.required_lessons.add(*instructional)

        result = eligibility(self.student, self.course)
        self.assertTrue(result['eligible'])
        self.assertEqual(len(result['evidence']['required_lesson_ids']), 15)
        self.assertNotIn(assessment_lesson.pk, result['evidence']['required_lesson_ids'])
        self.assertNotIn({'key': 'all_lessons', 'met': False}, result['requirements'])

    def test_foreign_lesson_scope_is_rejected_and_fails_closed(self):
        foreign = Course.objects.create(title='Other', slug='foreign-lessons', author=self.author, direction=self.course.direction)
        foreign_lesson = Lesson.objects.create(
            module=Module.objects.create(course=foreign, title='Foreign module', order=0),
            title='Foreign lesson', order=0,
        )
        self.policy.required_lessons.add(foreign_lesson)

        with self.assertRaises(ModelValidationError) as error:
            self.policy.full_clean()
        self.assertIn('required_lessons', error.exception.message_dict)
        self.assertFalse(eligibility(self.student, self.course)['eligible'])

    def test_duplicate_and_deleted_lesson_references_are_safe(self):
        selected = Lesson.objects.create(module=self.lesson.module, title='Selected lesson', order=1)
        self.policy.required_lessons.add(selected, selected)
        self.assertEqual(self.policy.required_lessons.count(), 1)

        selected.delete()
        self.assertEqual(self.policy.required_lessons.count(), 0)
        # With the legacy all-lessons switch on, removal of the relation safely
        # falls back to the remaining lessons in the course.
        self.assertTrue(eligibility(self.student, self.course)['eligible'])

    def test_enrollment_and_published_quiz_required(self):
        self.quiz.is_published = False
        self.quiz.save()
        self.assertFalse(eligibility(self.student, self.course)['eligible'])
        self.quiz.is_published = True
        self.quiz.save()
        self.enrollment.delete()
        self.assertFalse(eligibility(self.student, self.course)['eligible'])

    def test_student_author_staff_cannot_issue(self):
        self.student.is_staff = True
        self.student.save()
        for actor in [self.student, self.author, self.other]:
            self.client.force_authenticate(actor)
            response = self.client.post('/api/certificates/admin/issue/', {'student_id':self.student.pk,'course_id':self.course.pk,'learner_name':self.student.get_full_name()})
            self.assertEqual(response.status_code, 403)
        self.assertFalse(Certificate.objects.exists())

    def test_public_verification_minimal_and_revocation(self):
        certificate, _ = self.issue()
        response = self.client.get(f'/api/certificates/verify/{certificate.verification_code}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'valid')
        self.assertNotIn('learner_name', response.data)
        self.assertNotIn('student_id', response.data)
        self.assertNotIn('evidence', response.data)
        revoke_certificate(administrator=self.admin, certificate=certificate, reason='Administrative correction')
        response = self.client.get(f'/api/certificates/verify/{certificate.verification_code}/')
        self.assertEqual(response.data['status'], 'revoked')
        self.client.force_authenticate(self.student)
        self.assertEqual(self.client.get(f'/api/certificates/{certificate.verification_code}/download/').status_code,403)
        self.assertFalse(self.issue()[1])

    def test_other_student_cannot_download(self):
        certificate, _ = self.issue()
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get(f'/api/certificates/{certificate.verification_code}/download/').status_code,404)

    def test_issuance_uses_confirmed_name_instead_of_profile_and_requires_approved_issuer(self):
        self.student.certificate_name = 'Әлия Қасымқызы'
        self.student.certificate_name_confirmed_at = timezone.now()
        self.student.save(update_fields=['certificate_name', 'certificate_name_confirmed_at'])
        certificate, created = self.issue()
        self.assertTrue(created)
        self.assertEqual(certificate.learner_name, 'Әлия Қасымқызы')
        self.policy.issuer_approved = False
        self.policy.save()
        self.assertFalse(eligibility(self.student,self.course)['eligible'])

    @override_settings(CERTIFICATES_ENABLED=False)
    def test_disabled_issuance_keeps_private_reads_but_not_public_verification(self):
        self.client.force_authenticate(self.student)
        response = self.client.get('/api/my/certificates/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])
        with self.assertNumQueries(0):
            self.assertEqual(self.client.get('/api/certificates/verify/unknown/').status_code,404)

    def test_current_threshold_not_old_attempt_threshold(self):
        self.quiz.passing_percentage = 90
        self.quiz.save()
        self.assertFalse(eligibility(self.student, self.course)['eligible'])

    def test_foreign_course_assignment_and_quiz_rejected(self):
        foreign = Course.objects.create(title='Other', slug='other-course', author=self.author, direction=self.course.direction, is_published=True)
        lesson = Lesson.objects.create(module=Module.objects.create(course=foreign,title='Other',order=0),title='Other',order=0)
        assignment = Assignment.objects.create(lesson=lesson,type='text',description='Other')
        self.policy.required_assignments.add(assignment)
        self.assertFalse(eligibility(self.student,self.course)['eligible'])
        self.policy.final_quiz = Quiz.objects.create(lesson=lesson,title='Other quiz')
        with self.assertRaises(ModelValidationError): self.policy.full_clean()

    def test_malformed_name_and_stale_review_audit_block(self):
        for name in ['', 'One', 123, 'Injected <name>']:
            with self.assertRaises(ValidationError):
                valid_name(name)
        self.submission.revision += 1
        self.submission.save()
        self.assertFalse(eligibility(self.student,self.course)['eligible'])

    def test_admin_confirmation_form_and_permissions(self):
        self.admin.is_staff=True
        self.admin.save()
        self.client.force_login(self.admin)
        response=self.client.get('/admin/certificates/certificate/issue/')
        self.assertEqual(response.status_code,200)
        response=self.client.post('/admin/certificates/certificate/issue/',{'student':self.student.pk,'course':self.course.pk,'learner_name':self.student.get_full_name(),'confirmation':'on'})
        self.assertEqual(response.status_code,302)
        self.assertEqual(Certificate.objects.count(),1)
        self.student.is_staff=True
        self.student.save()
        self.client.force_login(self.student)
        self.assertEqual(self.client.get('/admin/certificates/certificate/issue/').status_code,403)

    def test_unknown_code_and_cache_control(self):
        self.assertEqual(self.client.get('/api/certificates/verify/nonexistent/').status_code,404)
        certificate,_=self.issue()
        response=self.client.get(f'/api/certificates/verify/{certificate.verification_code}/')
        self.assertEqual(response['Cache-Control'],'private, no-store')
        self.client.force_authenticate(self.student)
        response=self.client.get('/api/my/certificates/')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response['Cache-Control'],'private, no-store')

    @override_settings(CERTIFICATES_ENABLED=False)
    def test_service_issuance_also_disabled(self):
        with self.assertRaises(PermissionDenied): self.issue()
        self.assertFalse(Certificate.objects.exists())

    def test_only_administrator_can_revoke(self):
        certificate,_=self.issue()
        for actor in [self.student,self.author]:
            self.client.force_authenticate(actor)
            self.assertEqual(self.client.post(f'/api/certificates/admin/{certificate.verification_code}/revoke/',{'reason':'Request'}).status_code,403)
        certificate.refresh_from_db()
        self.assertIsNone(certificate.revoked_at)
        self.client.force_authenticate(self.admin)
        response=self.client.post(f'/api/certificates/admin/{certificate.verification_code}/revoke/',{'reason':'Administrative review'})
        self.assertEqual(response.status_code,200)
        self.assertTrue(response.data['revoked'])

    def test_owner_download_omits_optional_verification_without_trusted_origin(self):
        certificate,_=self.issue()
        self.client.force_authenticate(self.student)
        with self.settings(CERTIFICATE_PUBLIC_ORIGIN=''):
            self.assertEqual(self.client.get(f'/api/certificates/{certificate.verification_code}/download/').status_code,200)

    def test_wrong_reviewer_cannot_establish_evidence(self):
        self.submission.review_history[-1]['reviewer_id']=self.other.pk
        self.submission.save()
        self.assertFalse(eligibility(self.student,self.course)['eligible'])

    def test_unconfirmed_certificate_name_blocks_eligibility_and_issuance(self):
        self.student.certificate_name_confirmed_at = None
        self.student.save(update_fields=['certificate_name_confirmed_at'])
        result = eligibility(self.student, self.course)
        self.assertFalse(result['eligible'])
        self.assertIn({'key': 'certificate_name_confirmed', 'met': False}, result['requirements'])
        with self.assertRaises(ValidationError):
            self.issue()
        self.assertFalse(Certificate.objects.exists())

    def test_certificate_snapshot_survives_later_confirmed_name_change(self):
        certificate, _ = self.issue()
        original_name = certificate.learner_name
        self.student.certificate_name = 'Жанар Әбілова'
        self.student.certificate_name_confirmed_at = None
        self.student.save(update_fields=['certificate_name', 'certificate_name_confirmed_at'])
        self.assertFalse(eligibility(self.student, self.course)['eligible'])
        self.student.certificate_name_confirmed_at = timezone.now()
        self.student.save(update_fields=['certificate_name_confirmed_at'])
        certificate.refresh_from_db()
        self.assertEqual(certificate.learner_name, original_name)

    def test_student_certificate_name_api_confirms_normalized_value_and_resets_on_change(self):
        self.client.force_authenticate(self.student)
        response = self.client.get('/api/my/certificate-name/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['confirmed'])
        self.assertEqual(response.data['learner_name'], 'Айгерім Әбілова')

        # This decomposed spelling is normalized to NFC and whitespace is collapsed.
        response = self.client.put('/api/my/certificate-name/', {
            'learner_name': '  Jose\u0301   Garci\u0301a  ',
            'user_id': self.other.pk,
            'certificate_name_confirmed_at': '2099-01-01T00:00:00Z',
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['learner_name'], 'José García')
        self.assertFalse(response.data['confirmed'])
        self.assertIsNone(response.data['confirmed_at'])
        self.student.refresh_from_db()
        self.other.refresh_from_db()
        self.assertEqual(self.student.certificate_name, 'José García')
        self.assertEqual(self.other.certificate_name, '')
        self.assertIsNone(self.student.certificate_name_confirmed_at)

        response = self.client.post('/api/my/certificate-name/', {
            'learner_name': 'Jose\u0301 Garci\u0301a', 'confirmation': True,
            'confirmed_at': '2099-01-01T00:00:00Z',
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['confirmed'])
        self.assertEqual(response.data['learner_name'], 'José García')
        self.assertIsNotNone(response.data['confirmed_at'])
        self.assertNotEqual(str(response.data['confirmed_at']), '2099-01-01T00:00:00Z')

        response = self.client.put('/api/my/certificate-name/', {'learner_name': 'Әлия Қасымқызы'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data['confirmed'])
        self.assertIsNone(response.data['confirmed_at'])

    def test_certificate_name_api_rejects_missing_invalid_or_unconfirmed_data(self):
        self.student.certificate_name = ''
        self.student.certificate_name_confirmed_at = None
        self.student.save(update_fields=['certificate_name', 'certificate_name_confirmed_at'])
        self.client.force_authenticate(self.student)
        for payload in ({}, {'learner_name': ''}, {'learner_name': 'One'}, {'learner_name': 'Name <script>'}, {'learner_name': 123}):
            with self.subTest(payload=payload):
                self.assertEqual(self.client.put('/api/my/certificate-name/', payload, format='json').status_code, 400)
        for payload in (
            {'confirmation': True}, {'learner_name': '', 'confirmation': True},
            {'learner_name': 'Әлия Қасымқызы', 'confirmation': False},
            {'learner_name': 'Әлия Қасымқызы', 'confirmation': True},
        ):
            with self.subTest(payload=payload):
                self.assertEqual(self.client.post('/api/my/certificate-name/', payload, format='json').status_code, 400)
        self.student.refresh_from_db()
        self.assertIsNone(self.student.certificate_name_confirmed_at)

    def test_certificate_name_api_authentication_and_ownership(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get('/api/my/certificate-name/').status_code, 401)
        self.assertEqual(self.client.put('/api/my/certificate-name/', {'learner_name': 'Other Name'}).status_code, 401)

        self.client.force_authenticate(self.author)
        self.assertEqual(self.client.get('/api/my/certificate-name/').status_code, 403)
        self.assertEqual(self.client.put('/api/my/certificate-name/', {'learner_name': 'Other Name'}).status_code, 403)

        self.client.force_authenticate(self.other)
        me = self.client.get('/api/auth/me/')
        self.assertEqual(me.status_code, 200)
        self.assertNotIn('certificate_name', me.data)
        self.assertNotIn('certificate_name_confirmed_at', me.data)
        response = self.client.put('/api/my/certificate-name/', {'learner_name': 'Other Student'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.other.refresh_from_db()
        self.student.refresh_from_db()
        self.assertEqual(self.other.certificate_name, 'Other Student')
        self.assertEqual(self.student.certificate_name, 'Айгерім Әбілова')

    def test_admin_issue_api_rejects_certificate_name_override(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post('/api/certificates/admin/issue/', {
            'student_id': self.student.pk, 'course_id': self.course.pk,
            'learner_name': 'Administrator Override', 'confirmation': True,
        }, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Certificate.objects.exists())

    def test_admin_issue_api_snapshots_only_the_confirmed_student_name(self):
        self.student.certificate_name = 'Әлия Қасымқызы'
        self.student.certificate_name_confirmed_at = timezone.now()
        self.student.save(update_fields=['certificate_name', 'certificate_name_confirmed_at'])
        self.client.force_authenticate(self.admin)
        response = self.client.post('/api/certificates/admin/issue/', {
            'student_id': self.student.pk, 'course_id': self.course.pk, 'confirmation': True,
        }, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data['learner_name'], 'Әлия Қасымқызы')
