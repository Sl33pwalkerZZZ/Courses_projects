from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, transaction
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework.test import APITestCase

from courses.models import Course, Direction
from progress.models import Enrollment

from .models import Review


class CourseReviewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.student = User.objects.create_user(username="student", email="private@example.com")
        cls.other = User.objects.create_user(username="other")
        cls.third = User.objects.create_user(username="third")
        cls.author = User.objects.create_user(username="author", role="author")
        cls.direction = Direction.objects.create(name="AI", slug="ai")
        cls.course = Course.objects.create(
            title="AI foundations", slug="ai-foundations", description="Learn AI",
            direction=cls.direction, author=cls.author, is_published=True,
        )
        cls.draft = Course.objects.create(
            title="Draft course", slug="draft", description="",
            direction=cls.direction, author=cls.author,
        )
        Enrollment.objects.create(student=cls.student, course=cls.course)
        cls.url = reverse("course-reviews", args=[cls.course.slug])

    def setUp(self):
        self.client.force_authenticate(self.student)

    def review(self, student=None, rating=4, status=Review.Status.PENDING, course=None):
        return Review.objects.create(
            student=student or self.student, course=course or self.course,
            rating=rating, text="A thoughtful and useful course.", status=status,
        )

    def post(self, **overrides):
        return self.client.post(self.url, {"rating": 5, "text": "Clear and practical lessons.", **overrides}, format="json")

    def test_rating_below_one_is_rejected(self):
        response = self.post(rating=0)
        self.assertEqual(response.status_code, 400)
        self.assertIn("rating", response.data)
        self.assertFalse(Review.objects.exists())

    def test_rating_above_five_is_rejected(self):
        response = self.post(rating=6)
        self.assertEqual(response.status_code, 400)
        self.assertIn("rating", response.data)
        self.assertFalse(Review.objects.exists())

    def test_missing_and_noninteger_ratings_are_rejected(self):
        for data in ({"text": "Useful"}, {"rating": 2.5, "text": "Useful"}, {"rating": "bad", "text": "Useful"}):
            with self.subTest(data=data):
                response = self.client.post(self.url, data, format="json")
                self.assertEqual(response.status_code, 400)
                self.assertIn("rating", response.data)

    def test_text_is_required_and_cannot_be_blank(self):
        for data in ({"rating": 4}, {"rating": 4, "text": "   "}):
            with self.subTest(data=data):
                response = self.client.post(self.url, data, format="json")
                self.assertEqual(response.status_code, 400)
                self.assertIn("text", response.data)

    def test_valid_creation_derives_owner_and_course_and_starts_pending(self):
        response = self.post(text="  Clear and practical lessons.  ")
        self.assertEqual(response.status_code, 201)
        review = Review.objects.get()
        self.assertEqual(review.student, self.student)
        self.assertEqual(review.course, self.course)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.text, "Clear and practical lessons.")
        self.assertEqual(review.status, Review.Status.PENDING)
        self.assertEqual(response.data["status"], Review.Status.PENDING)
        self.assertEqual(response.data["author"], self.student.username)
        self.assertEqual(set(response.data), {"id", "rating", "text", "created_at", "author", "status"})

    def test_unauthenticated_post_is_rejected(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.post().status_code, 401)
        self.assertFalse(Review.objects.exists())

    def test_non_enrolled_user_cannot_review(self):
        self.client.force_authenticate(self.other)
        response = self.post()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["code"], "not_enrolled")
        self.assertFalse(Review.objects.exists())

    def test_duplicate_is_rejected_for_every_moderation_status(self):
        review = self.review()
        for moderation_status in Review.Status.values:
            with self.subTest(status=moderation_status):
                review.status = moderation_status
                review.save(update_fields=["status"])
                response = self.post()
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.data["code"], "duplicate_review")
                self.assertEqual(Review.objects.count(), 1)

    def test_server_controlled_fields_cannot_be_submitted(self):
        for field, value in {"student": self.other.id, "course": self.draft.id, "status": "approved", "created_at": "2026-01-01T00:00:00Z", "id": 123}.items():
            with self.subTest(field=field):
                response = self.post(**{field: value})
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.data)
        self.assertFalse(Review.objects.exists())

    def test_malformed_request_returns_validation_error(self):
        self.assertEqual(self.client.post(self.url, [], format="json").status_code, 400)

    def test_draft_and_missing_courses_are_not_exposed(self):
        for slug in (self.draft.slug, "missing"):
            url = reverse("course-reviews", args=[slug])
            self.assertEqual(self.client.get(url).status_code, 404)
            self.assertEqual(self.client.post(url, {"rating": 5, "text": "Useful"}, format="json").status_code, 404)

    def test_pending_reviews_are_hidden_from_public_list(self):
        self.review()
        self.client.force_authenticate(None)
        data = self.client.get(self.url).data
        self.assertEqual(data["reviews"], [])
        self.assertEqual(data["review_count"], 0)
        self.assertIsNone(data["average_rating"])
        self.assertIsNone(data["my_review"])
        self.assertFalse(data["can_review"])

    def test_rejected_reviews_are_hidden_from_public_list(self):
        self.review(status=Review.Status.REJECTED)
        self.client.force_authenticate(None)
        data = self.client.get(self.url).data
        self.assertEqual(data["reviews"], [])
        self.assertEqual(data["review_count"], 0)
        self.assertIsNone(data["average_rating"])

    def test_approved_reviews_are_public_safe_and_newest_first(self):
        first = self.review(status=Review.Status.APPROVED)
        second = self.review(student=self.other, status=Review.Status.APPROVED)
        self.client.force_authenticate(None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual([row["id"] for row in response.data["reviews"]], [second.id, first.id])
        for row in response.data["reviews"]:
            self.assertEqual(set(row), {"id", "rating", "text", "created_at", "author"})
        self.assertNotIn(self.student.email, str(response.data))

    def test_own_review_includes_every_status_without_exposing_other_private_reviews(self):
        own = self.review()
        self.review(student=self.other)
        self.review(student=self.third, status=Review.Status.REJECTED)
        for moderation_status in Review.Status.values:
            with self.subTest(status=moderation_status):
                own.status = moderation_status
                own.save(update_fields=["status"])
                data = self.client.get(self.url).data
                self.assertEqual(data["my_review"]["id"], own.id)
                self.assertEqual(data["my_review"]["status"], moderation_status)
                self.assertEqual([row["id"] for row in data["reviews"]], [own.id] if moderation_status == "approved" else [])
                self.assertTrue(data["can_review"])

    def test_enrollment_flag_is_scoped_to_current_user_and_course(self):
        self.client.force_authenticate(self.other)
        self.assertFalse(self.client.get(self.url).data["can_review"])
        Enrollment.objects.create(student=self.other, course=self.draft)
        self.assertFalse(self.client.get(self.url).data["can_review"])
        Enrollment.objects.create(student=self.other, course=self.course)
        self.assertTrue(self.client.get(self.url).data["can_review"])

    def test_all_summaries_use_only_approved_reviews_for_this_course(self):
        self.review(rating=5, status=Review.Status.APPROVED)
        other = self.review(student=self.other, rating=4, status=Review.Status.APPROVED)
        self.review(student=self.third, rating=1)
        self.review(student=self.author, rating=1, status=Review.Status.REJECTED)
        self.review(student=self.other, rating=1, status=Review.Status.APPROVED, course=self.draft)
        list_url = reverse("course-list")
        detail_url = reverse("course-detail", args=[self.course.slug])
        for url in (self.url, list_url, detail_url):
            with self.subTest(url=url):
                data = self.client.get(url).data
                if url == list_url:
                    self.assertEqual(len(data), 1)
                    data = data[0]
                self.assertEqual(data["average_rating"], 4.5)
                self.assertEqual(data["review_count"], 2)
        other.status = Review.Status.REJECTED
        other.save(update_fields=["status"])
        data = self.client.get(self.url).data
        self.assertEqual(data["average_rating"], 5)
        self.assertEqual(data["review_count"], 1)

    def test_empty_course_responses_preserve_fields_and_have_null_average(self):
        for url in (reverse("course-list"), reverse("course-detail", args=[self.course.slug])):
            data = self.client.get(url).data
            if isinstance(data, list):
                data = data[0]
            self.assertIsNone(data["average_rating"])
            self.assertEqual(data["review_count"], 0)
            self.assertTrue({"id", "title", "slug", "description", "direction", "level", "author"}.issubset(data))

    def test_average_is_rounded_to_one_decimal(self):
        self.review(rating=5, status=Review.Status.APPROVED)
        self.review(student=self.other, rating=5, status=Review.Status.APPROVED)
        self.review(student=self.third, rating=4, status=Review.Status.APPROVED)
        self.assertEqual(self.client.get(self.url).data["average_rating"], 4.7)
        self.assertEqual(self.client.get(reverse("course-list")).data[0]["average_rating"], 4.7)

    def test_course_list_query_count_does_not_grow_with_courses_and_review_authors(self):
        url = reverse("course-list")
        with CaptureQueriesContext(connection) as initial:
            self.client.get(url)
        for index in range(3):
            course = Course.objects.create(
                title=f"Course {index}", slug=f"course-{index}", description="",
                direction=self.direction, author=self.author, is_published=True,
            )
            self.review(course=course, status=Review.Status.APPROVED)
        with CaptureQueriesContext(connection) as expanded:
            response = self.client.get(url)
        self.assertEqual(len(response.data), 4)
        self.assertEqual(len(initial), len(expanded))

    def test_public_reviews_query_count_does_not_grow_with_authors(self):
        self.client.force_authenticate(None)
        self.review(status=Review.Status.APPROVED)
        with CaptureQueriesContext(connection) as initial:
            self.client.get(self.url)
        self.review(student=self.other, status=Review.Status.APPROVED)
        self.review(student=self.third, status=Review.Status.APPROVED)
        with CaptureQueriesContext(connection) as expanded:
            response = self.client.get(self.url)
        self.assertEqual(len(response.data["reviews"]), 3)
        self.assertEqual(len(initial), len(expanded))

    def test_model_validation_and_database_constraint_enforce_rating_range(self):
        for rating in (0, 6):
            with self.subTest(rating=rating):
                review = Review(student=self.student, course=self.course, rating=rating, text="Useful")
                with self.assertRaises(ValidationError):
                    review.full_clean()
                with self.assertRaises(IntegrityError), transaction.atomic():
                    review.save()
        for rating in (1, 5):
            Review(student=self.student, course=self.course, rating=rating, text="Useful").full_clean()

    def test_database_updates_cannot_bypass_rating_or_uniqueness_rules(self):
        review = self.review()
        with self.assertRaises(IntegrityError), transaction.atomic():
            Review.objects.filter(pk=review.pk).update(rating=6)
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.review()

    def detail_url(self, review):
        return reverse("review-detail", args=[review.pk])

    def assert_rating_summary(self, average, count, public_ids):
        urls = (self.url, reverse("course-list"), reverse("course-detail", args=[self.course.slug]))
        for url in urls:
            data = self.client.get(url).data
            if isinstance(data, list):
                data = data[0]
            self.assertEqual(data["average_rating"], average)
            self.assertEqual(data["review_count"], count)
            if url == self.url:
                self.assertEqual({row["id"] for row in data["reviews"]}, set(public_ids))

    def test_unauthenticated_edit_is_rejected(self):
        review = self.review(status=Review.Status.APPROVED)
        self.client.force_authenticate(None)
        self.assertEqual(self.client.patch(self.detail_url(review), {"text": "Edited"}, format="json").status_code, 401)
        review.refresh_from_db()
        self.assertEqual(review.status, Review.Status.APPROVED)

    def test_other_users_and_course_author_cannot_edit_a_review(self):
        review = self.review(status=Review.Status.APPROVED)
        for user in (self.other, self.author):
            self.client.force_authenticate(user)
            self.assertEqual(self.client.patch(self.detail_url(review), {"rating": 1}, format="json").status_code, 404)
        review.refresh_from_db()
        self.assertEqual(review.rating, 4)
        self.assertEqual(review.status, Review.Status.APPROVED)

    def test_author_can_edit_both_fields_with_safe_response_and_immutable_metadata(self):
        review = self.review()
        created_at = review.created_at
        response = self.client.patch(self.detail_url(review), {"rating": 2, "text": "  Updated experience.  "}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.data), {"id", "rating", "text", "status", "created_at", "author"})
        self.assertEqual(response.data["id"], review.pk)
        self.assertEqual(response.data["author"], self.student.username)
        self.assertEqual(response.data["rating"], 2)
        self.assertEqual(response.data["text"], "Updated experience.")
        self.assertEqual(response.data["status"], Review.Status.PENDING)
        review.refresh_from_db()
        self.assertEqual(review.created_at, created_at)
        self.assertEqual(review.student, self.student)
        self.assertEqual(review.course, self.course)
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(self.post().data["code"], "duplicate_review")

    def test_partial_edit_preserves_the_omitted_field(self):
        review = self.review()
        original_text = review.text
        response = self.client.patch(self.detail_url(review), {"rating": 1}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["text"], original_text)
        response = self.client.patch(self.detail_url(review), {"text": "New text"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["rating"], 1)

    def test_edit_rating_validation_does_not_change_content_or_moderation(self):
        review = self.review(status=Review.Status.APPROVED)
        for rating in (0, 6, 2.5, None, "invalid"):
            with self.subTest(rating=rating):
                response = self.client.patch(self.detail_url(review), {"rating": rating}, format="json")
                self.assertEqual(response.status_code, 400)
                self.assertIn("rating", response.data)
                review.refresh_from_db()
                self.assertEqual(review.rating, 4)
                self.assertEqual(review.status, Review.Status.APPROVED)

    def test_edit_text_cannot_be_empty_blank_or_null(self):
        review = self.review(status=Review.Status.APPROVED)
        original_text = review.text
        for text in ("", " \n\t ", None):
            with self.subTest(text=text):
                response = self.client.patch(self.detail_url(review), {"text": text}, format="json")
                self.assertEqual(response.status_code, 400)
                self.assertIn("text", response.data)
                review.refresh_from_db()
                self.assertEqual(review.text, original_text)
                self.assertEqual(review.status, Review.Status.APPROVED)

    def test_edit_rejects_server_controlled_fields(self):
        review = self.review(status=Review.Status.APPROVED)
        fields = {"student": self.other.pk, "course": self.draft.pk, "status": "approved", "created_at": "2026-01-01T00:00:00Z", "id": 999}
        for field, value in fields.items():
            with self.subTest(field=field):
                response = self.client.patch(self.detail_url(review), {"text": "Edited", field: value}, format="json")
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.data)
        review.refresh_from_db()
        self.assertEqual(review.status, Review.Status.APPROVED)
        self.assertEqual(review.text, "A thoughtful and useful course.")

    def test_empty_and_malformed_edits_are_rejected_without_demoting_review(self):
        review = self.review(status=Review.Status.APPROVED)
        for data in ({}, [], "invalid"):
            with self.subTest(data=data):
                response = self.client.patch(self.detail_url(review), data, format="json")
                self.assertEqual(response.status_code, 400)
        review.refresh_from_db()
        self.assertEqual(review.status, Review.Status.APPROVED)

    def test_approved_edit_becomes_pending_and_stops_affecting_all_public_summaries(self):
        review = self.review(rating=5, status=Review.Status.APPROVED)
        other = self.review(student=self.other, rating=3, status=Review.Status.APPROVED)
        self.assert_rating_summary(4, 2, [review.pk, other.pk])
        response = self.client.patch(self.detail_url(review), {"rating": 1, "text": "Changed experience"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], Review.Status.PENDING)
        self.assert_rating_summary(3, 1, [other.pk])
        own = self.client.get(self.url).data["my_review"]
        self.assertEqual(own["id"], review.pk)
        self.assertEqual(own["text"], "Changed experience")
        self.assertEqual(own["status"], Review.Status.PENDING)
        self.client.force_authenticate(None)
        public = self.client.get(self.url).data
        self.assertIsNone(public["my_review"])
        self.assertNotIn(review.pk, [row["id"] for row in public["reviews"]])
        # Existing Django-admin moderation can publish the edited content again.
        review.refresh_from_db()
        review.status = Review.Status.APPROVED
        review.save(update_fields=["status"])
        self.assert_rating_summary(2, 2, [review.pk, other.pk])

    def test_editing_only_approved_review_returns_null_average_and_zero_count(self):
        review = self.review(status=Review.Status.APPROVED)
        self.client.patch(self.detail_url(review), {"text": "Changed"}, format="json")
        self.assert_rating_summary(None, 0, [])

    def test_rejected_review_becomes_pending_after_edit(self):
        review = self.review(status=Review.Status.REJECTED)
        response = self.client.patch(self.detail_url(review), {"text": "Revised review"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], Review.Status.PENDING)
        self.assert_rating_summary(None, 0, [])

    def test_pending_review_remains_pending_after_edit(self):
        review = self.review()
        response = self.client.patch(self.detail_url(review), {"text": "Revised review"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], Review.Status.PENDING)
        self.assertEqual(self.client.get(self.url).data["my_review"]["text"], "Revised review")

    def test_unauthenticated_delete_is_rejected(self):
        review = self.review()
        self.client.force_authenticate(None)
        self.assertEqual(self.client.delete(self.detail_url(review)).status_code, 401)
        self.assertTrue(Review.objects.filter(pk=review.pk).exists())

    def test_other_users_and_course_author_cannot_delete_a_review(self):
        review = self.review()
        for user in (self.other, self.author):
            self.client.force_authenticate(user)
            self.assertEqual(self.client.delete(self.detail_url(review)).status_code, 404)
        self.assertTrue(Review.objects.filter(pk=review.pk).exists())

    def test_author_can_delete_pending_review_and_submit_a_new_one(self):
        review = self.review()
        response = self.client.delete(self.detail_url(review))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")
        self.assertFalse(Review.objects.filter(pk=review.pk).exists())
        self.assertIsNone(self.client.get(self.url).data["my_review"])
        self.assert_rating_summary(None, 0, [])
        self.assertEqual(self.post().status_code, 201)

    def test_author_can_delete_approved_review_and_all_summaries_update(self):
        review = self.review(rating=5, status=Review.Status.APPROVED)
        other = self.review(student=self.other, rating=3, status=Review.Status.APPROVED)
        self.assert_rating_summary(4, 2, [review.pk, other.pk])
        self.assertEqual(self.client.delete(self.detail_url(review)).status_code, 204)
        self.assertFalse(Review.objects.filter(pk=review.pk).exists())
        self.assertIsNone(self.client.get(self.url).data["my_review"])
        self.assert_rating_summary(3, 1, [other.pk])

    def test_deleting_only_approved_review_returns_null_average_and_zero_count(self):
        review = self.review(status=Review.Status.APPROVED)
        self.assertEqual(self.client.delete(self.detail_url(review)).status_code, 204)
        self.assert_rating_summary(None, 0, [])

    def test_author_can_delete_rejected_review(self):
        review = self.review(status=Review.Status.REJECTED)
        self.assertEqual(self.client.delete(self.detail_url(review)).status_code, 204)
        self.assertFalse(Review.objects.filter(pk=review.pk).exists())
        self.assertIsNone(self.client.get(self.url).data["my_review"])

    def test_missing_review_and_unsupported_methods_do_not_expose_data(self):
        url = reverse("review-detail", args=[999])
        self.assertEqual(self.client.patch(url, {"rating": 4}, format="json").status_code, 404)
        self.assertEqual(self.client.delete(url).status_code, 404)
        review = self.review()
        self.assertEqual(self.client.get(self.detail_url(review)).status_code, 405)
        self.assertEqual(self.client.put(self.detail_url(review), {}, format="json").status_code, 405)

    def test_author_can_manage_review_if_enrollment_or_publication_changes(self):
        review = self.review()
        Enrollment.objects.filter(student=self.student, course=self.course).delete()
        self.course.is_published = False
        self.course.save(update_fields=["is_published"])
        self.assertEqual(self.client.patch(self.detail_url(review), {"text": "Revised"}, format="json").status_code, 200)
        self.assertEqual(self.client.delete(self.detail_url(review)).status_code, 204)
