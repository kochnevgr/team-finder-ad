import random
from io import BytesIO
from uuid import uuid4

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

from core.constants import AVATAR_FONT_PATH, AVATAR_PALETTE, AVATAR_SIZE


def _load_font(size):
    try:
        return ImageFont.truetype(str(AVATAR_FONT_PATH), size)
    except OSError:
        return ImageFont.load_default(size=size)


def generate_avatar(name):
    letter = (name or "").strip()[:1].upper() or "?"
    background, foreground = random.choice(AVATAR_PALETTE)
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
