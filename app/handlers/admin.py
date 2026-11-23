"""Tugmali admin panel: statistika, broadcast, adminlar, emojilar."""
from __future__ import annotations

import asyncio
import csv
import io
import logging
import os
import sqlite3
import tempfile
from datetime import datetime, timezone
from typing import Any, Optional

from aiogram import Bot, Router, html
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError, TelegramRetryAfter
from aiogram.filters import Command, Filter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    InlineKeyboardMarkup,
    Message,
    TelegramObject,
)

import config
from app import database as db, emoji_pack, settings as bot_settings
from app.keyboards import (
    AdminCB,
    EmojiCB,
    admin_back_kb,
    admin_kb,
    admins_kb,
    banned_kb,
    bc_preview_kb,
    bc_stop_kb,
    bc_target_kb,
    bot_settings_kb,
    channels_kb,
    daily_kb,
    emoji_item_kb,
    emoji_list_kb,
    users_kb,
)
from app.locales import alert, t
from app.states import AdminAdd, AdminBroadcast, AdminChannel, EmojiSet

log = logging.getLogger(__name__)

#: Broadcast'ni to'xtatgan adminlar
_bc_stop: set[int] = set()


class IsAdmin(Filter):
    """.env dagi asosiy adminlar + bazaga qo'shilganlar."""

    async def __call__(self, event: TelegramObject) -> bool:
        user = getattr(event, "from_user", None)
        return user is not None and await db.is_admin(user.id)


router = Router(name="admin")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


# ------------------------------------------------------------- ko'rinishlar

async def _home_view(lang: str) -> tuple[str, InlineKeyboardMarkup]:
    stats = await db.global_stats()
    admins = len(await db.all_admin_ids())
    text = t(lang, "admin_home", users=stats["users"], messages=stats["messages"], admins=admins)
    return text, admin_kb(lang)


async def _stats_view(lang: str) -> tuple[str, InlineKeyboardMarkup]:
    return t(lang, "admin_stats", **await db.global_stats()), admin_back_kb(lang)


USERS_PER_PAGE = 10


def _user_name(row) -> str:
    name = (row["first_name"] or "").strip()
    shown = html.quote(name) if name else ""
    if row["username"]:
        tag = "@" + html.quote(row["username"])
        shown = f"{shown} ({tag})" if shown else tag
    return shown or "—"


