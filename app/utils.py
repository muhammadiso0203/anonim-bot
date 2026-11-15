"""Havola yasash va xabarni anonim uzatish."""
from __future__ import annotations

import logging
import time
from typing import Any, Optional

from aiogram import Bot, html
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramRetryAfter,
)
from aiogram.types import BufferedInputFile, Message

import config
from app import database as db, emoji_pack
from app.imagecard import render_card
from app.keyboards import incoming_kb
from app.locales import t

log = logging.getLogger(__name__)

#: /start havolasi uchun bot username'i — bot.py ishga tushganda to'ldiriladi
BOT_USERNAME: str = ""

#: Uzatish mumkin bo'lgan xabar turlari
ALLOWED_CONTENT = (
    "text",
    "photo",
    "video",
    "animation",
    "voice",
    "video_note",
    "audio",
    "document",
    "sticker",
    "location",
    "venue",
)

#: Sarlavhani (caption) qo'yib bo'ladigan turlar — bitta xabar bilan ketadi
CAPTION_CONTENT = ("photo", "video", "animation", "audio", "document")

#: Shu turdagi bezaklar bo'lsa xabar o'zgartirilmasdan, aynan nusxalanadi.
#: custom_emoji — premium emoji: uni bot o'zi yoza olmaydi (Fragment sharti),
#: lekin nusxalaganda asl ko'rinishida yetib boradi.
VERBATIM_ENTITIES = frozenset(
    {"custom_emoji", "blockquote", "expandable_blockquote"}
)

#: Anonimlikni buzadigan yoki nusxalanmaydigan turlar
FORBIDDEN_CONTENT = ("contact", "poll", "dice", "game", "story", "invoice", "paid_media")

#: Albom (bir nechta rasm/video birga) uchun yordamchi xotira
_albums: dict[tuple[str, int], float] = {}
_ALBUM_TTL = 60.0

#: relay_message natijalari
OK = "ok"                # yuborildi, tasdiq ko'rsatiladi
OK_SILENT = "ok_silent"  # albomning davomi — tasdiq takrorlanmaydi
FAIL = "fail"


async def custom_emoji_problem(exc: Exception) -> bool:
    """Premium emoji sabab xato bo'lsa — ularni o'chirib, True qaytaradi."""
    text = str(exc).lower()
    if "custom_emoji" in text or "custom emoji" in text or "entity" in text:
        if emoji_pack.has_custom():
            await emoji_pack.disable_custom()
            log.warning("Premium emoji ishlamadi, oddiy holatga qaytarildi: %s", exc)
            return True
    return False

CAPTION_LIMIT = 1024


def set_bot_username(username: str) -> None:
    global BOT_USERNAME
    BOT_USERNAME = username


def get_bot_username() -> str:
    return BOT_USERNAME


def user_link(code: str) -> str:
    return f"https://t.me/{BOT_USERNAME}?start={code}"


def display_name(row: Any) -> str:
    """Havola egasining ko'rinadigan nomi (u maxfiy emas)."""
    if row is None:
        return "—"
    name = (row["first_name"] or "").strip()
    if name:
        return html.quote(name)
    if row["username"]:
        return "@" + html.quote(row["username"])
    return "ID " + str(row["user_id"])


def content_kind(message: Message) -> Optional[str]:
    """Xabar turini qaytaradi, ruxsat etilmagan bo'lsa None."""
    for name in ALLOWED_CONTENT:
        if getattr(message, name, None):
            return name
    return None


def is_forbidden_content(message: Message) -> bool:
    return any(getattr(message, name, None) for name in FORBIDDEN_CONTENT)


def too_long(message: Message) -> bool:
    return len(message.text or message.caption or "") > config.MAX_TEXT_LEN


def needs_verbatim(message: Message) -> bool:
    """Premium emoji yoki sitata bor-yo'qligi — bunda xabar aynan nusxalanadi."""
    entities = list(message.entities or []) + list(message.caption_entities or [])
    return any(getattr(e, "type", None) in VERBATIM_ENTITIES for e in entities)


def rich_text(message: Message) -> str:
    """Xabar matni bezaklari (qalin, kursiv, havola, spoyler) bilan birga."""
    try:
        text = message.html_text
    except Exception:  # noqa: BLE001
        text = None
    if not text:
        text = html.quote(message.text or message.caption or "")
    return text


