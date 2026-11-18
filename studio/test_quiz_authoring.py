"""Quiz authoring round-trip and historical-result safety on disposable data."""
from copy import deepcopy
from uuid import uuid4
from django.test import TestCase
from progress.models import Enrollment
from quizzes.models import Quiz
from . import tests as studio_fixtures


class QuizAuthoringTests(TestCase):
    setUp = studio_fixtures.StudioTests.setUp
    url = studio_fixtures.StudioTests.url

    def test_round_trip_grading_privacy_and_attempt_lock(self):
        path = self.url(f'lessons/{self.lesson.pk}/quiz/')
        self.assertEqual(self.client.put(path, self.quiz_payload, format='json').status_code, 200)
        edited = deepcopy(self.client.get(path).data)
        edited['passing_percentage'] = 85
        edited['questions'][0]['text'] = 'Edited question?'
        edited['questions'][0]['explanation'] = 'Edited explanation'
        edited['questions'][0]['choices'][0]['is_correct'] = False
        edited['questions'][0]['choices'][1]['is_correct'] = True
        saved = self.client.put(path, edited, format='json')
        self.assertEqual(saved.status_code, 200, saved.data)
        reopened = self.client.get(path).data
        self.assertEqual(reopened, saved.data)
        self.assertEqual(reopened['passing_percentage'], 85)
        self.assertEqual(reopened['questions'][0]['text'], 'Edited question?')
        self.assertEqual([c['is_correct'] for c in reopened['questions'][0]['choices']], [False, True])
        bad = deepcopy(edited)
        bad['passing_percentage'] = 85.5
        self.assertEqual(self.client.put(path, bad, format='json').status_code, 400)
        self.assertEqual(self.client.get(path).data, reopened)
        quiz = Quiz.objects.get(lesson=self.lesson)
        quiz.is_published = True
        quiz.save()
        Enrollment.objects.create(student=self.student, course=self.course)
        self.client.force_authenticate(self.student)
        student_path = f'/api/lessons/{self.lesson.pk}/quiz/'
        public = self.client.get(student_path).data['quiz']
        self.assertNotIn('explanation', public['questions'][0])
        self.assertTrue(all('is_correct' not in c for c in public['questions'][0]['choices']))
        question = reopened['questions'][0]
        attempts_path = student_path + 'attempts/'
        def submit(choice):
            return self.client.post(attempts_path, {'submission_id': str(uuid4()), 'answers': [{'question_id': question['id'], 'choice_ids': [choice['id']]}]}, format='json')
        wrong = submit(question['choices'][0])
        right = submit(question['choices'][1])
        self.assertEqual(wrong.status_code, 201, wrong.data)
        self.assertEqual((wrong.data['score'], wrong.data['passed']), (0, False))
        self.assertEqual((right.data['score'], right.data['passed'], right.data['passing_percentage']), (100, True, 85))
        self.assertEqual(right.data['answers'][0]['correct_choice_ids'], [question['choices'][1]['id']])
        frozen = list(quiz.attempts.values())
        answers = list(quiz.attempts.get(pk=right.data['id']).answers.values())
        # Even an unpublished quiz remains locked after attempts exist.
        quiz.is_published = False
        quiz.save()
        self.client.force_authenticate(self.author)
        self.assertTrue(self.client.get(path).data['locked'])
        self.assertEqual(self.client.put(path, edited, format='json').status_code, 400)
        self.assertEqual(list(quiz.attempts.values()), frozen)
        self.assertEqual(list(quiz.attempts.get(pk=right.data['id']).answers.values()), answers)
