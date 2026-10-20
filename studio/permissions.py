from rest_framework.permissions import BasePermission


def active_user(user):
    return bool(user.is_authenticated and user.is_active)


def moderator(user):
    """Trusted admin role or explicit Django superuser override; staff is not a role."""
    return active_user(user) and (user.is_superuser or user.role == 'admin')


def instructor(user):
    return active_user(user) and (moderator(user) or user.role == 'author')


def effective_permissions(user):
    """Expose current DB authority without changing the user's stored role."""
    admin = moderator(user)
    allowed = instructor(user)
    return {
        'role': user.role,
        'effective_role': 'admin' if admin else 'author' if allowed else 'student',
        'is_staff': bool(user.is_staff), 'is_superuser': bool(user.is_superuser),
        'is_active': bool(user.is_active), 'can_access_studio': allowed,
        'is_moderator': admin, 'can_manage_instructors': admin,
        'authority_source': 'superuser' if admin and user.is_superuser else 'role' if allowed else 'none',
    }


class InstructorPermission(BasePermission):
    def has_permission(self, request, view):
        return instructor(request.user)