def _album_followup(message: Message, receiver_id: int) -> bool:
    """Albomning ikkinchi va keyingi elementlari uchun True."""
    group = getattr(message, "media_group_id", None)
    if not group:
        return False
    now = time.monotonic()
    if len(_albums) > 5_000:
        for key, ts in list(_albums.items()):
            if now - ts > _ALBUM_TTL:
                _albums.pop(key, None)
    key = (str(group), receiver_id)
    if key in _albums and now - _albums[key] < _ALBUM_TTL:
        _albums[key] = now
        return True
    _albums[key] = now
    return False


async def _send_card(bot: Bot, chat_id: int, text: str) -> Optional[int]:
    """Xabarni rasm qilib ham yuboradi (storiyaga tashlash uchun)."""
    if not config.SEND_IMAGE_CARD:
        return None
    buf = render_card(text, BOT_USERNAME)
    if buf is None:
        return None
    try:
        sent = await bot.send_photo(
            chat_id, BufferedInputFile(buf.getvalue(), filename="anon.png")
        )
        return sent.message_id
    except Exception as exc:  # noqa: BLE001
        log.debug("Rasm yuborilmadi: %s", exc)
        return None


async def relay_message(
    bot: Bot,
    message: Message,
    sender_id: int,
    receiver: Any,
    kind: str = "anon",
    parent_id: Optional[int] = None,
    _retry: bool = True,
) -> tuple[str, Optional[int]]:
    """Xabarni anonim holda qabul qiluvchiga uzatadi.

    `copy_message` ishlatiladi — qabul qiluvchi yuboruvchining ismini,
    username'ini yoki profilini ko'rmaydi. Natija: OK, OK_SILENT yoki FAIL.
    """
    receiver_id = int(receiver["user_id"])
    rlang = receiver["lang"]
    kind_name = content_kind(message) or "text"
    followup = _album_followup(message, receiver_id)

    key_text = "incoming_text" if kind == "anon" else "reply_text"
    key_media = "incoming_media" if kind == "anon" else "reply_media"

    mid: Optional[int] = None
    markup = None
    if not followup:
        mid = await db.add_message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            parent_id=parent_id,
            kind=kind,
            content=kind_name,
            body=message.text or message.caption,
        )
        markup = incoming_kb(rlang, mid, can_block=(kind == "anon"))

    verbatim = needs_verbatim(message)

    try:
        dest_id: int
        dest_id2: Optional[int] = None

        if message.text and not verbatim:
            sent = await bot.send_message(
                receiver_id,
                t(rlang, key_text, text=rich_text(message)),
                reply_markup=markup,
            )
            dest_id = sent.message_id

        elif kind_name in CAPTION_CONTENT and not followup and not verbatim:
            if message.caption:
                caption = t(rlang, key_text, text=rich_text(message))
            else:
                caption = t(rlang, key_media)
            sent = await bot.copy_message(
                chat_id=receiver_id,
                from_chat_id=message.chat.id,
                message_id=message.message_id,
                caption=caption[:CAPTION_LIMIT],
                parse_mode="HTML",
                reply_markup=markup,
            )
            dest_id = sent.message_id

        else:
            # Stiker, ovozli xabar, dumaloq video, joylashuv, albom davomi va
            # premium emojili xabarlar: alohida sarlavha + aynan nusxa.
            # Nusxalashda premium emoji va stikerlar asl holida yetib boradi.
            if not followup:
                header = await bot.send_message(receiver_id, t(rlang, key_media))
                dest_id2 = header.message_id
            sent = await bot.copy_message(
                chat_id=receiver_id,
                from_chat_id=message.chat.id,
                message_id=message.message_id,
                reply_markup=markup,
            )
            dest_id = sent.message_id

        if mid is not None:
            if config.AUTO_IMAGE_CARD and kind == "anon" and message.text and dest_id2 is None:
                dest_id2 = await _send_card(bot, receiver_id, message.text)
            await db.set_dest_msg_id(mid, dest_id, dest_id2)

        return (OK_SILENT if followup else OK), mid

    except TelegramForbiddenError:
        if mid is not None:
            await db.delete_message(mid)
        await db.mark_stopped(receiver_id, True)
        return FAIL, None
    except TelegramRetryAfter as exc:
        log.warning("Flood limit: %s", exc)
        if mid is not None:
            await db.delete_message(mid)
        return FAIL, None
    except TelegramBadRequest as exc:
        log.warning("Uzatib bo'lmadi (%s): %s", receiver_id, exc)
        if mid is not None:
            await db.delete_message(mid)
        if _retry and await custom_emoji_problem(exc):
            return await relay_message(
                bot, message, sender_id, receiver, kind, parent_id, _retry=False
            )
        return FAIL, None
