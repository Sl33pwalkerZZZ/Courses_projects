"""Strict validators and private storage helpers for student assignment files."""
import hashlib
import re
import zipfile
from pathlib import Path

from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError

MAX_DOCUMENT_IMAGE = 10 * 1024 * 1024
MAX_VIDEO = 50 * 1024 * 1024
MAX_FILES = 5
MAX_TOTAL = 100 * 1024 * 1024

MIME_BY_EXTENSION = {
    ".pdf": "application/pdf", ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".csv": "text/csv", ".txt": "text/plain", ".png": "image/png", ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg", ".webp": "image/webp", ".mp4": "video/mp4",
}
OOXML_PARTS = {
    ".docx": ("word/document.xml", "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"),
    ".pptx": ("ppt/presentation.xml", "application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"),
    ".xlsx": ("xl/workbook.xml", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"),
}
_SAFE_NAME = re.compile(r"[^\w.() -]+", re.UNICODE)


def safe_display_name(name):
    leaf = Path((name or "").replace("\\", "/")).name
    leaf = _SAFE_NAME.sub("_", leaf).strip(" .")[:255]
    if not leaf or leaf in {".", ".."}:
        raise ValidationError("Choose a file with a valid filename.")
    return leaf


def _read_start(upload, count=32):
    upload.seek(0)
    data = upload.read(count)
    upload.seek(0)
    return data


def _validate_ooxml(upload, extension):
    expected_part, expected_type = OOXML_PARTS[extension]
    try:
        upload.seek(0)
        with zipfile.ZipFile(upload, "r") as archive:
            names = set(archive.namelist())
            if any(name.startswith(("/", "\\")) or ".." in Path(name).parts for name in names):
                raise ValidationError("The Office document contains unsafe package paths.")
            if expected_part not in names or "[Content_Types].xml" not in names:
                raise ValidationError("The file contents do not match its Office document extension.")
            if any("vbaproject.bin" in name.lower() for name in names):
                raise ValidationError("Macro-enabled documents are not accepted.")
            info = archive.getinfo("[Content_Types].xml")
            if info.file_size > 256 * 1024:
                raise ValidationError("The Office document has invalid package metadata.")
            content_types = archive.read(info).decode("utf-8", "strict")
            if expected_type not in content_types or "macroEnabled" in content_types:
                raise ValidationError("The file contents do not match its Office document extension.")
    except (zipfile.BadZipFile, KeyError, UnicodeError, OSError):
        raise ValidationError("The file is not a valid supported Office document.")
    finally:
        upload.seek(0)


def _validate_mp4(upload):
    size = upload.size
    if size < 16 or _read_start(upload, 12)[4:8] != b"ftyp":
        raise ValidationError("The file contents are not a valid MP4 video.")
    # Walk top-level ISO-BMFF boxes by seeking; never decode or execute the media.
    found_media = False
    found_movie = False
    found_ftyp = False
    boxes_seen = 0
    upload.seek(0)
    offset = 0
    try:
        while offset + 8 <= size:
            boxes_seen += 1
            if boxes_seen > 10_000:
                raise ValidationError("The MP4 contains too many metadata boxes.")
            upload.seek(offset)
            header = upload.read(16)
            box_size = int.from_bytes(header[:4], "big")
            box_type = header[4:8]
            header_size = 8
            if box_size == 1:
                if len(header) < 16:
                    break
                box_size = int.from_bytes(header[8:16], "big")
                header_size = 16
            elif box_size == 0:
                box_size = size - offset
            if box_size < header_size or offset + box_size > size:
                break
            found_media |= box_type == b"mdat"
            found_movie |= box_type == b"moov"
            found_ftyp |= box_type == b"ftyp" and box_size >= 16
            offset += box_size
        if not (found_ftyp and found_media and found_movie):
            raise ValidationError("The file is not a complete supported MP4 video.")
    finally:
        upload.seek(0)


def validate_upload(upload):
    filename = safe_display_name(getattr(upload, "name", ""))
    extension = Path(filename).suffix.lower()
    if extension not in MIME_BY_EXTENSION:
        raise ValidationError(f"Unsupported file type: {extension or 'no extension'}.")
    limit = MAX_VIDEO if extension == ".mp4" else MAX_DOCUMENT_IMAGE
    if upload.size <= 0 or upload.size > limit:
        raise ValidationError(f"{filename} exceeds the {limit // (1024 * 1024)} MB per-file limit or is empty.")

    start = _read_start(upload, 32)
    if extension == ".pdf":
        upload.seek(max(0, upload.size - 1024))
        tail = upload.read(1024)
        upload.seek(0)
        if not start.startswith(b"%PDF-") or b"%%EOF" not in tail:
            raise ValidationError("The file contents do not match PDF format.")
    elif extension in OOXML_PARTS:
        _validate_ooxml(upload, extension)
    elif extension in (".png", ".jpg", ".jpeg", ".webp"):
        expected = {".png": "PNG", ".jpg": "JPEG", ".jpeg": "JPEG", ".webp": "WEBP"}[extension]
        try:
            upload.seek(0)
            with Image.open(upload) as image:
                if image.format != expected:
                    raise ValidationError("The file contents do not match the image extension.")
                image.verify()
        except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
            raise ValidationError("The image file is invalid or cannot be safely decoded.")
        finally:
            upload.seek(0)
    elif extension in (".txt", ".csv"):
        upload.seek(0)
        data = upload.read()
        upload.seek(0)
        try:
            data.decode("utf-8-sig", "strict")
        except UnicodeDecodeError:
            raise ValidationError("Text and CSV files must use valid UTF-8 encoding.")
        normalized = data.lstrip(b"\xef\xbb\xbf \t\r\n").lower()
        if b"\x00" in data or normalized.startswith((b"<!doctype html", b"<html", b"<svg")):
            raise ValidationError("Binary content is not accepted as text.")
    elif extension == ".mp4":
        _validate_mp4(upload)

    digest = hashlib.sha256()
    upload.seek(0)
    for chunk in upload.chunks():
        digest.update(chunk)
    upload.seek(0)
    return {"original_filename": filename, "detected_content_type": MIME_BY_EXTENSION[extension],
            "size": upload.size, "sha256": digest.hexdigest()}


def validate_upload_set(uploads):
    uploads = list(uploads)
    if len(uploads) > MAX_FILES:
        raise ValidationError(f"A submission can contain at most {MAX_FILES} files.")
    total = sum(getattr(item, "size", 0) for item in uploads)
    if total > MAX_TOTAL:
        raise ValidationError("The combined file size cannot exceed 100 MB.")
    result = [(upload, validate_upload(upload)) for upload in uploads]
    digests = [meta["sha256"] for _, meta in result]
    if len(digests) != len(set(digests)):
        raise ValidationError("The same file cannot be attached more than once to a submission.")
    return result
