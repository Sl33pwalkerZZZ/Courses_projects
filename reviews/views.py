from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Course
from progress.models import Enrollment

from .models import Review
from .serializers import OwnReviewSerializer, ReviewCreateSerializer, ReviewSerializer, ReviewUpdateSerializer
from .summaries import display_average, with_review_summary


def review_error(code, detail, http_status=status.HTTP_400_BAD_REQUEST):
    return Response({"code": code, "detail": detail}, status=http_status)


class CourseReviewsView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_course(self, slug):
        return get_object_or_404(with_review_summary(Course.objects.filter(is_published=True)), slug=slug)

    def get(self, request, slug):
        course = self.get_course(slug)
        reviews = course.reviews.filter(status=Review.Status.APPROVED).select_related("student").order_by(
            "-created_at", "-pk"
        )
        own_review = None
        can_review = False
        if request.user.is_authenticated:
            own_review = course.reviews.filter(student=request.user).select_related("student").first()
            can_review = Enrollment.objects.filter(student=request.user, course=course).exists()
        return Response({
            "average_rating": display_average(course.average_rating),
            "review_count": course.review_count,
            "reviews": ReviewSerializer(reviews, many=True).data,
            "my_review": OwnReviewSerializer(own_review).data if own_review else None,
            "can_review": can_review,
        })

    def post(self, request, slug):
        course = self.get_course(slug)
        if not Enrollment.objects.filter(student=request.user, course=course).exists():
            return review_error("not_enrolled", "Enroll in this course before writing a review.", status.HTTP_403_FORBIDDEN)
        if Review.objects.filter(student=request.user, course=course).exists():
            return review_error("duplicate_review", "You have already submitted a review for this course.")
        serializer = ReviewCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                review = serializer.save(student=request.user, course=course, status=Review.Status.PENDING)
        except IntegrityError:
            # The database uniqueness rule also handles concurrent submissions.
            if Review.objects.filter(student=request.user, course=course).exists():
                return review_error("duplicate_review", "You have already submitted a review for this course.")
            raise
        return Response(OwnReviewSerializer(review).data, status=status.HTTP_201_CREATED)


class OwnReviewDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_review(self, user, pk):
        # An owner-scoped lookup does not reveal whether another user's review exists.
        return get_object_or_404(
            Review.objects.select_for_update().select_related("student"), student=user, pk=pk,
        )

    def patch(self, request, pk):
        with transaction.atomic():
            review = self.get_review(request.user, pk)
            serializer = ReviewUpdateSerializer(review, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            review = serializer.save(status=Review.Status.PENDING)
        return Response(OwnReviewSerializer(review).data)

    def delete(self, request, pk):
        with transaction.atomic():
            review = self.get_review(request.user, pk)
            review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