async def _users_view(lang: str, page: int = 0) -> tuple[str, InlineKeyboardMarkup]:
    total = await db.users_count()
    if total == 0:
        return t(lang, "users_empty"), admin_back_kb(lang)

    pages = max(1, (total + USERS_PER_PAGE - 1) // USERS_PER_PAGE)
    page = max(0, min(page, pages - 1))
    rows = await db.users_page(USERS_PER_PAGE, page * USERS_PER_PAGE)
    stats = await db.global_stats()

    lines = [
        t(
            lang,
            "users_row",
            num=page * USERS_PER_PAGE + i,
            name=_user_name(row),
            uid=row["user_id"],
            got=row["got"],
            sent=row["sent"],
            date=(row["created_at"] or "")[:10],
        )
        for i, row in enumerate(rows, start=1)
    ]
    text = t(
        lang,
        "users_title",
        total=total,
        active=stats["active_users"],
        stopped=total - stats["active_users"],
        today=stats["new_today"],
        rows="\n".join(lines),
    )
    return text, users_kb(lang, page, pages)


def _users_csv(rows: list) -> bytes:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(
        ["user_id", "username", "first_name", "lang", "accepting",
         "stopped_bot", "created_at", "received", "sent", "code"]
    )
    for row in rows:
        writer.writerow([
            row["user_id"], row["username"] or "", row["first_name"] or "",
            row["lang"], row["accepting"], row["stopped_bot"],
            row["created_at"], row["got"], row["sent"], row["code"],
        ])
    # utf-8-sig — Excel kirill/o'zbek harflarini to'g'ri ochishi uchun
    return buf.getvalue().encode("utf-8-sig")


async def _admins_view(lang: str) -> tuple[str, InlineKeyboardMarkup]:
    rows = await db.admin_rows()
    return t(lang, "admins_title"), admins_kb(lang, rows, list(config.ADMINS))


def _emoji_view(lang: str) -> tuple[str, InlineKeyboardMarkup]:
    """Matnda — hozirgi (premium) ko'rinishi, tugmalarda — tanlash uchun emojilar."""
    preview = emoji_pack.for_text(" ".join(e for e, _ in emoji_pack.EDITABLE))
    items = [(idx, emoji) for idx, (emoji, _title) in enumerate(emoji_pack.EDITABLE)]
    return t(lang, "emoji_title", preview=preview), emoji_list_kb(lang, items)


async def _channels_view(lang: str) -> tuple[str, InlineKeyboardMarkup]:
    rows = await db.channels()
    if not rows:
        return t(lang, "channels_empty"), channels_kb(lang, [])
    return t(lang, "channels_title", count=len(rows)), channels_kb(lang, rows)


async def _banned_view(lang: str) -> tuple[str, InlineKeyboardMarkup]:
    rows = await db.banned_rows()
    if not rows:
        return t(lang, "banned_empty"), admin_back_kb(lang)
    return t(lang, "banned_title", count=len(rows)), banned_kb(lang, rows)


def _settings_view(lang: str) -> tuple[str, InlineKeyboardMarkup]:
    return t(lang, "bot_settings_title"), bot_settings_kb(lang)


async def _daily_view(lang: str, days: int) -> tuple[str, InlineKeyboardMarkup]:
    days = 30 if days >= 30 else 7
    rows = await db.daily_stats(days)
    lines = [f"{'sana':<6}{'yangi':>6}{'xabar':>7}{'otish':>7}"]
    for row in rows:
        lines.append(
            f"{row['date'][5:]:<6}{row['users']:>6}{row['messages']:>7}{row['views']:>7}"
        )
    lines.append(
        f"{'jami':<6}{sum(r['users'] for r in rows):>6}"
        f"{sum(r['messages'] for r in rows):>7}{sum(r['views'] for r in rows):>7}"
    )
    return t(lang, "daily_title", days=days, chart="\n".join(lines)), daily_kb(lang, days)


def _make_backup() -> bytes:
    """Bazaning xavfsiz nusxasi (bot ishlab turganda ham to'g'ri chiqadi)."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        src = sqlite3.connect(f"file:{config.DB_PATH}?mode=ro", uri=True)
        dst = sqlite3.connect(path)
        try:
            with dst:
                src.backup(dst)
        finally:
            dst.close()
            src.close()
        with open(path, "rb") as fh:
            return fh.read()
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


async def _resolve_channel(bot: Bot, message: Message):
    """Forward qilingan post yoki @nom bo'yicha kanalni topadi."""
    chat = None
    origin = getattr(message, "forward_origin", None)
    if origin is not None:
        chat = getattr(origin, "chat", None)
    if chat is None:
        chat = getattr(message, "forward_from_chat", None)

    ident: Any = chat.id if chat is not None else None
    if ident is None:
        text = (message.text or "").strip()
        if text.startswith("@") and len(text) > 1:
            ident = text
        elif text.lstrip("-").isdigit():
            ident = int(text)
    if ident is None:
        return None, None

    try:
        full = await bot.get_chat(ident)
        member = await bot.get_chat_member(full.id, bot.id)
    except Exception as exc:  # noqa: BLE001
        log.warning("Kanal topilmadi (%s): %s", ident, exc)
        return "not_admin", None
    if member.status not in ("administrator", "creator"):
        return "not_admin", None

    link = getattr(full, "invite_link", None)
    if not link and full.username:
        link = f"https://t.me/{full.username}"
    if not link:
        try:
            link = await bot.export_chat_invite_link(full.id)
        except Exception:  # noqa: BLE001
            link = None
    return full, link


async def _safe_edit(call: CallbackQuery, text: str, markup: InlineKeyboardMarkup) -> None:
    if call.message is None:
        return
    try:
        await call.message.edit_text(text, reply_markup=markup)
    except TelegramBadRequest as exc:
        if "not modified" in str(exc):
            return
        try:
            await call.message.answer(text, reply_markup=markup)
        except Exception:  # noqa: BLE001
            pass
    except Exception:  # noqa: BLE001
        pass


# ------------------------------------------------------------------ /admin

@router.message(Command("admin", "panel"))
async def cmd_admin(message: Message, state: FSMContext, lang: str) -> None:
    await state.clear()
    text, markup = await _home_view(lang)
    await message.answer(text, reply_markup=markup)


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, state: FSMContext, lang: str) -> None:
    await state.set_state(AdminBroadcast.writing)
    await message.answer(t(lang, "broadcast_prompt"))


# ------------------------------------------------------------ panel tugmalari

