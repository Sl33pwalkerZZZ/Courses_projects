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
from .services import eligibility, issue_certificate, revoke_certificate


@override_settings(CERTIFICATES_ENABLED=True)
class CertificateTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(username='administrator', role='admin')
        self.author = User.objects.create_user(username='author', role='author')
        self.student = User.objects.create_user(username='student', first_name='Айгерім', last_name='Әбілова')
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
        return issue_certificate(administrator=self.admin, student=self.student, course_id=self.course.pk, learner_name=self.student.get_full_name())

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

    def test_name_must_match_profile_and_issuer_approved(self):
        with self.assertRaises(ValidationError):
            issue_certificate(administrator=self.admin,student=self.student,course_id=self.course.pk,learner_name='Different Name')
        self.policy.issuer_approved = False
        self.policy.save()
        self.assertFalse(eligibility(self.student,self.course)['eligible'])

    @override_settings(CERTIFICATES_ENABLED=False)
    def test_disabled_feature_has_no_certificate_queries(self):
        self.client.force_authenticate(self.student)
        with self.assertNumQueries(0):
            self.assertEqual(self.client.get('/api/my/certificates/').status_code,404)
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
                issue_certificate(administrator=self.admin,student=self.student,course_id=self.course.pk,learner_name=name)
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

    def test_owner_download_requires_trusted_origin(self):
        certificate,_=self.issue()
        self.client.force_authenticate(self.student)
        with self.settings(CERTIFICATE_PUBLIC_ORIGIN=''):
            self.assertEqual(self.client.get(f'/api/certificates/{certificate.verification_code}/download/').status_code,403)

    def test_wrong_reviewer_cannot_establish_evidence(self):
        self.submission.review_history[-1]['reviewer_id']=self.other.pk
        self.submission.save()
        self.assertFalse(eligibility(self.student,self.course)['eligible'])
