def can_preview_lessons(user):
    """Use Django permissions for administrator previews, never the display role."""
    return user.is_active and (
        user.is_superuser or (user.is_staff and user.has_perm("courses.view_lesson"))
    )
