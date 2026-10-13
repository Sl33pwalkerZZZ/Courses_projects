from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import override_settings
from django.urls import path, reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from progress.models import Enrollment, EnrollmentRequest
from progress.services import review_enrollment_request

from config.urls import urlpatterns as application_urls
from .media import public_media
from .models import Course, Direction, Lesson, LessonImage, Module


# Django's test runner disables DEBUG before loading URLs. Include the real
# development public handler explicitly so its filesystem isolation is tested.
urlpatterns = [*application_urls, path("media/<path:filename>", public_media)]

# All records/files below are disposable test fixtures, never development data.
PNG = (
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
    b'\x08\x04\x00\x00\x00\xb5\x1c\x0c\x02\x00\x00\x00\x0bIDATx\xdac\xfc\xff'
    b'\x1f\x00\x03\x03\x02\x00\xef\xbf\x69\x9b\x00\x00\x00\x00IEND\xaeB`\x82'
)


class ProtectedLessonMediaTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.student = User.objects.create_user(username="media-student", password="test-password")
        cls.other = User.objects.create_user(username="media-other")
        cls.staff = User.objects.create_user(username="media-staff", is_staff=True)
        cls.admin = User.objects.create_superuser(username="media-admin", password="test-password")
        direction = Direction.objects.create(name="Media AI", slug="media-ai")
        cls.course = Course.objects.create(
            title="Media course", slug="media-course", description="", direction=direction,
            author=cls.admin, is_published=True,
        )
        cls.other_course = Course.objects.create(
            title="Other media course", slug="other-media", description="", direction=direction,
            author=cls.admin, is_published=True,
        )
        module = Module.objects.create(course=cls.course, title="Images", order=1)
        other_module = Module.objects.create(course=cls.other_course, title="Other images", order=1)
        cls.lesson = Lesson.objects.create(module=module, title="Image lesson", text_content="", order=1)
        cls.other_lesson = Lesson.objects.create(module=other_module, title="Other image lesson", text_content="", order=1)
        cls.image = LessonImage.objects.create(lesson=cls.lesson, image="lessons/example.png")
        cls.other_image = LessonImage.objects.create(lesson=cls.other_lesson, image="lessons/other.png")
        cls.url = reverse("lesson-image", args=[cls.image.pk])

    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.private_root = self.root / "private"
        self.public_root = self.root / "public"
        (self.private_root / "lessons").mkdir(parents=True)
        (self.private_root / "submissions").mkdir()
        (self.public_root / "covers").mkdir(parents=True)
        (self.private_root / "lessons/example.png").write_bytes(PNG)
        (self.private_root / "lessons/other.png").write_bytes(PNG)
        (self.private_root / "submissions/private.txt").write_text("private submission")
        (self.private_root / "unrelated.txt").write_text("unrelated private file")
        (self.public_root / "covers/public.png").write_bytes(PNG)
        self.settings_override = override_settings(
            MEDIA_ROOT=self.private_root, PUBLIC_MEDIA_ROOT=self.public_root, DEBUG=True,
            ROOT_URLCONF=__name__,
        )
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)

    def enroll(self, student=None, course=None):
        Enrollment.objects.create(student=student or self.student, course=course or self.course)

    def image_bytes(self, response):
        self.assertEqual(response.status_code, 200)
        content = b"".join(response.streaming_content)
        response.close()
        return content

    def test_anonymous_and_invalid_jwt_cannot_fetch_image(self):
        self.assertEqual(self.client.get(self.url).status_code, 401)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalid-token")
        self.assertEqual(self.client.get(self.url).status_code, 401)

    def test_pending_and_rejected_students_cannot_fetch_image(self):
        self.client.force_authenticate(self.student)
        request = EnrollmentRequest.objects.create(
            student=self.student, course=self.course, message="Please approve this test application.",
        )
        self.assertEqual(self.client.get(self.url).status_code, 403)
        review_enrollment_request(application_id=request.pk, reviewer=self.admin, approve=False, note="Test rejection")
        self.assertEqual(self.client.get(self.url).status_code, 403)

    def test_approved_student_can_fetch_with_real_jwt(self):
        request = EnrollmentRequest.objects.create(
            student=self.student, course=self.course, message="Please approve this test application.",
        )
        review_enrollment_request(application_id=request.pk, reviewer=self.admin, approve=True)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(self.student)}")
        response = self.client.get(self.url)
        self.assertEqual(response["Content-Type"], "image/png")
        self.assertEqual(response["Cache-Control"], "private, no-store")
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")
        self.assertIn("Authorization", response["Vary"])
        self.assertIn("Cookie", response["Vary"])
        self.assertEqual(self.image_bytes(response), PNG)

    def test_enrolled_student_can_fetch_but_another_course_cannot(self):
        self.enroll()
        self.enroll(self.other, self.other_course)
        self.client.force_authenticate(self.student)
        self.assertEqual(self.image_bytes(self.client.get(self.url)), PNG)
        self.assertEqual(self.client.get(reverse("lesson-image", args=[self.other_image.pk])).status_code, 403)
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get(self.url).status_code, 403)

    def test_staff_preview_requires_existing_lesson_permission(self):
        self.client.force_authenticate(self.staff)
        self.assertEqual(self.client.get(self.url).status_code, 403)
        self.staff.user_permissions.add(Permission.objects.get(codename="view_lesson", content_type__app_label="courses"))
        # Refetch to discard Django's permission cache from the denied request.
        self.client.force_authenticate(get_user_model().objects.get(pk=self.staff.pk))
        self.assertEqual(self.image_bytes(self.client.get(self.url)), PNG)

    def test_admin_session_can_use_authenticated_filefield_link(self):
        self.client.force_login(self.admin)
        self.assertEqual(self.image.image.url, "/api/private-media/lessons/example.png")
        self.assertEqual(self.image_bytes(self.client.get(self.image.image.url)), PNG)

    def test_unknown_or_missing_image_is_404(self):
        self.enroll()
        self.client.force_authenticate(self.student)
        self.assertEqual(self.client.get(reverse("lesson-image", args=[999999])).status_code, 404)
        (self.private_root / "lessons/example.png").unlink()
        self.assertEqual(self.client.get(self.url).status_code, 404)

    def test_serializer_returns_only_authenticated_image_endpoint(self):
        self.enroll()
        self.client.force_authenticate(self.student)
        with patch("django.core.files.storage.FileSystemStorage.url", side_effect=AssertionError("No storage URL")):
            response = self.client.get(reverse("lesson-detail", args=[self.lesson.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["images"][0]["image"], self.url)
        self.assertNotIn("example.png", str(response.data))

    def test_private_filename_link_preserves_permissions_and_denies_unrelated_files(self):
        path = reverse("private-media", args=["lessons/example.png"])
        self.assertEqual(self.client.get(path).status_code, 401)
        self.client.force_authenticate(self.student)
        self.assertEqual(self.client.get(path).status_code, 403)
        self.enroll()
        self.assertEqual(self.image_bytes(self.client.get(path)), PNG)
        for name in ("submissions/private.txt", "unrelated.txt", "lessons/unregistered.png"):
            self.assertEqual(self.client.get(reverse("private-media", args=[name])).status_code, 404)

    def test_shared_filename_requires_access_to_at_least_one_registered_lesson(self):
        LessonImage.objects.create(lesson=self.other_lesson, image=self.image.image.name)
        self.client.force_authenticate(self.other)
        path = reverse("private-media", args=[self.image.image.name])
        self.assertEqual(self.client.get(path).status_code, 403)
        self.enroll(self.other, self.other_course)
        self.assertEqual(self.image_bytes(self.client.get(path)), PNG)
        # Sharing physical bytes does not grant access to the first lesson's ID.
        self.assertEqual(self.client.get(self.url).status_code, 403)

    def test_direct_legacy_media_never_serves_private_files(self):
        for user in (None, self.student, self.admin):
            self.client.force_authenticate(user)
            for name in ("lessons/example.png", "submissions/private.txt", "unrelated.txt"):
                self.assertEqual(self.client.get(f"/media/{name}").status_code, 404)

    def test_public_course_cover_remains_public(self):
        self.assertEqual(self.image_bytes(self.client.get("/media/covers/public.png")), PNG)

    def test_path_traversal_cannot_retrieve_private_or_unrelated_files(self):
        self.enroll()
        self.client.force_authenticate(self.student)
        for path in (
            "/media/../private/lessons/example.png", "/media/%2e%2e/private/lessons/example.png",
            "/media/covers/../../private/lessons/example.png", "/media/covers%5c..%5csecret",
            "/api/private-media/lessons/../submissions/private.txt",
            "/api/private-media/lessons/%2e%2e/submissions/private.txt",
            "/api/private-media/lessons//example.png",
        ):
            self.assertEqual(self.client.get(path).status_code, 404, path)
        for filename in ("../unrelated.txt", "lessons/../unrelated.txt", "/etc/passwd", "lessons/../../secret", "lessons\\example.png"):
            LessonImage.objects.filter(pk=self.image.pk).update(image=filename)
            self.assertEqual(self.client.get(self.url).status_code, 404, filename)

    def test_symlinks_cannot_escape_or_access_unrelated_private_directories(self):
        self.enroll()
        self.client.force_authenticate(self.student)
        (self.private_root / "lessons/escape.png").symlink_to(self.private_root / "submissions/private.txt")
        LessonImage.objects.filter(pk=self.image.pk).update(image="lessons/escape.png")
        self.assertEqual(self.client.get(self.url).status_code, 404)
        (self.public_root / "covers/escape.png").symlink_to(self.private_root / "lessons/example.png")
        self.assertEqual(self.client.get("/media/covers/escape.png").status_code, 404)

    def test_overlapping_public_private_roots_fail_closed(self):
        for public_root in (self.private_root, self.root):
            with override_settings(PUBLIC_MEDIA_ROOT=public_root):
                self.assertEqual(self.client.get("/media/unrelated.txt").status_code, 404)

    @override_settings(DEBUG=False)
    def test_private_images_remain_protected_without_debug(self):
        self.assertEqual(self.client.get(self.url).status_code, 401)
        self.assertEqual(self.client.get("/media/lessons/example.png").status_code, 404)
        self.enroll()
        self.client.force_authenticate(self.student)
        self.assertEqual(self.image_bytes(self.client.get(self.url)), PNG)
