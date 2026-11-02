import re
from urllib.parse import urlparse

from django.core.exceptions import ValidationError

GITHUB_HOSTS = ("github.com", "www.github.com")
PHONE_PATTERN = re.compile(r"^(\+7|8)\d{10}$")
PHONE_SEPARATORS = re.compile(r"[\s\-()]")


def validate_github_url(value):
    if not value:
        return
    host = (urlparse(value).hostname or "").lower()
    if host not in GITHUB_HOSTS:
        raise ValidationError("Ссылка должна вести на GitHub (github.com).")


def normalize_phone(value):
    cleaned = PHONE_SEPARATORS.sub("", value or "")
    if not PHONE_PATTERN.match(cleaned):
        raise ValidationError(
            "Телефон должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX."
        )
    return "+7" + cleaned[-10:]
