"""Final-project authoring contract on disposable fixtures only."""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from courses.models import Course, Direction, Module, Lesson, Assignment
from progress.models import AssignmentSubmission


class AssignmentAuthoringTests(TestCase):
    def setUp(self):
        users = get_user_model()
        self.author = users.objects.create_user(username='assignment-owner', role='author')
        self.student = users.objects.create_user(username='assignment-student')
        self.other = users.objects.create_user(username='assignment-other', role='author')
        direction = Direction.objects.create(name='Test', slug='assignment-authoring')
        self.course = Course.objects.create(title='Draft fixture', slug='assignment-authoring', author=self.author, direction=direction)
        module = Module.objects.create(course=self.course, title='Module', order=1)
        self.lesson = Lesson.objects.create(module=module, title='Lesson', order=1, text_content='Fixture lesson')
        self.url = f'/api/studio/lessons/{self.lesson.pk}/assignments/'
        self.payload = {'description': 'Original title\n\nInstructions with paragraphs.\nSecond line.', 'type': 'text', 'learning_activity': 'final_media_project'}
        self.client = APIClient()
        self.client.force_authenticate(self.author)

    def create(self, **updates):
        return self.client.post(self.url, {**self.payload, **updates}, format='json')

    def test_create_edit_reopen_and_student_preview_exact_instructions(self):
        created = self.create()
        self.assertEqual(created.status_code, 201, created.data)
        pk = created.data['id']
        self.assertEqual(created.data['description'], self.payload['description'])
        text = 'Edited title\n\nVerify rights and document your decisions.\nKeep this line break.'
        result = self.client.patch(f'/api/studio/assignments/{pk}/', {'description': text, 'type': 'file'}, format='json')
        self.assertEqual(result.status_code, 200, result.data)
        reopened = self.client.get(self.url).data[0]
        self.assertEqual(reopened['description'], text)
        self.assertEqual(reopened['learning_activity'], 'final_media_project')
        self.assertEqual(reopened['type'], 'file')
        preview = self.client.get(f'/api/lessons/{self.lesson.pk}/').data['assignments'][0]
        self.assertEqual(preview, reopened)
        self.assertFalse(self.course.is_published)

    def test_final_text_and_file_are_supported_but_not_quiz(self):
        for kind in ['text', 'file']:
            self.assertEqual(self.create(type=kind).status_code, 201)
        self.assertEqual(self.create(type='quiz').status_code, 400)
        self.assertEqual(Assignment.objects.count(), 2)

    def test_invalid_activity_empty_description_and_selection_map_file_reject(self):
        for data in [{'learning_activity': 'invented'}, {'description': '  \n '}, {'type': 'file', 'learning_activity': 'ai_selection_map'}, {'type': 'both'}]:
            self.assertEqual(self.create(**data).status_code, 400)
        self.assertFalse(Assignment.objects.exists())
        self.assertEqual(self.create(learning_activity='ai_selection_map').status_code, 201)
        self.assertEqual(self.create(learning_activity='').status_code, 201)

    def test_existing_submissions_reviews_and_instructions_are_immutable(self):
        assignment = Assignment.objects.create(lesson=self.lesson, **self.payload)
        submission = AssignmentSubmission.objects.create(assignment=assignment, student=self.student, content='Historical fixture work', status='approved', reviewer_comment='Historical feedback', review_history=[{'status': 'approved', 'rubric_scores': {'completeness': 25, 'application': 20, 'quality': 21, 'documentation': 22}}])
        before = AssignmentSubmission.objects.values().get(pk=submission.pk)
        result = self.client.patch(f'/api/studio/assignments/{assignment.pk}/', {'description': 'Changed', 'learning_activity': ''}, format='json')
        self.assertEqual(result.status_code, 400)
        assignment.refresh_from_db()
        self.assertEqual(assignment.description, self.payload['description'])
        self.assertEqual(AssignmentSubmission.objects.values().get(pk=submission.pk), before)

    def test_authorization_and_published_course_lock(self):
        for user, code in [(None, 401), (self.student, 403), (self.other, 404)]:
            self.client.force_authenticate(user)
            self.assertEqual(self.create().status_code, code)
        self.client.force_authenticate(self.author)
        self.course.is_published = True
        self.course.save()
        self.assertEqual(self.create().status_code, 400)
        self.assertFalse(Assignment.objects.exists())
