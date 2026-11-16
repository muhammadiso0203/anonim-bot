"""Bot matnlaridagi emojilarni almashtirish (oddiy yoki premium emoji).

Admin /admin -> Emojilar bo'limidan har bir emojini boshqasiga almashtiradi.
Premium (custom) emoji Telegram tomonidan faqat Fragment'da username sotib
olgan botlarga ruxsat etilgan — aks holda xabar yuborilmaydi va bot
avtomatik ravishda oddiy emojiga qaytadi.
"""
from __future__ import annotations

import logging
from typing import Optional

log = logging.getLogger(__name__)

SETTING_PREFIX = "emoji:"

#: Sozlash mumkin bo'lgan emojilar: (emoji, nima uchun ishlatiladi)
EDITABLE: tuple[tuple[str, str], ...] = (
    ("💬", "Yangi xabar"),
    ("✉️", "Javob keldi"),
    ("↩️", "Javob berish"),
    ("✍️", "Yozish"),
    ("🚀", "Boshlash"),
    ("🔗", "Havola"),
    ("✅", "Tasdiq"),
    ("🖼", "Rasm qilish"),
    ("🗑", "O'chirish"),
    ("🚫", "Bloklash"),
    ("📊", "Statistika"),
    ("👀", "Havola o'tishlari"),
    ("👑", "Mashhurlik"),
    ("⭐️", "Yulduz"),
    ("💡", "G'oya"),
    ("🔔", "Qabul yoqilgan"),
    ("🔕", "Qabul o'chirilgan"),
    ("⚙️", "Sozlamalar"),
    ("🌐", "Til"),
    ("❌", "Bekor qilish"),
    ("❓", "Yordam"),
    ("👤", "Foydalanuvchi"),
    ("⚠️", "Ogohlantirish"),
    ("ℹ️", "Ma'lumot"),
    ("👇", "Pastga ishora"),
    ("☝️", "Yuqoriga ishora"),
    ("👉", "O'ngga ishora"),
    ("📱", "Profil: telefon"),
    ("🎵", "Profil: TikTok"),
    ("📷", "Profil: Instagram"),
    ("🔹", "Ro'yxat belgisi"),
    ("🙃", "Hazil"),
    ("🐢", "Sekinroq yozing"),
    ("⬅️", "Orqaga"),
    ("♻️", "Asliga qaytarish"),
    ("🛠", "Admin panel"),
    ("👮", "Adminlar"),
    ("👥", "Foydalanuvchilar"),
    ("📣", "Xabar yuborish"),
    ("📢", "Majburiy obuna"),
    ("➕", "Qo'shish"),
    ("🔒", "Asosiy admin"),
    ("😀", "Emojilar"),
    ("🔄", "Yangilash"),
    ("⛔️", "To'xtatish"),
    ("🆕", "Yangi"),
    ("📅", "Sana"),
    ("⏳", "Kutish"),
    ("📤", "Yuborildi"),
    ("💾", "Zaxira nusxa"),
    ("📈", "Kunlik statistika"),
)

EDITABLE_MAP = dict(EDITABLE)

#: emoji -> (kind, value, fallback)
#:   plain  : value = yangi emoji, fallback = o'sha emoji
#:   custom : value = premium emoji ID, fallback = o'sha premium emojining
#:            oddiy ko'rinishi (admin yuborgan belgi). Premium ishlamasa
#:            shu belgi ko'rinadi — shuning uchun emoji baribir o'zgaradi.
_cache: dict[str, tuple[str, str, str]] = {}


def _parse(raw: str, original: str) -> Optional[tuple[str, str, str]]:
    if not raw or ":" not in raw:
        return None
    kind, value = raw.split(":", 1)
    if kind not in ("plain", "custom") or not value:
        return None
    if kind == "plain":
        return "plain", value, value
    emoji_id, _, fallback = value.partition("|")
    if not emoji_id:
        return None
    return "custom", emoji_id, (fallback or original)


