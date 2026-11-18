"""Publication rehearsal uses synthetic records in the isolated test database."""
from django.test import TestCase
from courses.models import CourseImport
from . import tests as fixtures


class PublicationReadinessTests(TestCase):
    setUp = fixtures.StudioTests.setUp
    url = fixtures.StudioTests.url
    make_quiz = fixtures.StudioTests.make_quiz

    def test_blocker_preview_request_and_moderation(self):
        path = self.url(f'courses/{self.course.pk}/publication/')
        original_keys = {'title','description','curriculum','lesson_content','assessment','source_reviewed','assessment_reviewed'}
        status = self.client.get(path).data
        self.assertEqual({x['key'] for x in status['requirements']}, original_keys)
        self.assertFalse(next(x['met'] for x in status['requirements'] if x['key']=='assessment'))
        self.make_quiz()
        self.lesson.text_content = ''
        self.lesson.save()
        self.assertFalse(next(x['met'] for x in self.client.get(path).data['requirements'] if x['key']=='lesson_content'))
        self.client.patch(self.url(f'lessons/{self.lesson.pk}/'), {'text_content':'Verified fixture lesson text'}, format='json')
        preview = self.client.get(f'/api/instructor/courses/{self.course.slug}/preview/')
        self.assertEqual(preview.status_code, 200, preview.data)
        self.assertEqual(preview.data['modules'][0]['lessons'][0]['title'], self.lesson.title)
        self.assertFalse(self.course.enrollments.exists())
        CourseImport.objects.create(course=self.course,source_name='fixture.docx',source_sha256='d'*64,manifest_sha256='e'*64,content_sha256='f'*64,version='v1')
        self.assertEqual(self.client.post(path,{},format='json').status_code,400)
        response=self.client.post(path,{'source_reviewed':True,'assessment_reviewed':True},format='json')
        self.assertEqual(response.status_code,201,response.data)
        self.course.refresh_from_db()
        self.assertFalse(self.course.is_published)
        self.assertEqual(self.client.post(path,{'source_reviewed':True,'assessment_reviewed':True},format='json').status_code,400)
        decision=self.url(f"reviews/{response.data['id']}/decision/")
        self.assertEqual(self.client.post(decision,{'decision':'approve'},format='json').status_code,403)
        self.client.force_authenticate(self.admin)
        self.assertEqual(self.client.post(decision,{'decision':'approve'},format='json').status_code,200)
        self.assertTrue(self.client.get(path).data['is_published'])
        self.course.refresh_from_db()
        self.assertTrue(self.course.is_published)
