"""Studio changes only disposable TestCase databases, never development records."""
from io import BytesIO
import zipfile
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from courses.models import Assignment, Course, CourseImport, Direction, Lesson, Module
from progress.models import AssignmentSubmission, Enrollment, LessonProgress
from quizzes.models import Quiz, QuizAttempt
from .models import ImportPreview, PublicationRequest, PublicationEvent


def document():
    data = BytesIO()
    with zipfile.ZipFile(data, 'w') as archive:
        archive.writestr('[Content_Types].xml', '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
        archive.writestr('word/document.xml', '''<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>Source course</w:t></w:r></w:p><w:p><w:pPr><w:pStyle w:val="Heading2"/></w:pPr><w:r><w:t>Lesson one</w:t></w:r></w:p><w:p><w:r><w:t>Source paragraph https://example.com</w:t></w:r></w:p></w:body></w:document>''')
    return SimpleUploadedFile('source.docx', data.getvalue(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')


class StudioTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.author = User.objects.create_user(username='author', role='author')
        self.other = User.objects.create_user(username='other', role='author')
        self.student = User.objects.create_user(username='student')
        self.admin = User.objects.create_superuser(username='admin', password='not-used')
        self.direction = Direction.objects.create(name='AI', slug='ai')
        self.course = Course.objects.create(title='Private', slug='private', description='Details', direction=self.direction, author=self.author)
        self.module = Module.objects.create(course=self.course, title='One', order=1)
        self.lesson = Lesson.objects.create(module=self.module, title='Lesson', text_content='Educational content', order=1)
        self.client = APIClient()
        self.client.force_authenticate(self.author)
        self.quiz_payload = {'title': 'Quiz', 'instructions': 'Choose', 'passing_percentage': 70, 'questions': [{'text': 'Question?', 'type': 'single', 'explanation': 'Why', 'choices': [{'text': 'A', 'is_correct': True}, {'text': 'B', 'is_correct': False}]}]}

    def url(self, suffix):
        return '/api/studio/' + suffix

    def make_quiz(self):
        response = self.client.put(self.url(f'lessons/{self.lesson.pk}/quiz/'), self.quiz_payload, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        return Quiz.objects.get(lesson=self.lesson)

    def request_publication(self):
        return self.client.post(self.url(f'courses/{self.course.pk}/publication/'), {'source_reviewed': True, 'assessment_reviewed': True}, format='json')

    def test_roles_and_owner_isolation(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get(self.url('courses/')).status_code, 401)
        self.client.force_authenticate(self.student)
        self.assertEqual(self.client.get(self.url('courses/')).status_code, 403)
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get(self.url('courses/')).data, [])
        self.assertEqual(self.client.get(self.url(f'courses/{self.course.pk}/')).status_code, 404)
        self.assertEqual(self.client.patch(self.url(f'lessons/{self.lesson.pk}/'), {'title': 'Stolen'}).status_code, 404)
        self.assertEqual(self.client.get(self.url(f'lessons/{self.lesson.pk}/quiz/')).status_code, 404)
        self.client.force_authenticate(self.author)
        self.assertEqual(self.client.get(self.url('reviews/')).status_code, 403)

    def test_role_admin_without_real_staff_permission_is_denied(self):
        self.student.role = 'admin'
        self.student.save()
        self.client.force_authenticate(self.student)
        self.assertEqual(self.client.get(self.url('reviews/')).status_code, 403)
        self.assertEqual(self.client.get(self.url('courses/')).status_code, 403)

    def test_create_patch_unique_slug_and_no_publish_mass_assignment(self):
        payload = {'title': 'New Course', 'description': 'Description', 'direction': self.direction.pk, 'level': 'beginner', 'enrollment_mode': 'approval', 'language': 'kk'}
        first = self.client.post(self.url('courses/'), payload, format='json')
        second = self.client.post(self.url('courses/'), payload, format='json')
        self.assertEqual(first.status_code, 201, first.data)
        self.assertNotEqual(first.data['slug'], second.data['slug'])
        self.assertEqual(first.data['language'], 'kk')
        self.assertFalse(first.data['is_published'])
        path = self.url(f"courses/{first.data['id']}/")
        self.assertEqual(self.client.patch(path, {'title': 'Edited'}, format='json').status_code, 200)
        self.assertEqual(self.client.patch(path, {'is_published': True}, format='json').status_code, 400)
        self.assertEqual(self.client.patch(path, {'author': self.other.pk}, format='json').status_code, 400)
        self.assertEqual(self.client.get('/api/courses/').data, [])

    def test_curriculum_add_edit_and_reorder(self):
        module = self.client.post(self.url(f'courses/{self.course.pk}/modules/'), {'title': 'Two'}, format='json')
        self.assertEqual(module.status_code, 201)
        created = self.client.post(self.url(f"modules/{module.data['id']}/lessons/"), {'title': 'Two', 'text_content': 'Body'}, format='json')
        self.assertEqual(created.status_code, 201, created.data)
        self.assertEqual(self.client.patch(self.url(f"lessons/{created.data['id']}/"), {'title': 'Revised'}, format='json').status_code, 200)
        ids = [module.data['id'], self.module.pk]
        self.assertEqual(self.client.post(self.url(f'courses/{self.course.pk}/reorder/'), {'ids': ids}, format='json').status_code, 200)
        self.module.refresh_from_db()
        self.assertEqual(self.module.order, 2)
        for bad in ([self.module.pk], [self.module.pk, self.module.pk], [True, module.data['id']]):
            self.assertEqual(self.client.post(self.url(f'courses/{self.course.pk}/reorder/'), {'ids': bad}, format='json').status_code, 400)
        lesson = self.client.post(self.url(f'modules/{self.module.pk}/lessons/'), {'title': 'Second', 'text_content': 'Body'}, format='json')
        self.assertEqual(self.client.post(self.url(f'modules/{self.module.pk}/reorder/'), {'ids': [lesson.data['id'], self.lesson.pk]}, format='json').status_code, 200)

    def test_learning_content_rejects_shapes_that_crash_react(self):
        path = self.url(f'lessons/{self.lesson.pk}/')
        invalid = [{'type': 'categories', 'items': {'title': 'Object not list'}}, {'type': 'model_service', 'rows': ['bad']}, {'type': 'categories', 'items': [{'title': {'bad': 'object'}}]}, {'type': 'script', 'text': 'alert(1)'}]
        for interaction in invalid:
            result = self.client.patch(path, {'learning_content': {'content_language': 'ru', 'interactions': [interaction]}}, format='json')
            self.assertEqual(result.status_code, 400, result.data)
        valid = {'content_language': 'ru', 'objectives': ['Read'], 'interactions': [{'type': 'model_service', 'title': 'Compare', 'headers': ['A'], 'rows': [['Text']]}]}
        self.assertEqual(self.client.patch(path, {'learning_content': valid}, format='json').status_code, 200)

    def test_author_preview_only_own_and_no_enrollment_created(self):
        self.assertEqual(self.client.get('/api/instructor/courses/private/preview/').status_code, 200)
        self.assertEqual(self.client.get(f'/api/lessons/{self.lesson.pk}/').status_code, 200)
        self.assertFalse(Enrollment.objects.exists())
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get('/api/instructor/courses/private/preview/').status_code, 403)
        self.assertEqual(self.client.get(f'/api/lessons/{self.lesson.pk}/').status_code, 403)

    def test_quiz_validation_and_draft_keys_not_public(self):
        self.make_quiz()
        path = self.url(f'lessons/{self.lesson.pk}/quiz/')
        bad = dict(self.quiz_payload, passing_percentage=101)
        self.assertEqual(self.client.put(path, bad, format='json').status_code, 400)
        bad = dict(self.quiz_payload, questions=[{'text': 'Bad', 'type': 'single', 'choices': [{'text': 'A', 'is_correct': False}, {'text': 'B', 'is_correct': False}]}])
        self.assertEqual(self.client.put(path, bad, format='json').status_code, 400)
        self.client.force_authenticate(self.student)
        self.assertEqual(self.client.get(path).status_code, 403)
        self.assertEqual(Quiz.objects.get(lesson=self.lesson).questions.count(), 1)

    def test_assessed_or_published_quiz_cannot_be_rewritten(self):
        quiz = self.make_quiz()
        QuizAttempt.objects.create(quiz=quiz, student=self.student, request_digest='a'*64, score=100, correct_count=1, question_count=1, passing_percentage=70, passed=True)
        self.assertEqual(self.client.put(self.url(f'lessons/{self.lesson.pk}/quiz/'), self.quiz_payload, format='json').status_code, 400)
        quiz.attempts.all().delete()
        quiz.is_published = True
        quiz.save()
        self.assertEqual(self.client.put(self.url(f'lessons/{self.lesson.pk}/quiz/'), self.quiz_payload, format='json').status_code, 400)

    def test_publication_review_preserves_import_guard_then_publishes(self):
        self.make_quiz()
        imported = CourseImport.objects.create(course=self.course, source_name='word.docx', source_sha256='a'*64, manifest_sha256='b'*64, content_sha256='c'*64, version='v1')
        response = self.request_publication()
        self.assertEqual(response.status_code, 201, response.data)
        imported.refresh_from_db()
        self.assertFalse(imported.review_approved)
        self.course.refresh_from_db()
        self.assertFalse(self.course.is_published)
        self.assertEqual(self.request_publication().status_code, 400)
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.post(self.url(f"reviews/{response.data['id']}/decision/"), {'decision': 'approve'}, format='json').status_code, 403)
        self.client.force_authenticate(self.admin)
        result = self.client.post(self.url(f"reviews/{response.data['id']}/decision/"), {'decision': 'approve'}, format='json')
        self.assertEqual(result.status_code, 200, result.data)
        self.course.refresh_from_db(); imported.refresh_from_db()
        self.assertTrue(self.course.is_published)
        self.assertTrue(imported.review_approved)
        self.assertTrue(Quiz.objects.get(lesson=self.lesson).is_published)
        self.assertEqual(PublicationEvent.objects.count(), 2)
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get('/api/courses/').data[0]['id'], self.course.pk)
        self.client.force_authenticate(self.author)
        self.assertEqual(self.client.patch(self.url(f'lessons/{self.lesson.pk}/'), {'title': 'Changed'}, format='json').status_code, 400)

    def test_publication_missing_acknowledgments_and_stale_content(self):
        self.make_quiz()
        self.assertEqual(self.client.post(self.url(f'courses/{self.course.pk}/publication/'), {}, format='json').status_code, 400)
        response = self.request_publication()
        self.assertEqual(response.status_code, 201)
        self.client.patch(self.url(f'lessons/{self.lesson.pk}/'), {'title': 'Edited after request'}, format='json')
        self.client.force_authenticate(self.admin)
        result = self.client.post(self.url(f"reviews/{response.data['id']}/decision/"), {'decision': 'approve'}, format='json')
        self.assertEqual(result.status_code, 400, result.data)
        self.assertEqual(self.client.post(self.url(f"reviews/{response.data['id']}/decision/"), {'decision': 'reject'}, format='json').status_code, 400)
        result = self.client.post(self.url(f"reviews/{response.data['id']}/decision/"), {'decision': 'reject', 'note': 'Please review again'}, format='json')
        self.assertEqual(result.status_code, 200)
        self.client.force_authenticate(self.author)
        self.assertEqual(self.request_publication().status_code, 201)

    def test_submission_ownership_draft_privacy_and_review_revision(self):
        assignment = Assignment.objects.create(lesson=self.lesson, type='text', description='Map', learning_activity='ai_selection_map')
        draft = AssignmentSubmission.objects.create(assignment=assignment, student=self.student, status='draft', is_structured=True)
        listing = self.url(f'courses/{self.course.pk}/submissions/')
        self.assertEqual(self.client.get(listing).data, [])
        draft.status = 'pending'; draft.save()
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get(listing).status_code, 404)
        self.assertEqual(self.client.post(self.url(f'submissions/{draft.pk}/review/'), {'revision': 0, 'status': 'approved'}, format='json').status_code, 404)
        self.client.force_authenticate(self.author)
        self.assertEqual(len(self.client.get(listing).data), 1)
        path = self.url(f'submissions/{draft.pk}/review/')
        self.assertEqual(self.client.post(path, {'revision': 2, 'status': 'approved'}, format='json').status_code, 409)
        self.assertEqual(self.client.post(path, {'revision': 0, 'status': 'rejected'}, format='json').status_code, 400)
        result = self.client.post(path, {'revision': 0, 'status': 'rejected', 'reviewer_comment': 'Compare criteria'}, format='json')
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.data['revision'], 1)
        self.assertEqual(len(result.data['review_history']), 1)
        self.assertFalse(LessonProgress.objects.exists())
        self.assertEqual(self.client.post(path, {'revision': 1, 'status': 'approved'}, format='json').status_code, 400)

    def test_no_privilege_self_escalation(self):
        path = self.url(f'instructors/{self.student.pk}/')
        self.assertEqual(self.client.post(path, {'role': 'author'}, format='json').status_code, 403)
        self.client.force_authenticate(self.admin)
        self.assertEqual(self.client.post(path, {'role': 'admin'}, format='json').status_code, 400)
        self.assertEqual(self.client.post(path, {'role': 'author'}, format='json').status_code, 200)
        self.student.refresh_from_db()
        self.assertEqual(self.student.role, 'author')
        self.assertFalse(self.student.is_staff)
        self.assertFalse(self.student.is_superuser)

    def test_docx_preview_no_database_writes_explicit_confirm_idempotent(self):
        before = Course.objects.count()
        response = self.client.post(self.url('imports/preview/'), {'file': document()}, format='multipart')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(Course.objects.count(), before)
        self.assertEqual(ImportPreview.objects.count(), 0)
        payload = {'title': 'Word', 'description': 'Document', 'direction': self.direction.pk, 'level': 'beginner', 'language': 'ru', 'enrollment_mode': 'approval',
                   'preview_token': response.data['preview_token'], 'lessons': [{'title': lesson['title'], 'text_content': lesson['text_content']} for lesson in response.data['parsed']['lessons']]}
        path = self.url(f"imports/{response.data['id']}/confirm/")
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.post(path, payload, format='json').status_code, 400)
        self.client.force_authenticate(self.author)
        result = self.client.post(path, payload, format='json')
        self.assertEqual(result.status_code, 201, result.data)
        self.assertFalse(result.data['is_published'])
        repeated = self.client.post(path, payload, format='json')
        self.assertEqual(repeated.status_code, 200)
        self.assertEqual(repeated.data['id'], result.data['id'])
        self.assertEqual(Course.objects.count(), before + 1)
        self.assertEqual(CourseImport.objects.count(), 1)
        self.assertFalse(CourseImport.objects.get().review_approved)
        # A separate preview of same source must not duplicate existing import.
        second = self.client.post(self.url('imports/preview/'), {'file': document()}, format='multipart')
        payload['preview_token'] = second.data['preview_token']
        self.assertEqual(self.client.post(self.url(f"imports/{second.data['id']}/confirm/"), payload, format='json').status_code, 400)
        self.assertEqual(Course.objects.count(), before + 1)

    def test_docx_invalid_confirm_rolls_back_and_existing_records_unchanged(self):
        snapshot = list(Course.objects.values())
        response = self.client.post(self.url('imports/preview/'), {'file': document()}, format='multipart')
        path = self.url(f"imports/{response.data['id']}/confirm/")
        result = self.client.post(path, {'preview_token': response.data['preview_token'], 'title': 'Bad'}, format='json')
        self.assertEqual(result.status_code, 400)
        self.assertEqual(list(Course.objects.values()), snapshot)
        self.assertEqual(ImportPreview.objects.count(), 0)
        self.assertEqual(self.client.post(self.url('imports/preview/'), {'file': SimpleUploadedFile('bad.docx', b'notzip')}, format='multipart').status_code, 400)

    @override_settings(MEDIA_ROOT='/tmp/studio-test-media-only')
    def test_images_private_and_accessible_descriptions(self):
        import shutil
        from PIL import Image
        data = BytesIO(); Image.new('RGB', (2, 2), 'blue').save(data, format='PNG')
        self.addCleanup(shutil.rmtree, '/tmp/studio-test-media-only', True)
        response = self.client.post(self.url(f'lessons/{self.lesson.pk}/images/'), {'image': SimpleUploadedFile('a.png', data.getvalue()), 'alt_text': '{"ru":"Схема"}'}, format='multipart')
        self.assertEqual(response.status_code, 201, response.data)
        url = response.data['image']
        student_lesson = self.client.get(f'/api/lessons/{self.lesson.pk}/')
        self.assertEqual(student_lesson.data['images'][0]['alt_text'], {'ru': 'Схема'})
        self.assertEqual(self.client.get(url).status_code, 200)
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get(url).status_code, 403)
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get(url).status_code, 401)

    def test_no_delete_endpoints(self):
        self.assertEqual(self.client.delete(self.url(f'courses/{self.course.pk}/')).status_code, 405)
        self.assertEqual(self.client.delete(self.url(f'lessons/{self.lesson.pk}/')).status_code, 405)
        self.assertTrue(Course.objects.filter(pk=self.course.pk).exists())
