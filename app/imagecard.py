"""Anonim xabarni rasm qilib chizish (storiyaga ulashish uchun).

@anonAskBot kelgan har bir xabarni shunday rasm qilib ham yuboradi.
Pillow o'rnatilmagan bo'lsa — bot baribir ishlayveradi, shunchaki rasm yuborilmaydi.
"""
from __future__ import annotations

import logging
from io import BytesIO
from typing import Optional

log = logging.getLogger(__name__)

try:
    from PIL import Image, ImageDraw, ImageFont

    PIL_OK = True
except ImportError:  # pragma: no cover
    PIL_OK = False

SIZE = 1080
MARGIN = 90
CARD_RADIUS = 56

# Gradient ranglari (chapdan o'ngga, yuqoridan pastga)
GRADIENT_TOP = (124, 92, 255)      # binafsha
GRADIENT_BOTTOM = (96, 173, 255)   # moviy
CARD_BG = (255, 255, 255)
TEXT_COLOR = (28, 28, 38)
BADGE_BG = (56, 150, 255)
BADGE_TEXT = (255, 255, 255)

#: Shrift qidiriladigan joylar — Windows, Linux va macOS
FONT_CANDIDATES = (
    "C:/Windows/Fonts/segoeui.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
)
FONT_CANDIDATES_BOLD = (
    "C:/Windows/Fonts/segoeuib.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
)


def _load_font(size: int, bold: bool = False):
    for path in FONT_CANDIDATES_BOLD if bold else FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default(size)


def _gradient(width: int, height: int) -> "Image.Image":
    base = Image.new("RGB", (1, height))
    px = base.load()
    for y in range(height):
        k = y / max(1, height - 1)
        px[0, y] = (
            int(GRADIENT_TOP[0] + (GRADIENT_BOTTOM[0] - GRADIENT_TOP[0]) * k),
            int(GRADIENT_TOP[1] + (GRADIENT_BOTTOM[1] - GRADIENT_TOP[1]) * k),
            int(GRADIENT_TOP[2] + (GRADIENT_BOTTOM[2] - GRADIENT_TOP[2]) * k),
        )
    return base.resize((width, height))


def _wrap(draw, text: str, font, max_width: int) -> list[str]:
    """So'zlar bo'yicha o'rash; juda uzun so'z harflab bo'linadi."""
    lines: list[str] = []
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            lines.append("")
            continue
        words, line = paragraph.split(), ""
        for word in words:
            probe = f"{line} {word}".strip()
            if draw.textlength(probe, font=font) <= max_width:
                line = probe
                continue
            if line:
                lines.append(line)
            while draw.textlength(word, font=font) > max_width and len(word) > 1:
                cut = len(word)
                while cut > 1 and draw.textlength(word[:cut], font=font) > max_width:
                    cut -= 1
                lines.append(word[:cut])
                word = word[cut:]
            line = word
        if line:
            lines.append(line)
    return lines or [""]


def _draw_logo(draw, cx: int, cy: int, r: int) -> None:
    """Oddiy konvert belgisi — doira ichida."""
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=BADGE_BG)
    w, h = int(r * 1.05), int(r * 0.72)
    x0, y0, x1, y1 = cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2
    draw.rounded_rectangle((x0, y0, x1, y1), radius=max(4, r // 8), fill=(255, 255, 255))
    draw.line((x0 + 4, y0 + 6, cx, cy + h // 6), fill=BADGE_BG, width=max(3, r // 12))
    draw.line((x1 - 4, y0 + 6, cx, cy + h // 6), fill=BADGE_BG, width=max(3, r // 12))


def render_card(text: str, bot_username: str = "") -> Optional[BytesIO]:
    """Xabar matnidan ulashsa bo'ladigan rasm yasaydi. Xato bo'lsa — None."""
    if not PIL_OK:
        return None
    try:
        text = (text or "").strip()
        if not text:
            return None
        if len(text) > 400:
            text = text[:397] + "..."

        img = _gradient(SIZE, SIZE)
        draw = ImageDraw.Draw(img)

        # Fon naqshi — yengil "?" belgilar
        pattern_font = _load_font(64, bold=True)
        for row in range(9):
            for col in range(7):
                x = -40 + col * 170 + (85 if row % 2 else 0)
                draw.text((x, 20 + row * 130), "?", font=pattern_font,
                          fill=(255, 255, 255, 255), stroke_width=0)
        img = Image.blend(img, _gradient(SIZE, SIZE), 0.82)
        draw = ImageDraw.Draw(img)

        # Matn shriftini joyiga qarab tanlash
        card_w = SIZE - MARGIN * 2
        text_w = card_w - 110
        for font_size in range(76, 27, -4):
            font = _load_font(font_size, bold=True)
            lines = _wrap(draw, text, font, text_w)
            line_h = int(font_size * 1.32)
            if len(lines) * line_h <= 560:
                break

        card_h = max(260, len(lines) * line_h + 120)
        card_x0 = MARGIN
        card_y0 = (SIZE - card_h) // 2
        draw.rounded_rectangle(
            (card_x0, card_y0, card_x0 + card_w, card_y0 + card_h),
            radius=CARD_RADIUS,
            fill=CARD_BG,
        )

        y = card_y0 + (card_h - len(lines) * line_h) // 2
        for line in lines:
            lw = draw.textlength(line, font=font)
            draw.text((SIZE // 2 - lw / 2, y), line, font=font, fill=TEXT_COLOR)
            y += line_h

        # Logo — kartaning tepasida
        _draw_logo(draw, SIZE // 2, card_y0, 58)

        # Pastdagi @username yorlig'i
        if bot_username:
            label = f"@{bot_username}"
            bfont = _load_font(34, bold=True)
            bw = draw.textlength(label, font=bfont)
            pad_x, pad_y = 30, 16
            bx0 = SIZE // 2 - (bw + pad_x * 2) / 2
            by0 = card_y0 + card_h - 28
            draw.rounded_rectangle(
                (bx0, by0, bx0 + bw + pad_x * 2, by0 + 34 + pad_y * 2),
                radius=30,
                fill=BADGE_BG,
            )
            draw.text((bx0 + pad_x, by0 + pad_y - 2), label, font=bfont, fill=BADGE_TEXT)

        buf = BytesIO()
        img.save(buf, format="PNG", optimize=True)
        buf.seek(0)
        return buf
    except Exception as exc:  # noqa: BLE001
        log.warning("Rasm yasalmadi: %s", exc)
        return None
