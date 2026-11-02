import random
from io import BytesIO
from uuid import uuid4

from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

AVATAR_SIZE = 256
FONT_PATH = settings.BASE_DIR / "static" / "fonts" / "Neue_Haas_Grotesk_Display_Pro_75_Bold.otf"
PALETTE = (
    ("#DCE8F7", "#2F5D8A"),
    ("#E3F1E1", "#3A6B35"),
    ("#FBE7D3", "#9A5B1E"),
    ("#EFE1F5", "#6B3F86"),
    ("#FDE2E4", "#9B3B47"),
    ("#E0F2F1", "#2E6F69"),
    ("#F5F0D7", "#7A6A1F"),
    ("#E8E8EE", "#44475A"),
)


def _load_font(size):
    try:
        return ImageFont.truetype(str(FONT_PATH), size)
    except OSError:
        return ImageFont.load_default(size=size)


def generate_avatar(name):
    letter = (name or "").strip()[:1].upper() or "?"
    background, foreground = random.choice(PALETTE)
    image = Image.new("RGB", (AVATAR_SIZE, AVATAR_SIZE), background)
    draw = ImageDraw.Draw(image)
    draw.text(
        (AVATAR_SIZE / 2, AVATAR_SIZE / 2),
        letter,
        fill=foreground,
        font=_load_font(AVATAR_SIZE // 2),
        anchor="mm",
    )
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue(), name=f"avatar_{uuid4().hex}.png")