@router.callback_query(AdminCB.filter())
async def cb_admin(
    call: CallbackQuery, callback_data: AdminCB, state: FSMContext, lang: str, bot: Bot
) -> None:
    action = callback_data.action

    if action == "home":
        await state.clear()
        text, markup = await _home_view(lang)
    elif action == "stats":
        text, markup = await _stats_view(lang)
    elif action == "admins":
        text, markup = await _admins_view(lang)
    elif action == "users":
        text, markup = await _users_view(lang, callback_data.arg)
    elif action == "users_csv":
        rows = await db.users_all()
        await bot.send_document(
            call.from_user.id,
            BufferedInputFile(_users_csv(rows), filename="foydalanuvchilar.csv"),
            caption=t(lang, "users_csv_caption", total=len(rows)),
        )
        await call.answer()
        return
    elif action == "broadcast":
        await state.clear()
        counts = await db.broadcast_counts()
        await _safe_edit(call, t(lang, "bc_target"), bc_target_kb(lang, counts))
        await call.answer()
        return
    elif action == "bc_pick":
        await state.set_state(AdminBroadcast.writing)
        await state.update_data(bc_target=callback_data.arg)
        await _safe_edit(call, t(lang, "bc_ask"), admin_back_kb(lang))
        await call.answer()
        return
    elif action == "bc_send":
        await _run_broadcast(call, state, lang, bot)
        return
    elif action == "bc_stop":
        _bc_stop.add(call.from_user.id)
        await call.answer(alert(lang, "bc_stopped"), show_alert=True)
        return
    elif action == "channels":
        await state.clear()
        text, markup = await _channels_view(lang)
    elif action == "ch_add":
        await state.set_state(AdminChannel.writing)
        await _safe_edit(call, t(lang, "channel_add_prompt"), admin_back_kb(lang))
        await call.answer()
        return
    elif action == "ch_rm":
        await db.remove_channel(callback_data.arg)
        await call.answer(alert(lang, "channel_removed"))
        text, markup = await _channels_view(lang)
    elif action == "banned":
        await state.clear()
        text, markup = await _banned_view(lang)
    elif action == "unban":
        await db.unban_user(callback_data.arg)
        await call.answer(alert(lang, "unban_done"))
        text, markup = await _banned_view(lang)
    elif action == "rban":
        row = await db.get_message(callback_data.arg)
        if row is not None:
            await db.ban_user(int(row["sender_id"]), reason="shikoyat")
        await call.answer(alert(lang, "ban_done"), show_alert=True)
        if call.message is not None:
            try:
                await call.message.edit_reply_markup(reply_markup=None)
            except Exception:  # noqa: BLE001
                pass
        return
    elif action == "rskip":
        await call.answer(alert(lang, "report_closed"))
        if call.message is not None:
            try:
                await call.message.edit_reply_markup(reply_markup=None)
            except Exception:  # noqa: BLE001
                pass
        return
    elif action == "settings":
        await state.clear()
        text, markup = _settings_view(lang)
    elif action == "set":
        toggles = bot_settings.TOGGLES
        if 0 <= callback_data.arg < len(toggles):
            await bot_settings.toggle(toggles[callback_data.arg][0])
        text, markup = _settings_view(lang)
    elif action == "daily":
        await state.clear()
        text, markup = await _daily_view(lang, callback_data.arg or 7)
    elif action == "backup":
        await call.answer()
        try:
            data_bytes = await asyncio.to_thread(_make_backup)
            stats = await db.global_stats()
            await bot.send_document(
                call.from_user.id,
                BufferedInputFile(
                    data_bytes,
                    filename=f"anonbot-{datetime.now(timezone.utc):%Y%m%d-%H%M}.db",
                ),
                caption=t(
                    lang,
                    "backup_caption",
                    date=f"{datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC",
                    users=stats["users"],
                    messages=stats["messages"],
                ),
            )
        except Exception as exc:  # noqa: BLE001
            log.exception("Zaxira olinmadi")
            await bot.send_message(
                call.from_user.id, t(lang, "backup_failed", error=str(exc)[:200])
            )
        return
    elif action == "add":
        await state.set_state(AdminAdd.writing)
        await _safe_edit(call, t(lang, "admin_add_prompt"), admin_back_kb(lang))
        await call.answer()
        return
    elif action == "rm":
        await db.remove_admin(callback_data.arg)
        await call.answer(alert(lang, "admin_removed", uid=callback_data.arg), show_alert=True)
        text, markup = await _admins_view(lang)
    elif action == "owner":
        await call.answer(alert(lang, "admin_is_owner"), show_alert=True)
        return
    elif action == "close":
        await state.clear()
        await call.answer()
        if call.message is not None:
            try:
                await call.message.delete()
            except Exception:  # noqa: BLE001
                pass
        return
    else:
        await call.answer()
        return

    await _safe_edit(call, text, markup)
    await call.answer()


# ------------------------------------------------------------ admin qo'shish

