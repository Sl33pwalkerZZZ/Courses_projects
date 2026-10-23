"""Isolated review lifecycle and certificate-evidence regressions."""
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory
from django.urls import reverse
from rest_framework.test import APITestCase

from certificates.services import approved_submission
from courses.models import Assignment, Course, Direction, Lesson, Module
from progress.models import AssignmentSubmission, Enrollment
from progress.test_selection_maps import complete_map
from progress.services import review_assignment_submission
from unittest.mock import patch


class AssignmentReviewWorkflowTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        users = get_user_model()
        cls.owner = users.objects.create_user(username='review-owner', role='author', is_staff=True)
        cls.other = users.objects.create_user(username='review-other', role='author')
        cls.student = users.objects.create_user(username='review-student')
        cls.administrator = users.objects.create_superuser(username='review-admin', password='test')
        direction = Direction.objects.create(name='Review', slug='review')
        cls.course = Course.objects.create(title='Review', slug='review', description='Read', direction=direction, author=cls.owner, is_published=True)
        module = Module.objects.create(course=cls.course, title='Module', order=1)
        cls.lesson = Lesson.objects.create(module=module, title='Lesson', text_content='Read', order=1)
        cls.assignment = Assignment.objects.create(lesson=cls.lesson, description='Practice', type='text', learning_activity='ai_selection_map')
        Enrollment.objects.create(course=cls.course, student=cls.student)

    def create_submission(self, student=None, status='pending'):
        return AssignmentSubmission.objects.create(assignment=self.assignment, student=student or self.student, status=status, is_structured=True)

    def review(self, submission, status='approved', revision=0, comment=''):
        return self.client.post(f'/api/studio/submissions/{submission.pk}/review/', {'revision': revision, 'status': status, 'reviewer_comment': comment}, format='json')

    def test_ownership_is_rechecked_after_course_lock(self):
        submission = self.create_submission()
        # Simulate an ownership reassignment between the initial read and lock.
        with patch('progress.services.Course.objects.select_for_update') as locked:
            locked.return_value.get.return_value = Course(pk=self.course.pk, author=self.other)
            with self.assertRaises(PermissionDenied):
                review_assignment_submission(submission_id=submission.pk, reviewer=self.owner,
                                             revision=0, status='approved', comment='Review')
        submission.refresh_from_db()
        self.assertEqual(submission.status, 'pending')
        self.assertEqual(submission.review_history, [])

    def test_draft_reopen_submit_approve_and_verifiable_evidence(self):
        self.client.force_authenticate(self.student)
        draft_url = reverse('selection-map', args=[self.assignment.pk])
        result = self.client.put(draft_url, {'revision': 0, 'payload': {'working_task': 'Draft task'}}, format='json')
        self.assertEqual(result.status_code, 200, result.data)
        self.assertEqual(self.client.get(draft_url).data['payload']['working_task'], 'Draft task')
        self.client.force_authenticate(self.owner)
        self.assertEqual(self.client.get('/api/studio/submissions/').data, [])
        self.client.force_authenticate(self.student)
        result = self.client.post(reverse('selection-map-submit', args=[self.assignment.pk]), {'revision': 1, 'payload': complete_map()}, format='json')
        self.assertEqual(result.status_code, 200, result.data)
        submission = AssignmentSubmission.objects.get(pk=result.data['id'])
        self.client.force_authenticate(self.owner)
        listing = self.client.get('/api/studio/submissions/').data
        self.assertEqual(listing[0]['course_id'], self.course.pk)
        self.assertTrue(listing[0]['can_review'])
        decision = self.review(submission, revision=2, comment='Good evidence')
        self.assertEqual(decision.status_code, 200, decision.data)
        self.assertEqual(approved_submission(self.student, self.assignment).pk, submission.pk)
        submission.refresh_from_db()
        self.assertEqual(submission.review_history[-1]['reviewer_id'], self.owner.pk)
        self.assertEqual(submission.review_history[-1]['revision'], submission.revision)
        self.assertEqual(submission.review_history[-1]['reviewed_at'], submission.reviewed_at.isoformat())
        self.assertEqual(self.review(submission, revision=3).status_code, 400)
        self.client.force_authenticate(self.student)
        reopened = self.client.get(draft_url).data
        self.assertEqual(reopened['status'], 'approved')
        self.assertEqual(reopened['reviewer_comment'], 'Good evidence')

    def test_permissions_other_teacher_student_admin_and_no_self_review(self):
        submission = self.create_submission()
        self.client.force_authenticate(self.student)
        self.assertEqual(self.client.get('/api/studio/submissions/').status_code, 403)
        self.assertEqual(self.review(submission).status_code, 403)
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get('/api/studio/submissions/').data, [])
        self.assertEqual(self.review(submission).status_code, 404)
        self.client.force_authenticate(self.administrator)
        self.assertEqual(self.review(submission).status_code, 200)
        for reviewer in (self.owner, self.administrator):
            own = self.create_submission(student=reviewer)
            self.client.force_authenticate(reviewer)
            self.assertEqual(self.review(own).status_code, 403)
            own.refresh_from_db()
            self.assertEqual(own.status, 'pending')
            self.assertEqual(own.review_history, [])

    def test_rejection_feedback_revision_and_reapplication(self):
        submission = self.create_submission()
        self.client.force_authenticate(self.owner)
        self.assertEqual(self.review(submission, revision=99).status_code, 409)
        self.assertEqual(self.review(submission, status='rejected').status_code, 400)
        result = self.review(submission, status='rejected', comment='Add comparison evidence')
        self.assertEqual(result.status_code, 200)
        self.assertIsNone(approved_submission(self.student, self.assignment))
        self.client.force_authenticate(self.student)
        result = self.client.post(reverse('selection-map-submit', args=[self.assignment.pk]), {'revision': 1, 'payload': complete_map()}, format='json')
        self.assertEqual(result.status_code, 200, result.data)
        self.assertEqual(len(result.data['review_history']), 1)
        self.client.force_authenticate(self.owner)
        self.assertEqual(self.review(submission, revision=2).status_code, 200)
        self.assertIsNotNone(approved_submission(self.student, self.assignment))

    def test_historical_approval_is_not_certificate_evidence(self):
        from django.utils import timezone
        submission = self.create_submission(status='approved')
        submission.reviewed_at = timezone.now()
        submission.save()
        self.assertIsNone(approved_submission(self.student, self.assignment))
        self.client.force_authenticate(self.owner)
        result = self.client.get('/api/studio/submissions/')
        self.assertFalse(result.data[0]['review_is_verifiable'])

    def test_admin_is_readonly_ownership_scoped_and_drafts_private(self):
        submission = self.create_submission()
        model_admin = admin.site._registry[AssignmentSubmission]
        request = RequestFactory().get('/admin/')
        request.user = self.owner
        self.assertTrue(model_admin.has_view_permission(request, submission))
        self.assertFalse(model_admin.has_add_permission(request))
        self.assertFalse(model_admin.has_change_permission(request, submission))
        self.assertFalse(model_admin.has_delete_permission(request, submission))
        request.user = self.student
        self.assertFalse(model_admin.has_view_permission(request, submission))
        request.user = self.other
        self.assertFalse(model_admin.has_view_permission(request, submission))
        self.assertFalse(model_admin.get_queryset(request).exists())
