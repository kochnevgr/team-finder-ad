import re
from enum import StrEnum

from django.conf import settings

PAGE_SIZE = 12
SKILL_SUGGESTIONS_LIMIT = 10

PROJECT_NAME_MAX_LENGTH = 200
PROJECT_STATUS_MAX_LENGTH = 6

SKILL_NAME_MAX_LENGTH = 124

USER_NAME_MAX_LENGTH = 124
USER_SURNAME_MAX_LENGTH = 124
USER_PHONE_MAX_LENGTH = 12
USER_ABOUT_MAX_LENGTH = 256
PHONE_INPUT_MAX_LENGTH = 20

GITHUB_HOSTS = ("github.com", "www.github.com")
PHONE_PATTERN = re.compile(r"^(\+7|8)\d{10}$")
PHONE_SEPARATORS = re.compile(r"[\s\-()]")

AVATAR_SIZE = 256
AVATAR_FONT_PATH = (
    settings.BASE_DIR / "static" / "fonts" / "Neue_Haas_Grotesk_Display_Pro_75_Bold.otf"
)


class AvatarColor(StrEnum):
    LIGHT_BLUE = "#DCE8F7"
    DARK_BLUE = "#2F5D8A"
    LIGHT_GREEN = "#E3F1E1"
    DARK_GREEN = "#3A6B35"
    LIGHT_ORANGE = "#FBE7D3"
    DARK_ORANGE = "#9A5B1E"
    LIGHT_PURPLE = "#EFE1F5"
    DARK_PURPLE = "#6B3F86"
    LIGHT_PINK = "#FDE2E4"
    DARK_RED = "#9B3B47"
    LIGHT_TEAL = "#E0F2F1"
    DARK_TEAL = "#2E6F69"
    LIGHT_YELLOW = "#F5F0D7"
    DARK_OLIVE = "#7A6A1F"
    LIGHT_GRAY = "#E8E8EE"
    DARK_GRAY = "#44475A"


AVATAR_PALETTE = (
    (AvatarColor.LIGHT_BLUE, AvatarColor.DARK_BLUE),
    (AvatarColor.LIGHT_GREEN, AvatarColor.DARK_GREEN),
    (AvatarColor.LIGHT_ORANGE, AvatarColor.DARK_ORANGE),
    (AvatarColor.LIGHT_PURPLE, AvatarColor.DARK_PURPLE),
    (AvatarColor.LIGHT_PINK, AvatarColor.DARK_RED),
    (AvatarColor.LIGHT_TEAL, AvatarColor.DARK_TEAL),
    (AvatarColor.LIGHT_YELLOW, AvatarColor.DARK_OLIVE),
    (AvatarColor.LIGHT_GRAY, AvatarColor.DARK_GRAY),
)
