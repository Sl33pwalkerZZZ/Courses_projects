"""Optional authored image alternatives without changing stored lesson records."""
import json
import logging
from pathlib import Path

from django.conf import settings


logger = logging.getLogger(__name__)
LANGUAGES = ("en", "ru", "kk")


def load_image_descriptions():
    try:
        with Path(settings.LESSON_IMAGE_DESCRIPTIONS_FILE).open(encoding="utf-8") as source:
            descriptions = json.load(source)
        if not isinstance(descriptions, dict):
            raise ValueError("Expected an image-ID mapping")
        return descriptions
    except FileNotFoundError:
        return {}
    except (OSError, ValueError, TypeError):
        # Do not log authored content or break lesson access for bad optional metadata.
        logger.warning("Could not read lesson image descriptions; check the private metadata file.")
        return {}


def image_alt_text(descriptions, image_id):
    entry = descriptions.get(str(image_id), {})
    if not isinstance(entry, dict):
        return {}
    return {
        language: entry[language].strip()
        for language in LANGUAGES
        if isinstance(entry.get(language), str) and entry[language].strip()
    }
