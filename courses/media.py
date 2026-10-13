"""Separate public assets from existing private uploads without moving files."""
from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404
from django.views.decorators.http import require_safe


def confined_file(root, filename):
    """Reject traversal and symlinks escaping the selected filesystem root."""
    if not filename or "\\" in filename or "\x00" in filename:
        raise Http404("File not found.")
    if any(part in ("", ".", "..") for part in filename.split("/")):
        raise Http404("File not found.")
    root = Path(root).resolve()
    candidate = (root / filename).resolve()
    if not candidate.is_relative_to(root):
        raise Http404("File not found.")
    return candidate


def private_lesson_file(root, filename):
    if not filename.startswith("lessons/"):
        raise Http404("Image not found.")
    candidate = confined_file(root, filename)
    # Also reject symlinks into unrelated private directories inside MEDIA_ROOT.
    if not candidate.is_relative_to(Path(root).resolve() / "lessons"):
        raise Http404("Image not found.")
    return candidate


@require_safe
def public_media(request, filename):
    # Legacy private URLs must stay blocked, even if public storage is mispopulated.
    if filename.split("/", 1)[0] in ("lessons", "submissions"):
        raise Http404("File not found.")
    candidate = confined_file(settings.PUBLIC_MEDIA_ROOT, filename)
    # Fail closed for overlapping roots, including a public root containing private uploads.
    private_root = Path(settings.MEDIA_ROOT).resolve()
    public_root = Path(settings.PUBLIC_MEDIA_ROOT).resolve()
    if public_root.is_relative_to(private_root) or private_root.is_relative_to(public_root):
        raise Http404("File not found.")
    try:
        response = FileResponse(candidate.open("rb"))
    except (FileNotFoundError, IsADirectoryError, PermissionError):
        raise Http404("File not found.")
    response["X-Content-Type-Options"] = "nosniff"
    return response
