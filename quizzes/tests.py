import uuid
from unittest.mock import patch

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, transaction
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework.test import APITestCase

from courses.models import Course, Direction, Lesson, Module
from progress.models import Enrollment, EnrollmentRequest, LessonProgress
from progress.services import review_enrollment_request

from .models import Quiz, QuizAnswer, QuizAttempt, QuizChoice, QuizQuestion


class QuizTests(APITestCase):
    """All curriculum and quiz fixtures are confined to Django's test database."""

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.student = User.objects.create_user(username="quiz-student")
        cls.other = User.objects.create_user(username="quiz-other")
        cls.pending = User.objects.create_user(username="quiz-pending")
        cls.rejected = User.objects.create_user(username="quiz-rejected")
        cls.staff = User.objects.create_user(username="quiz-staff", is_staff=True)
        cls.admin = User.objects.create_superuser(username="quiz-admin", password="test-password")
        direction = Direction.objects.create(name="Quiz test", slug="quiz-test")
        cls.course = Course.objects.create(
            title="Test curriculum", slug="quiz-curriculum", description="Protected curriculum",
            direction=direction, author=cls.admin, is_published=True,
        )
        cls.module = Module.objects.create(course=cls.course, title="Test module", order=1)
        cls.lesson = Lesson.objects.create(module=cls.module, title="Existing lesson", text_content="Read this", order=1)
        cls.no_quiz_lesson = Lesson.objects.create(module=cls.module, title="No quiz", text_content="Read this too", order=2)
        cls.enrollment = Enrollment.objects.create(student=cls.student, course=cls.course)
        Enrollment.objects.create(student=cls.other, course=cls.course)
        cls.quiz = Quiz.objects.create(lesson=cls.lesson, title="Knowledge check", instructions="Choose carefully", passing_percentage=50)
        cls.single = QuizQuestion.objects.create(quiz=cls.quiz, text="Single question", type="single", order=1, explanation="Single explanation")
        cls.multi = QuizQuestion.objects.create(quiz=cls.quiz, text="Multiple question", type="multiple", order=2, explanation="Multiple explanation")
        cls.single_choices = [QuizChoice.objects.create(question=cls.single, text=f"Single {i}", order=i, is_correct=i == 1) for i in range(3)]
        cls.multi_choices = [QuizChoice.objects.create(question=cls.multi, text=f"Multiple {i}", order=i, is_correct=i in (0, 2)) for i in range(3)]
        cls.quiz.is_published = True
        cls.quiz.full_clean()
        cls.quiz.save()
        cls.quiz_url = reverse("lesson-quiz", args=[cls.lesson.pk])
        cls.attempts_url = reverse("lesson-quiz-attempts", args=[cls.lesson.pk])

    def setUp(self):
        self.client.force_authenticate(self.student)

    def payload(self, *, single=None, multiple=None, submission_id=None):
        return {
            "submission_id": str(submission_id or uuid.uuid4()),
            "answers": [
                {"question_id": self.single.pk, "choice_ids": single if single is not None else [self.single_choices[1].pk]},
                {"question_id": self.multi.pk, "choice_ids": multiple if multiple is not None else [self.multi_choices[0].pk, self.multi_choices[2].pk]},
            ],
        }

    def post(self, payload=None):
        return self.client.post(self.attempts_url, payload or self.payload(), format="json")

    def draft(self):
        self.quiz.is_published = False
        self.quiz.save(update_fields=["is_published"])

    def question_admin_data(self, *, correct=(1,), delete=(), type="single"):
        return {
            "quiz": self.quiz.pk, "text": self.single.text, "type": type, "order": self.single.order,
            "explanation": self.single.explanation,
            "choices-TOTAL_FORMS": "3", "choices-INITIAL_FORMS": "3", "choices-MIN_NUM_FORMS": "0", "choices-MAX_NUM_FORMS": "1000",
            **{f"choices-{index}-{name}": value for index, choice in enumerate(self.single_choices) for name, value in {
                "id": choice.pk, "question": self.single.pk, "text": choice.text, "order": choice.order,
                **({"is_correct": "on"} if index in correct else {}),
                **({"DELETE": "on"} if index in delete else {}),
            }.items()},
        }

    def test_one_optional_quiz_per_lesson(self):
        with transaction.atomic(), self.assertRaises(IntegrityError):
            Quiz.objects.create(lesson=self.lesson, title="Duplicate")

    def test_passing_percentage_model_and_database_bounds(self):
        for percentage in (-1, 101):
            with self.subTest(percentage=percentage):
                self.quiz.passing_percentage = percentage
                with self.assertRaises(ValidationError):
                    self.quiz.full_clean()
                with transaction.atomic(), self.assertRaises(IntegrityError):
                    Quiz.objects.filter(pk=self.quiz.pk).update(passing_percentage=percentage)
        for percentage in (0, 100):
            self.quiz.passing_percentage = percentage
            self.quiz.full_clean()

    def test_drafts_may_be_incomplete_but_publication_requires_questions(self):
        quiz = Quiz(lesson=self.no_quiz_lesson, title="Draft")
        quiz.full_clean()
        quiz.save()
        quiz.is_published = True
        with self.assertRaisesMessage(ValidationError, "at least one question"):
            quiz.full_clean()

    def test_publication_requires_two_choices_and_valid_single_correct_count(self):
        for correct in (0, 2):
            self.single.choices.update(is_correct=False)
            self.single.choices.filter(pk__in=[choice.pk for choice in self.single_choices[:correct]]).update(is_correct=True)
            with self.subTest(correct=correct), self.assertRaisesMessage(ValidationError, "exactly one"):
                self.quiz.full_clean()
        self.single.choices.exclude(pk=self.single_choices[0].pk).delete()
        with self.assertRaisesMessage(ValidationError, "at least two"):
            self.quiz.full_clean()

    def test_multiple_select_requires_a_correct_answer(self):
        self.multi.choices.update(is_correct=False)
        with self.assertRaisesMessage(ValidationError, "at least one correct"):
            self.quiz.full_clean()

    def test_published_question_model_validation_checks_its_correct_choices(self):
        self.single.choices.update(is_correct=False)
        with self.assertRaisesMessage(ValidationError, "exactly one"):
            self.single.full_clean()
        self.draft()
        self.single.full_clean()

    def test_whitespace_questions_or_choices_cannot_be_published(self):
        self.single.text = " "
        self.single.save()
        with self.assertRaises(ValidationError):
            self.quiz.full_clean()
        self.single.text = "Restored question"
        self.single.save()
        self.single.choices.filter(pk=self.single_choices[0].pk).update(text="  ")
        with self.assertRaises(ValidationError):
            self.quiz.full_clean()

    def test_unknown_question_type_is_rejected_by_model_and_database(self):
        self.single.type = "essay"
        with self.assertRaises(ValidationError):
            self.single.full_clean()
        with transaction.atomic(), self.assertRaises(IntegrityError):
            self.single.save()

    def test_anonymous_cannot_read_submit_or_list_attempts(self):
        self.client.force_authenticate(None)
        for method, path in (("get", self.quiz_url), ("get", self.attempts_url), ("post", self.attempts_url)):
            with self.subTest(method=method):
                self.assertEqual(getattr(self.client, method)(path).status_code, 401)
        self.assertEqual(QuizAttempt.objects.count(), 0)

    def test_pending_and_rejected_applicants_cannot_access_quizzes(self):
        for student in (self.pending, self.rejected):
            application = EnrollmentRequest.objects.create(student=student, course=self.course, message="I want to learn this subject in detail.")
            if student == self.rejected:
                review_enrollment_request(application_id=application.pk, reviewer=self.admin, approve=False, note="Not approved")
            self.client.force_authenticate(student)
            for method, path in (("get", self.quiz_url), ("get", self.attempts_url), ("post", self.attempts_url)):
                with self.subTest(student=student.username, method=method):
                    self.assertEqual(getattr(self.client, method)(path).status_code, 403)
        self.assertEqual(QuizAttempt.objects.count(), 0)

    def test_admin_approval_grants_quiz_access_via_existing_enrollment(self):
        application = EnrollmentRequest.objects.create(student=self.pending, course=self.course, message="I want to learn this subject in detail.")
        review_enrollment_request(application_id=application.pk, reviewer=self.admin, approve=True)
        self.client.force_authenticate(self.pending)
        self.assertEqual(self.client.get(self.quiz_url).status_code, 200)
        self.assertEqual(self.post().status_code, 201)

    def test_display_role_and_staff_status_do_not_bypass_enrollment(self):
        for user in (self.staff, self.admin):
            self.client.force_authenticate(user)
            self.assertEqual(self.client.get(self.quiz_url).status_code, 403)
            self.assertEqual(self.post().status_code, 403)

    def test_open_courses_still_require_actual_enrollment(self):
        self.course.enrollment_mode = Course.EnrollmentMode.OPEN
        self.course.save()
        self.client.force_authenticate(self.pending)
        self.assertEqual(self.client.get(self.quiz_url).status_code, 403)
        self.client.post(reverse("course-enroll", args=[self.course.slug]))
        self.assertEqual(self.client.get(self.quiz_url).status_code, 200)

    def test_no_quiz_and_drafts_return_null_without_content(self):
        response = self.client.get(reverse("lesson-quiz", args=[self.no_quiz_lesson.pk]))
        self.assertEqual(response.data, {"quiz": None})
        self.draft()
        self.assertEqual(self.client.get(self.quiz_url).data, {"quiz": None})
        self.assertEqual(self.post().status_code, 409)
        self.assertFalse(QuizAttempt.objects.exists())

    def test_invalid_published_quizzes_are_never_usable_even_if_orm_bypasses_clean(self):
        self.single.choices.update(is_correct=False)
        self.assertEqual(self.client.get(self.quiz_url).status_code, 409)
        self.assertEqual(self.post().status_code, 409)
        self.assertFalse(QuizAttempt.objects.exists())

    def test_pre_submission_content_has_no_correct_flags_or_explanations(self):
        response = self.client.get(self.quiz_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.data["quiz"]), {"id", "lesson_id", "title", "instructions", "passing_percentage", "questions"})
        for question in response.data["quiz"]["questions"]:
            self.assertNotIn("explanation", question)
            self.assertNotIn("correct_choice_ids", question)
            self.assertTrue(all(set(choice) == {"id", "text", "order"} for choice in question["choices"]))
        self.assertNotIn("Single explanation", str(response.data))

    def test_questions_and_choices_follow_order_with_stable_id_ties(self):
        self.multi.order = 0
        self.multi.save()
        self.single.choices.filter(pk=self.single_choices[2].pk).update(order=0)
        data = self.client.get(self.quiz_url).data["quiz"]
        self.assertEqual([q["id"] for q in data["questions"]], [self.multi.pk, self.single.pk])
        self.assertEqual([c["id"] for c in data["questions"][1]["choices"]], [self.single_choices[0].pk, self.single_choices[2].pk, self.single_choices[1].pk])

    def test_get_quiz_uses_bounded_queries(self):
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(self.quiz_url)
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(queries), 5)

    def test_correct_answers_score_100_and_include_post_submission_feedback(self):
        response = self.post()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["score"], 100)
        self.assertTrue(response.data["passed"])
        self.assertEqual(response.data["correct_count"], 2)
        self.assertEqual(response.data["answers"][0]["explanation"], "Single explanation")
        self.assertEqual(response.data["answers"][0]["correct_choice_ids"], [self.single_choices[1].pk])
        self.assertEqual(QuizAnswer.objects.count(), 2)

    def test_wrong_single_answer_and_correct_multiple_answer_have_equal_weight(self):
        response = self.post(self.payload(single=[self.single_choices[0].pk]))
        self.assertEqual(response.data["score"], 50)
        self.assertTrue(response.data["passed"])
        self.assertEqual([answer["is_correct"] for answer in response.data["answers"]], [False, True])

    def test_multiple_select_requires_exact_set_without_partial_credit(self):
        for selected in ([self.multi_choices[0].pk], [self.multi_choices[0].pk, self.multi_choices[1].pk, self.multi_choices[2].pk], [self.multi_choices[1].pk]):
            with self.subTest(selected=selected):
                response = self.post(self.payload(multiple=selected))
                self.assertEqual(response.data["score"], 50)
                self.assertFalse(response.data["answers"][1]["is_correct"])

    def test_passing_threshold_boundaries_zero_and_100(self):
        for threshold, single, multiple, passed in (
            (0, [self.single_choices[0].pk], [self.multi_choices[1].pk], True),
            (100, [self.single_choices[0].pk], [self.multi_choices[0].pk, self.multi_choices[2].pk], False),
            (100, [self.single_choices[1].pk], [self.multi_choices[0].pk, self.multi_choices[2].pk], True),
        ):
            self.quiz.passing_percentage = threshold
            self.quiz.save()
            response = self.post(self.payload(single=single, multiple=multiple))
            self.assertEqual(response.data["passed"], passed)
            self.assertEqual(response.data["passing_percentage"], threshold)

    def test_percentage_rounds_to_two_decimals_but_pass_uses_exact_ratio(self):
        question = QuizQuestion.objects.create(quiz=self.quiz, text="Third", order=3)
        choice = QuizChoice.objects.create(question=question, text="Yes", is_correct=True)
        QuizChoice.objects.create(question=question, text="No")
        self.quiz.passing_percentage = 67
        self.quiz.save()
        payload = self.payload(single=[self.single_choices[0].pk])
        payload["answers"].append({"question_id": question.pk, "choice_ids": [choice.pk]})
        response = self.post(payload)
        self.assertEqual(float(response.data["score"]), 66.67)
        self.assertFalse(response.data["passed"])

    def test_missing_extra_foreign_and_duplicate_questions_are_rejected(self):
        for mutate in (
            lambda answers: answers.pop(),
            lambda answers: answers.append({"question_id": 99999, "choice_ids": [1]}),
            lambda answers: answers.append(answers[0].copy()),
            lambda answers: answers[0].update(question_id=self.multi.pk),
        ):
            payload = self.payload()
            mutate(payload["answers"])
            self.assertEqual(self.post(payload).status_code, 400)
        self.assertFalse(QuizAttempt.objects.exists())

    def test_foreign_choice_even_from_same_quiz_is_rejected(self):
        self.assertEqual(self.post(self.payload(single=[self.multi_choices[0].pk])).status_code, 400)
        self.assertEqual(self.post(self.payload(single=[99999])).status_code, 400)
        self.assertFalse(QuizAttempt.objects.exists())

    def test_single_question_rejects_multiple_selections(self):
        self.assertEqual(self.post(self.payload(single=[self.single_choices[0].pk, self.single_choices[1].pk])).status_code, 400)
        self.assertFalse(QuizAttempt.objects.exists())

    def test_malformed_submissions_are_rejected_without_attempts(self):
        payloads = [{}, [], "bad", True, {"submission_id": "bad", "answers": []}, {"answers": []}, {"submission_id": str(uuid.uuid4()), "answers": "wrong"}]
        for bad in ([], [True], [1.5], ["1"], [None], [self.single_choices[1].pk] * 2):
            payloads.append(self.payload(single=bad))
        for payload in payloads:
            with self.subTest(payload=payload):
                self.assertEqual(self.client.post(self.attempts_url, payload, format="json").status_code, 400)
        self.assertFalse(QuizAttempt.objects.exists())

    def test_client_cannot_supply_score_owner_or_solution_flags(self):
        for extra in ({"score": 100}, {"student": self.other.pk}, {"passed": True}, {"quiz_id": 123}):
            self.assertEqual(self.post({**self.payload(), **extra}).status_code, 400)
        payload = self.payload()
        payload["answers"][0]["is_correct"] = True
        self.assertEqual(self.post(payload).status_code, 400)
        self.assertFalse(QuizAttempt.objects.exists())

    def test_same_submission_reuses_one_attempt_and_timestamp(self):
        payload = self.payload()
        first, second = self.post(payload), self.post(payload)
        self.assertEqual((first.status_code, second.status_code), (201, 200))
        self.assertEqual(first.data, second.data)
        self.assertEqual(QuizAttempt.objects.count(), 1)
        self.assertEqual(QuizAnswer.objects.count(), 2)

    def test_reordered_answers_and_choices_are_same_idempotent_submission(self):
        payload = self.payload()
        first = self.post(payload)
        payload["answers"].reverse()
        payload["answers"][0]["choice_ids"].reverse()
        second = self.post(payload)
        self.assertEqual(first.data["id"], second.data["id"])
        self.assertEqual(QuizAttempt.objects.count(), 1)

    def test_reusing_submission_id_for_different_answers_is_a_conflict(self):
        payload = self.payload()
        self.post(payload)
        payload["answers"][0]["choice_ids"] = [self.single_choices[0].pk]
        self.assertEqual(self.post(payload).status_code, 409)
        self.assertEqual(QuizAttempt.objects.count(), 1)

    def test_unique_constraint_guards_duplicate_attempts(self):
        self.post()
        attempt = QuizAttempt.objects.get()
        with transaction.atomic(), self.assertRaises(IntegrityError):
            QuizAttempt.objects.create(
                quiz=self.quiz, student=self.student, submission_id=attempt.submission_id, request_digest=attempt.request_digest,
                score=0, correct_count=0, question_count=2, passing_percentage=50, passed=False,
            )

    def test_different_submission_ids_allow_unlimited_attempts_and_latest_best(self):
        first = self.post().data
        last = None
        for _ in range(11):
            last = self.post(self.payload(single=[self.single_choices[0].pk], multiple=[self.multi_choices[1].pk])).data
        history = self.client.get(self.attempts_url).data
        self.assertEqual(history["count"], 12)
        self.assertEqual(history["latest"]["id"], last["id"])
        self.assertEqual(history["best"]["id"], first["id"])
        self.assertEqual(len(history["results"]), 10)
        self.assertIsNotNone(history["next"])
        page_two = self.client.get(self.attempts_url + "?page=2").data
        self.assertEqual(len(page_two["results"]), 2)

    def test_students_cannot_view_or_change_another_students_attempts(self):
        attempt_id = self.post().data["id"]
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get(self.attempts_url + f"?student={self.student.pk}").data["count"], 0)
        self.assertEqual(self.client.get(reverse("quiz-attempt-detail", args=[attempt_id])).status_code, 404)
        self.assertEqual(self.client.patch(reverse("quiz-attempt-detail", args=[attempt_id]), {"score": 100}).status_code, 405)
        self.assertEqual(self.client.delete(reverse("quiz-attempt-detail", args=[attempt_id])).status_code, 405)

    def test_own_attempt_detail_and_history_remain_available_when_quiz_is_draft(self):
        attempt_id = self.post().data["id"]
        self.draft()
        self.assertEqual(self.client.get(reverse("quiz-attempt-detail", args=[attempt_id])).status_code, 200)
        self.assertEqual(self.client.get(self.attempts_url).data["count"], 1)

    def test_revoked_enrollment_also_revokes_previous_attempt_access(self):
        attempt_id = self.post().data["id"]
        self.enrollment.delete()
        self.assertEqual(self.client.get(reverse("quiz-attempt-detail", args=[attempt_id])).status_code, 403)
        self.assertEqual(self.client.get(self.attempts_url).status_code, 403)

    def test_feedback_and_threshold_snapshots_survive_question_edits_and_deletion(self):
        result = self.post().data
        self.draft()
        self.quiz.passing_percentage = 100
        self.quiz.save()
        self.single.text = "Changed question"
        self.single.save()
        self.single.choices.all().delete()
        self.single.delete()
        saved = self.client.get(reverse("quiz-attempt-detail", args=[result["id"]])).data
        self.assertEqual(saved, result)
        self.assertIsNone(QuizAnswer.objects.first().question_id)

    def test_quiz_with_attempts_cannot_move_to_another_lesson(self):
        self.post()
        self.quiz.lesson = self.no_quiz_lesson
        with self.assertRaisesMessage(ValidationError, "cannot be moved"):
            self.quiz.full_clean()

    def test_submissions_never_change_curriculum_enrollments_or_lesson_progress(self):
        models = (Course, Module, Lesson, Enrollment, LessonProgress)
        before = [list(model.objects.order_by("pk").values()) for model in models]
        activity_before = self.client.get(reverse("my-activity")).data
        self.post()
        self.post(self.payload(single=[self.single_choices[0].pk]))
        self.assertEqual(before, [list(model.objects.order_by("pk").values()) for model in models])
        self.assertEqual(activity_before, self.client.get(reverse("my-activity")).data)

    def test_existing_completion_button_works_independently_of_failed_quiz(self):
        self.post(self.payload(single=[self.single_choices[0].pk], multiple=[self.multi_choices[1].pk]))
        response = self.client.post(reverse("lesson-complete", args=[self.lesson.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(LessonProgress.objects.get().completed_at)

    def test_partial_save_failure_rolls_back_the_whole_attempt(self):
        with patch("quizzes.services.QuizAnswer.objects.bulk_create", side_effect=RuntimeError("Storage failed")):
            with self.assertRaises(RuntimeError):
                self.post()
        self.assertFalse(QuizAttempt.objects.exists())

    def test_admin_rejects_zero_or_multiple_correct_single_answers(self):
        self.draft()
        self.client.force_login(self.admin)
        path = reverse("admin:quizzes_quizquestion_change", args=[self.single.pk])
        for correct in ((), (0, 1)):
            response = self.client.post(path, self.question_admin_data(correct=correct))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "exactly one correct choice")
        self.assertEqual(list(self.single.choices.values_list("is_correct", flat=True)), [False, True, False])

    def test_admin_can_author_and_publish_a_quiz_without_modifying_curriculum(self):
        before = [list(model.objects.order_by("pk").values()) for model in (Course, Module, Lesson, Enrollment)]
        self.client.force_login(self.admin)
        response = self.client.post(reverse("admin:quizzes_quiz_add"), {
            "lesson": self.no_quiz_lesson.pk, "title": "Admin quiz", "instructions": "Read the choices", "passing_percentage": 75,
            "questions-TOTAL_FORMS": 0, "questions-INITIAL_FORMS": 0, "questions-MIN_NUM_FORMS": 0, "questions-MAX_NUM_FORMS": 1000,
        })
        self.assertEqual(response.status_code, 302)
        quiz = Quiz.objects.get(lesson=self.no_quiz_lesson)
        self.assertFalse(quiz.is_published)
        response = self.client.post(reverse("admin:quizzes_quizquestion_add"), {
            "quiz": quiz.pk, "text": "Choose both", "type": "multiple", "order": 1, "explanation": "Both are correct",
            "choices-TOTAL_FORMS": 2, "choices-INITIAL_FORMS": 0, "choices-MIN_NUM_FORMS": 0, "choices-MAX_NUM_FORMS": 1000,
            **{f"choices-{index}-{name}": value for index in range(2) for name, value in {
                "text": f"Choice {index}", "order": index, "is_correct": "on",
            }.items()},
        })
        self.assertEqual(response.status_code, 302)
        question = quiz.questions.get()
        response = self.client.post(reverse("admin:quizzes_quiz_change", args=[quiz.pk]), {
            "lesson": self.no_quiz_lesson.pk, "title": quiz.title, "instructions": quiz.instructions,
            "passing_percentage": 75, "is_published": "on",
            "questions-TOTAL_FORMS": 1, "questions-INITIAL_FORMS": 1, "questions-MIN_NUM_FORMS": 0, "questions-MAX_NUM_FORMS": 1000,
            "questions-0-id": question.pk, "questions-0-quiz": quiz.pk, "questions-0-text": question.text,
            "questions-0-type": question.type, "questions-0-order": question.order,
        })
        self.assertEqual(response.status_code, 302)
        quiz.refresh_from_db()
        self.assertTrue(quiz.is_published)
        self.assertEqual(before, [list(model.objects.order_by("pk").values()) for model in (Course, Module, Lesson, Enrollment)])

    def test_admin_cannot_publish_a_quiz_with_invalid_questions(self):
        self.draft()
        self.single.choices.all().delete()
        self.client.force_login(self.admin)
        response = self.client.post(reverse("admin:quizzes_quiz_change", args=[self.quiz.pk]), {
            "lesson": self.lesson.pk, "title": self.quiz.title, "instructions": "", "passing_percentage": 50, "is_published": "on",
            "questions-TOTAL_FORMS": 2, "questions-INITIAL_FORMS": 2, "questions-MIN_NUM_FORMS": 0, "questions-MAX_NUM_FORMS": 1000,
            **{f"questions-{index}-{name}": value for index, question in enumerate((self.single, self.multi)) for name, value in {
                "id": question.pk, "quiz": self.quiz.pk, "text": question.text, "type": question.type, "order": question.order,
            }.items()},
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "at least two choices")
        self.quiz.refresh_from_db()
        self.assertFalse(self.quiz.is_published)

    def test_admin_validates_two_choices_after_deletions_and_multiple_type(self):
        self.draft()
        self.client.force_login(self.admin)
        path = reverse("admin:quizzes_quizquestion_change", args=[self.single.pk])
        response = self.client.post(path, self.question_admin_data(delete=(0, 2)))
        self.assertContains(response, "at least two choices")
        response = self.client.post(path, self.question_admin_data(correct=(), type="multiple"))
        self.assertContains(response, "at least one correct choice")
        response = self.client.post(path, self.question_admin_data(correct=(0, 2), type="multiple"))
        self.assertEqual(response.status_code, 302)
        self.single.refresh_from_db()
        self.assertEqual(self.single.type, "multiple")

    def test_admin_requires_unpublishing_before_question_edits_or_deletes(self):
        request = type("Request", (), {"user": self.admin})()
        question_admin = admin.site._registry[QuizQuestion]
        self.assertIn("text", question_admin.get_readonly_fields(request, self.single))
        self.assertFalse(question_admin.has_delete_permission(request, self.single))
        self.draft()
        self.assertTrue(question_admin.has_delete_permission(request, self.single))

    def test_admin_attempt_history_is_read_only(self):
        request = type("Request", (), {"user": self.admin})()
        attempt_admin = admin.site._registry[QuizAttempt]
        self.assertFalse(attempt_admin.has_add_permission(request))
        self.assertFalse(attempt_admin.has_change_permission(request))
        self.assertFalse(attempt_admin.has_delete_permission(request))
        result = self.post().data
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(reverse("admin:quizzes_quizattempt_change", args=[result["id"]])).status_code, 200)

    def test_admin_cannot_delete_a_quiz_with_attempt_history(self):
        self.post()
        request = type("Request", (), {"user": self.admin})()
        self.assertFalse(admin.site._registry[Quiz].has_delete_permission(request, self.quiz))