def _extract_user_id(message: Message) -> Optional[int]:
    origin = getattr(message, "forward_origin", None)
    if origin is not None:
        sender = getattr(origin, "sender_user", None)
        if sender is not None:
            return int(sender.id)
    legacy = getattr(message, "forward_from", None)
    if legacy is not None:
        return int(legacy.id)
    text = (message.text or "").strip()
    if text.isdigit():
        return int(text)
    return None


@router.message(AdminAdd.writing)
async def on_admin_add(message: Message, state: FSMContext, lang: str) -> None:
    uid = _extract_user_id(message)
    if uid is None:
        hidden = getattr(message, "forward_sender_name", None) or getattr(
            getattr(message, "forward_origin", None), "sender_user_name", None
        )
        await message.answer(
            t(lang, "admin_forward_hidden") if hidden else t(lang, "admin_bad_id")
        )
        return

    await state.clear()
    if await db.is_admin(uid):
        await message.answer(t(lang, "admin_exists"))
    else:
        await db.add_admin(uid, message.from_user.id)
        await message.answer(t(lang, "admin_added", uid=uid))
    text, markup = await _home_view(lang)
    await message.answer(text, reply_markup=markup)


# ------------------------------------------------------------------ emojilar

@router.callback_query(EmojiCB.filter())
async def cb_emoji(
    call: CallbackQuery, callback_data: EmojiCB, state: FSMContext, lang: str
) -> None:
    action = callback_data.action
    idx = callback_data.idx

    if action == "back":
        await state.clear()
        text, markup = _emoji_view(lang)
    elif action == "pick":
        if not 0 <= idx < len(emoji_pack.EDITABLE):
            await call.answer()
            return
        emoji, title = emoji_pack.EDITABLE[idx]
        await state.set_state(EmojiSet.waiting)
        await state.update_data(emoji_idx=idx)
        await _safe_edit(
            call,
            t(lang, "emoji_pick", emoji=emoji, title=title),
            emoji_item_kb(lang, idx),
        )
        await call.answer()
        return
    elif action == "reset":
        if 0 <= idx < len(emoji_pack.EDITABLE):
            await emoji_pack.reset(emoji_pack.EDITABLE[idx][0])
        await state.clear()
        await call.answer(alert(lang, "emoji_reset_ok"))
        text, markup = _emoji_view(lang)
    elif action == "resetall":
        await emoji_pack.reset_all()
        await state.clear()
        await call.answer(alert(lang, "emoji_resetall_ok"))
        text, markup = _emoji_view(lang)
    else:
        await call.answer()
        return

    await _safe_edit(call, text, markup)
    await call.answer()


def _custom_emoji(message: Message) -> Optional[tuple[str, str]]:
    """(premium emoji ID, uning oddiy ko'rinishi).

    Telegram belgi o'rnini UTF-16 birliklarida beradi, shuning uchun
    kesish ham shu kodlashda bajariladi — aks holda emoji buzilib chiqadi.
    """
    text = message.text or message.caption or ""
    entities = list(message.entities or []) + list(message.caption_entities or [])
    for entity in entities:
        if entity.type == "custom_emoji" and entity.custom_emoji_id:
            raw = text.encode("utf-16-le")
            base = raw[
                entity.offset * 2 : (entity.offset + entity.length) * 2
            ].decode("utf-16-le", "ignore")
            return str(entity.custom_emoji_id), base.strip()
    return None


def _looks_like_emoji(text: str) -> bool:
    text = text.strip()
    return 0 < len(text) <= 8 and not any(ch.isalnum() or ch.isspace() for ch in text)


@router.message(EmojiSet.waiting)
async def on_emoji_set(message: Message, state: FSMContext, lang: str, bot: Bot) -> None:
    data = await state.get_data()
    idx = int(data.get("emoji_idx", -1))
    if not 0 <= idx < len(emoji_pack.EDITABLE):
        await state.clear()
        return
    emoji, _title = emoji_pack.EDITABLE[idx]

    found = _custom_emoji(message)
    text = (message.text or "").strip()

    if found:
        custom_id, base = found
        base = base or emoji
        # Avval sinab ko'ramiz: bu bot premium emoji yubora oladimi?
        try:
            # Sinov xabari ataylab o'chirilmaydi — Telegram premium emojini
            # ba'zan xatosiz, lekin oddiy ko'rinishda yuboradi. Buni faqat
            # ko'z bilan tekshirish mumkin.
            tag = f'<tg-emoji emoji-id="{custom_id}">{base}</tg-emoji>'
            await bot.send_message(message.chat.id, f"{tag} {tag} {tag}")
        except TelegramBadRequest:
            await state.clear()
            await message.answer(t(lang, "emoji_custom_failed"))
            await emoji_pack.disable_custom()
            txt, markup = _emoji_view(lang)
            await message.answer(txt, reply_markup=markup)
            return
        await emoji_pack.save(emoji, "custom", custom_id, base)
        await state.clear()
        await message.answer(
            t(lang, "emoji_saved_custom", emoji=emoji, new=custom_id, base=base)
        )
    elif _looks_like_emoji(text):
        await emoji_pack.save(emoji, "plain", text)
        await state.clear()
        await message.answer(t(lang, "emoji_saved", emoji=emoji, new=text))
    else:
        await message.answer(t(lang, "emoji_need_emoji"))
        return

    txt, markup = _emoji_view(lang)
    await message.answer(txt, reply_markup=markup)


