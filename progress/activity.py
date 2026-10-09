"""Learning activity uses stored completion dates in settings.TIME_ZONE (currently UTC).

The calendar includes today and the previous 364 dates. A streak ends today if
today is active, otherwise yesterday; an older last completion gives a zero
current streak. Streaks can exceed the calendar's 365-day window.
"""
from datetime import timedelta
from zoneinfo import ZoneInfo

from django.conf import settings
from django.db.models import Count, F
from django.db.models.functions import TruncDate
from django.utils import timezone

from .models import LessonProgress


def student_activity(student):
    now = timezone.now()
    activity_timezone = ZoneInfo(settings.TIME_ZONE)
    today = timezone.localtime(now, activity_timezone).date()
    start = today - timedelta(days=364)
    # Match enrollment summaries: exclude malformed rows pointing at another
    # course, unfinished lessons, other students, and future timestamps.
    grouped = (
        LessonProgress.objects.filter(
            enrollment__student=student,
            lesson__module__course_id=F("enrollment__course_id"),
            completed_at__lte=now,
        )
        .annotate(day=TruncDate("completed_at", tzinfo=activity_timezone))
        .values("day")
        .annotate(count=Count("lesson_id", distinct=True))
        .order_by("day")
    )
    counts = {row["day"]: row["count"] for row in grouped}
    daily_counts = [
        {"date": (start + timedelta(days=index)).isoformat(),
         "count": counts.get(start + timedelta(days=index), 0)}
        for index in range(365)
    ]
    streak_day = today if counts.get(today, 0) else today - timedelta(days=1)
    streak = 0
    while counts.get(streak_day, 0):
        streak += 1
        streak_day -= timedelta(days=1)

    # Valid rows are unique per student/lesson through Enrollment's and
    # LessonProgress's existing constraints; counting daily totals counts each once.
    return {
        "timezone": settings.TIME_ZONE,
        "start_date": start.isoformat(),
        "end_date": today.isoformat(),
        "total_completed_lessons": sum(counts.values()),
        "active_days_last_365": sum(day["count"] > 0 for day in daily_counts),
        "current_streak_days": streak,
        "daily_counts": daily_counts,
    }
