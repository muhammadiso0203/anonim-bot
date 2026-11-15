"""Tugmali admin panel: statistika, broadcast, adminlar, emojilar."""
from __future__ import annotations

import asyncio
import logging
from typing import Optional

from aiogram import Bot, Router
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError, TelegramRetryAfter
from aiogram.filters import Command, Filter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message, TelegramObject

import config
from app import database as db, emoji_pack
from app.keyboards import AdminCB, EmojiCB, admin_back_kb, admin_kb, admins_kb, emoji_item_kb, emoji_list_kb
from app.locales import t
from app.states import AdminAdd, AdminBroadcast, EmojiSet

log = logging.getLogger(__name__)


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


async def _admins_view(lang: str) -> tuple[str, InlineKeyboardMarkup]:
    rows = await db.admin_rows()
    return t(lang, "admins_title"), admins_kb(lang, rows, list(config.ADMINS))


def _emoji_view(lang: str) -> tuple[str, InlineKeyboardMarkup]:
    """Matnda — hozirgi (premium) ko'rinishi, tugmalarda — tanlash uchun emojilar."""
    preview = emoji_pack.for_text(" ".join(e for e, _ in emoji_pack.EDITABLE))
    items = [(idx, emoji) for idx, (emoji, _title) in enumerate(emoji_pack.EDITABLE)]
    return t(lang, "emoji_title", preview=preview), emoji_list_kb(lang, items)


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
    call: CallbackQuery, callback_data: AdminCB, state: FSMContext, lang: str
) -> None:
    action = callback_data.action

    if action == "home":
        await state.clear()
        text, markup = await _home_view(lang)
    elif action == "stats":
        text, markup = await _stats_view(lang)
    elif action == "admins":
        text, markup = await _admins_view(lang)
    elif action == "broadcast":
        await state.set_state(AdminBroadcast.writing)
        await _safe_edit(call, t(lang, "broadcast_prompt"), admin_back_kb(lang))
        await call.answer()
        return
    elif action == "add":
        await state.set_state(AdminAdd.writing)
        await _safe_edit(call, t(lang, "admin_add_prompt"), admin_back_kb(lang))
        await call.answer()
        return
    elif action == "rm":
        await db.remove_admin(callback_data.arg)
        await call.answer(t(lang, "admin_removed", uid=callback_data.arg), show_alert=True)
        text, markup = await _admins_view(lang)
    elif action == "owner":
        await call.answer(t(lang, "admin_is_owner"), show_alert=True)
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
        await call.answer(t(lang, "emoji_reset_ok"))
        text, markup = _emoji_view(lang)
    elif action == "resetall":
        await emoji_pack.reset_all()
        await state.clear()
        await call.answer(t(lang, "emoji_resetall_ok"))
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
async def do_broadcast(message: Message, state: FSMContext, lang: str, bot: Bot) -> None:
    if (message.text or "").strip() in ("/cancel", "/stop", "/admin"):
        await state.clear()
        await message.answer(t(lang, "cancelled"))
        return

    await state.clear()
    await message.answer(t(lang, "broadcast_started"))

    ok = failed = 0
    for uid in await db.all_user_ids():
        try:
            await bot.copy_message(
                chat_id=uid, from_chat_id=message.chat.id, message_id=message.message_id
            )
            ok += 1
        except TelegramRetryAfter as exc:
            await asyncio.sleep(exc.retry_after + 1)
            try:
                await bot.copy_message(
                    chat_id=uid, from_chat_id=message.chat.id, message_id=message.message_id
                )
                ok += 1
            except Exception:  # noqa: BLE001
                failed += 1
        except TelegramForbiddenError:
            await db.mark_stopped(uid, True)
            failed += 1
        except Exception as exc:  # noqa: BLE001
            log.warning("Broadcast xatosi (%s): %s", uid, exc)
            failed += 1
        await asyncio.sleep(0.05)

    await message.answer(t(lang, "broadcast_done", ok=ok, failed=failed))
    text, markup = await _home_view(lang)
    await message.answer(text, reply_markup=markup)