# ----------------------------------------------------------------- broadcast

@router.message(AdminBroadcast.writing)
async def bc_collect(message: Message, state: FSMContext, lang: str) -> None:
    """Yuboriladigan xabar olindi — endi ko'rib chiqish."""
    if (message.text or "").strip() in ("/cancel", "/stop", "/admin"):
        await state.clear()
        await message.answer(t(lang, "cancelled"))
        return

    data = await state.get_data()
    target = int(data.get("bc_target", 0))
    await state.update_data(bc_chat=message.chat.id, bc_msg=message.message_id)
    count = len(await db.broadcast_targets(target))
    await message.answer(t(lang, "bc_preview", n=count), reply_markup=bc_preview_kb(lang))


async def _run_broadcast(
    call: CallbackQuery, state: FSMContext, lang: str, bot: Bot
) -> None:
    data = await state.get_data()
    chat_id = data.get("bc_chat")
    msg_id = data.get("bc_msg")
    target = int(data.get("bc_target", 0))
    await state.clear()
    if not chat_id or not msg_id:
        await call.answer(alert(lang, "msg_not_found"), show_alert=True)
        return

    await call.answer()
    admin_id = call.from_user.id
    _bc_stop.discard(admin_id)
    targets = await db.broadcast_targets(target)
    total = len(targets)

    progress = await bot.send_message(
        admin_id,
        t(lang, "bc_progress", done=0, total=total, ok=0, failed=0),
        reply_markup=bc_stop_kb(lang),
    )

    ok = failed = 0
    for done, uid in enumerate(targets, start=1):
        if admin_id in _bc_stop:
            break
        try:
            await bot.copy_message(chat_id=uid, from_chat_id=chat_id, message_id=msg_id)
            ok += 1
        except TelegramRetryAfter as exc:
            await asyncio.sleep(exc.retry_after + 1)
            try:
                await bot.copy_message(chat_id=uid, from_chat_id=chat_id, message_id=msg_id)
                ok += 1
            except Exception:  # noqa: BLE001
                failed += 1
        except TelegramForbiddenError:
            await db.mark_stopped(uid, True)
            failed += 1
        except Exception as exc:  # noqa: BLE001
            log.warning("Broadcast xatosi (%s): %s", uid, exc)
            failed += 1

        if done % 25 == 0:
            try:
                await progress.edit_text(
                    t(lang, "bc_progress", done=done, total=total, ok=ok, failed=failed),
                    reply_markup=bc_stop_kb(lang),
                )
            except Exception:  # noqa: BLE001
                pass
        await asyncio.sleep(0.05)

    _bc_stop.discard(admin_id)
    try:
        await progress.edit_text(t(lang, "broadcast_done", ok=ok, failed=failed))
    except Exception:  # noqa: BLE001
        await bot.send_message(admin_id, t(lang, "broadcast_done", ok=ok, failed=failed))

    text, markup = await _home_view(lang)
    await bot.send_message(admin_id, text, reply_markup=markup)


# ------------------------------------------------------- kanal qo'shish

@router.message(AdminChannel.writing)
async def on_channel_add(
    message: Message, state: FSMContext, lang: str, bot: Bot
) -> None:
    if (message.text or "").strip() in ("/cancel", "/admin"):
        await state.clear()
        await message.answer(t(lang, "cancelled"))
        return

    chat, link = await _resolve_channel(bot, message)
    if chat is None:
        await message.answer(t(lang, "channel_bad"))
        return
    if chat == "not_admin":
        await message.answer(t(lang, "channel_not_admin"))
        return

    await state.clear()
    await db.add_channel(
        chat_id=chat.id,
        title=chat.title,
        username=chat.username,
        invite_link=link,
        added_by=message.from_user.id,
    )
    await message.answer(t(lang, "channel_added", title=html.quote(chat.title or "")))
    text, markup = await _channels_view(lang)
    await message.answer(text, reply_markup=markup)
