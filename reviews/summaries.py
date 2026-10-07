from django.db.models import Avg, Count, Q

from .models import Review


def with_review_summary(queryset):
    approved = Q(reviews__status=Review.Status.APPROVED)
    return queryset.annotate(
        average_rating=Avg("reviews__rating", filter=approved),
        review_count=Count("reviews", filter=approved),
    )


def display_average(value):
    return round(value, 1) if value is not None else None