def set_cache(raw_settings: dict[str, str]) -> None:
    """Bazadan o'qilgan sozlamalarni xotiraga joylaydi."""
    _cache.clear()
    for key, raw in raw_settings.items():
        emoji = key[len(SETTING_PREFIX):]
        if not emoji:
            continue
        parsed = _parse(raw, emoji)
        if parsed:
            _cache[emoji] = parsed


def current(emoji: str) -> Optional[tuple[str, str, str]]:
    return _cache.get(emoji)


def describe(emoji: str) -> str:
    """Tugmada ko'rsatish uchun: hozir nimaga almashtirilgan."""
    item = _cache.get(emoji)
    if item is None:
        return emoji
    kind, _value, fallback = item
    return fallback if kind == "plain" else fallback + "⭑"


def has_custom() -> bool:
    return any(kind == "custom" for kind, _v, _f in _cache.values())


def for_text(text: str) -> str:
    """Xabar matni uchun: premium emoji HTML tegiga o'raladi.

    Teg ichidagi belgi — admin yuborgan emojining oddiy ko'rinishi.
    Telegram premium emojini ko'rsata olmasa o'sha belgi chiqadi.
    """
    if not _cache or not text:
        return text
    for emoji, (kind, value, fallback) in _cache.items():
        if emoji not in text:
            continue
        if kind == "plain":
            text = text.replace(emoji, value)
        else:
            text = text.replace(
                emoji, f'<tg-emoji emoji-id="{value}">{fallback}</tg-emoji>'
            )
    return text


def for_button(text: str) -> str:
    """Tugma yozuvi: HTML ishlamaydi, shuning uchun oddiy ko'rinishi qo'yiladi."""
    if not _cache or not text:
        return text
    for emoji, (_kind, _value, fallback) in _cache.items():
        if emoji in text:
            text = text.replace(emoji, fallback)
    return text


def button_parts(raw_label: str) -> tuple[str, Optional[str]]:
    """Tugma uchun: (yozuv, icon_custom_emoji_id).

    raw_label — ALMASHTIRILMAGAN yozuv (asl emoji bilan). Agar yozuv
    boshidagi emoji premium emojiga almashtirilgan bo'lsa, u yozuvdan
    olib tashlanadi va alohida «icon» sifatida qaytariladi — Telegram uni
    tugma yozuvidan oldin chizadi (Bot API 9.4+).
    """
    if not raw_label:
        return raw_label, None
    for emoji, (kind, value, _fallback) in _cache.items():
        if kind == "custom" and raw_label.startswith(emoji):
            rest = raw_label[len(emoji):].lstrip()
            return for_button(rest), value
    return for_button(raw_label), None


async def load() -> None:
    """Bazadan o'qib xotiraga yuklaydi (bot ishga tushganda)."""
    from app import database as db

    try:
        set_cache(await db.settings_with_prefix(SETTING_PREFIX))
    except Exception as exc:  # noqa: BLE001
        log.warning("Emoji sozlamalari o'qilmadi: %s", exc)


async def save(emoji: str, kind: str, value: str, fallback: str = "") -> None:
    """kind='plain' -> value = yangi emoji.
    kind='custom' -> value = premium emoji ID, fallback = uning oddiy ko'rinishi."""
    from app import database as db

    raw = f"{kind}:{value}"
    if kind == "custom":
        raw = f"custom:{value}|{fallback or emoji}"
    await db.set_setting(SETTING_PREFIX + emoji, raw)
    await load()


async def reset(emoji: str) -> None:
    from app import database as db

    await db.set_setting(SETTING_PREFIX + emoji, None)
    await load()


async def reset_all() -> None:
    from app import database as db

    for emoji, _ in EDITABLE:
        await db.set_setting(SETTING_PREFIX + emoji, None)
    await load()


async def disable_custom() -> bool:
    """Premium emoji ishlamasa — hammasini oddiy holatga qaytaradi."""
    from app import database as db

    changed = False
    for emoji, (kind, _value, _fallback) in list(_cache.items()):
        if kind == "custom":
            await db.set_setting(SETTING_PREFIX + emoji, None)
            changed = True
    if changed:
        await load()
    return changed
