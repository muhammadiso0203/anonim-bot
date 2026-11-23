"""Anonim xabar yuborish, «surib» javob berish, rasm va o'chirish tugmalari."""
from __future__ import annotations

from typing import Any

from aiogram import Bot, F, Router, html
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from app import database as db
from app.imagecard import render_card
from app.keyboards import (
    CancelCB,
    MsgCB,
    cancel_kb,
    cancel_send_kb,
    report_kb,
    sent_kb,
    share_kb,
)
from app.locales import alert, t
from app.states import AnonReply, AnonSend
from app.utils import (
    FAIL,
    OK,
    album_route,
    content_kind,
    is_forbidden_content,
    relay_message,
    get_bot_username,
    too_long,
    user_link,
)

router = Router(name="anon")

#: Kelgan xabarga javob sifatida yuborilsa — muallif bloklanadi
BLOCK_COMMANDS = ("/block", "/bloklash", "/ban")


async def start_anon_session(
    message: Message, state: FSMContext, lang: str, target: Any
) -> None:
    """Foydalanuvchini «anonim yozish» holatiga o'tkazadi."""
    await state.set_state(AnonSend.writing)
    await state.update_data(target_id=int(target["user_id"]))
    await message.answer(t(lang, "anon_prompt"), reply_markup=cancel_send_kb(lang))


def _content_ok(message: Message) -> bool:
    return not is_forbidden_content(message) and content_kind(message) is not None


async def _can_send_to(message: Message, lang: str, target: Any, sender_id: int) -> bool:
    """O'ziga yozish ruxsat etilgan — faqat qabul qiluvchi holati tekshiriladi."""
    if target is None:
        await message.answer(t(lang, "user_not_found"))
        return False
    if not target["accepting"] and int(target["user_id"]) != sender_id:
        await message.answer(t(lang, "not_accepting"))
        return False
    if await db.is_blocked(int(target["user_id"]), sender_id):
        await message.answer(t(lang, "you_are_blocked"))
        return False
    return True


async def _show_own_link(message: Message, lang: str) -> None:
    """Xabar yuborilgandan keyin foydalanuvchiga o'z havolasini ko'rsatadi."""
    user = await db.get_user(message.from_user.id)
    if user is None:
        return
    link = user_link(user["code"])
    await message.answer(t(lang, "start_main", link=link), reply_markup=share_kb(lang, link))


async def _delete_pair(bot: Bot, chat_id: int, row) -> bool:
    """Xabar va uning rasmini qabul qiluvchi chatidan o'chiradi."""
    ok = False
    for msg_id in (row["dest_msg_id"], row["dest_msg_id2"]):
        if not msg_id:
            continue
        try:
            await bot.delete_message(chat_id, int(msg_id))
            ok = True
        except Exception:  # noqa: BLE001
            pass
    return ok


# --------------------------------------------------- anonim xabar yuborish

@router.message(AnonSend.writing)
async def on_anon_message(
    message: Message, state: FSMContext, lang: str, bot: Bot
) -> None:
    data = await state.get_data()
    target_id = data.get("target_id")
    if not target_id:
        await state.clear()
        await message.answer(t(lang, "msg_not_found"))
        return

    target = await db.get_user(int(target_id))
    sender_id = message.from_user.id

    if not await _can_send_to(message, lang, target, sender_id):
        await state.clear()
        return
    if not _content_ok(message) or too_long(message):
        await message.answer(t(lang, "unsupported"), reply_markup=cancel_send_kb(lang))
        return

    result, mid = await relay_message(bot, message, sender_id, target, kind="anon")

    if result == FAIL:
        await state.clear()
        await message.answer(t(lang, "receiver_unavailable"))
        return
    if result != OK:          # albomning davomi — tasdiq takrorlanmaydi
        return

    # Bitta xabardan keyin suhbat yopiladi: keyingi oddiy xabarlar
    # boshqa odamga ketib qolmasin. Yana yozish — tugma orqali.
    await state.clear()
    await message.answer(
        t(lang, "sent_ok"), reply_markup=sent_kb(lang, mid) if mid else None
    )
    await _show_own_link(message, lang)


# ------------------------------- javob berish: tugma orqali yoki surib

async def _send_reply(message: Message, lang: str, bot: Bot, row: Any) -> None:
    """row — javob berilayotgan xabar yozuvi."""
    sender_id = message.from_user.id

    if (message.text or "").strip().lower() in BLOCK_COMMANDS:
        await db.block_user(sender_id, int(row["sender_id"]))
        await message.answer(t(lang, "blocked_ok"))
        return

    target = await db.get_user(int(row["sender_id"]))
    if target is None:
        await message.answer(t(lang, "user_not_found"))
        return
    if await db.is_blocked(int(target["user_id"]), sender_id):
        await message.answer(t(lang, "you_are_blocked"))
        return
    if not _content_ok(message) or too_long(message):
        await message.answer(t(lang, "unsupported"))
        return

    result, mid = await relay_message(
        bot, message, sender_id, target, kind="reply", parent_id=int(row["id"])
    )
    if result == OK:
        await message.answer(
            t(lang, "reply_sent"), reply_markup=sent_kb(lang, mid) if mid else None
        )
    elif result == FAIL:
        await message.answer(t(lang, "receiver_unavailable"))


@router.callback_query(MsgCB.filter(F.action == "reply"))
async def cb_reply(
    call: CallbackQuery, callback_data: MsgCB, state: FSMContext, lang: str
) -> None:
    row = await db.get_message(callback_data.mid)
    if row is None or int(row["receiver_id"]) != call.from_user.id:
        await call.answer(alert(lang, "msg_not_found"), show_alert=True)
        return

    target = await db.get_user(int(row["sender_id"]))
    if target is None:
        await call.answer(alert(lang, "user_not_found"), show_alert=True)
        return
    if await db.is_blocked(int(target["user_id"]), call.from_user.id):
        await call.answer(alert(lang, "you_are_blocked"), show_alert=True)
        return

    await state.set_state(AnonReply.writing)
    await state.update_data(parent_id=int(row["id"]))
    await call.answer()
    if call.message is not None:
        await call.message.answer(
            t(lang, "reply_prompt"), reply_markup=cancel_kb(lang, "reply")
        )


@router.message(AnonReply.writing)
async def on_reply_state(
    message: Message, state: FSMContext, lang: str, bot: Bot
) -> None:
    data = await state.get_data()
    row = await db.get_message(int(data.get("parent_id", 0)))
    if row is None or int(row["receiver_id"]) != message.from_user.id:
        await state.clear()
        await message.answer(t(lang, "msg_not_found"))
        return
    if not message.media_group_id:
        await state.clear()
    await _send_reply(message, lang, bot, row)


@router.message(F.reply_to_message)
async def on_swipe_reply(message: Message, lang: str, user, bot: Bot) -> None:
    row = await db.get_message_by_dest(
        message.from_user.id, message.reply_to_message.message_id
    )
    if row is None:
        link = user_link(user["code"])
        await message.answer(t(lang, "start_main", link=link), reply_markup=share_kb(lang, link))
        return
    await _send_reply(message, lang, bot, row)


# ------------------------------- qabul qiluvchi tugmalari: rasm / o'chirish

@router.callback_query(MsgCB.filter(F.action == "img"))
async def cb_make_image(
    call: CallbackQuery, callback_data: MsgCB, lang: str, bot: Bot
) -> None:
    row = await db.get_message(callback_data.mid)
    if row is None or int(row["receiver_id"]) != call.from_user.id:
        await call.answer(alert(lang, "msg_not_found"), show_alert=True)
        return
    body = (row["body"] or "").strip()
    if not body:
        await call.answer(alert(lang, "img_no_text"), show_alert=True)
        return

    buf = render_card(body, get_bot_username())
    if buf is None:
        await call.answer(alert(lang, "img_failed"), show_alert=True)
        return
    await call.answer()
    await bot.send_photo(
        call.from_user.id, BufferedInputFile(buf.getvalue(), filename="anon.png")
    )


@router.callback_query(MsgCB.filter(F.action == "del"))
async def cb_delete(
    call: CallbackQuery, callback_data: MsgCB, lang: str, bot: Bot
) -> None:
    row = await db.get_message(callback_data.mid)
    if row is None or int(row["receiver_id"]) != call.from_user.id:
        await call.answer(alert(lang, "msg_not_found"), show_alert=True)
        return
    await _delete_pair(bot, call.from_user.id, row)
    await db.delete_message(int(row["id"]))
    await call.answer(alert(lang, "deleted_ok"))


@router.callback_query(MsgCB.filter(F.action == "report"))
async def cb_report(
    call: CallbackQuery, callback_data: MsgCB, lang: str, bot: Bot
) -> None:
    row = await db.get_message(callback_data.mid)
    if row is None or int(row["receiver_id"]) != call.from_user.id:
        await call.answer(alert(lang, "msg_not_found"), show_alert=True)
        return
    if not await db.mark_reported(int(row["id"])):
        await call.answer(alert(lang, "report_already"), show_alert=True)
        return

    body = (row["body"] or "").strip() or f"[{row['content']}]"
    for admin_id in await db.all_admin_ids():
        admin = await db.get_user(admin_id)
        alang = admin["lang"] if admin else None
        try:
            await bot.send_message(
                admin_id,
                t(alang, "admin_report", text=html.quote(body[:600])),
                reply_markup=report_kb(alang, int(row["id"])),
            )
            # Matnsiz xabar bo'lsa — asl nusxasini ham yuboramiz
            if not row["body"] and row["dest_msg_id"]:
                await bot.copy_message(
                    chat_id=admin_id,
                    from_chat_id=int(row["receiver_id"]),
                    message_id=int(row["dest_msg_id"]),
                )
        except Exception:  # noqa: BLE001
            pass

    await call.answer(alert(lang, "report_sent"), show_alert=True)


@router.callback_query(MsgCB.filter(F.action == "block"))
async def cb_block(call: CallbackQuery, callback_data: MsgCB, lang: str) -> None:
    row = await db.get_message(callback_data.mid)
    if row is None or int(row["receiver_id"]) != call.from_user.id:
        await call.answer(alert(lang, "msg_not_found"), show_alert=True)
        return
    await db.block_user(call.from_user.id, int(row["sender_id"]))
    await call.answer(alert(lang, "blocked_ok"), show_alert=True)


# --------------------------- yuboruvchi tugmalari: yana yozish / qaytarib olish

@router.callback_query(MsgCB.filter(F.action == "again"))
async def cb_send_again(
    call: CallbackQuery, callback_data: MsgCB, state: FSMContext, lang: str
) -> None:
    row = await db.get_message(callback_data.mid)
    if row is None or int(row["sender_id"]) != call.from_user.id:
        await call.answer(alert(lang, "msg_not_found"), show_alert=True)
        return

    target = await db.get_user(int(row["receiver_id"]))
    if target is None:
        await call.answer(alert(lang, "user_not_found"), show_alert=True)
        return

    await state.set_state(AnonSend.writing)
    await state.update_data(target_id=int(target["user_id"]))
    await call.answer()
    if call.message is not None:
        await call.message.answer(
            t(lang, "anon_prompt"), reply_markup=cancel_send_kb(lang)
        )


@router.callback_query(MsgCB.filter(F.action == "unsend"))
async def cb_unsend(
    call: CallbackQuery, callback_data: MsgCB, lang: str, bot: Bot
) -> None:
    row = await db.get_message(callback_data.mid)
    if row is None or int(row["sender_id"]) != call.from_user.id:
        await call.answer(alert(lang, "msg_not_found"), show_alert=True)
        return

    deleted = await _delete_pair(bot, int(row["receiver_id"]), row)
    if not deleted:
        await call.answer(alert(lang, "unsend_failed"), show_alert=True)
        return

    await db.delete_message(int(row["id"]))
    await call.answer()
    if call.message is not None:
        try:
            await call.message.edit_text(t(lang, "unsent_ok"))
        except Exception:  # noqa: BLE001
            pass


# ------------------------------------------------------------ bekor qilish

@router.callback_query(CancelCB.filter())
async def cb_cancel(
    call: CallbackQuery, callback_data: CancelCB, state: FSMContext, lang: str
) -> None:
    await state.clear()
    await call.answer()
    if call.message is not None:
        try:
            await call.message.edit_text(t(lang, "cancelled"))
        except Exception:  # noqa: BLE001
            pass


# ------------------- albomning qolgan rasmlari (suhbat yopilgandan keyin ham)

@router.message(F.media_group_id)
async def on_album_rest(message: Message, lang: str, user, bot: Bot) -> None:
    route = album_route(message.from_user.id, message.media_group_id)
    if route is None:
        link = user_link(user["code"])
        await message.answer(
            t(lang, "start_main", link=link), reply_markup=share_kb(lang, link)
        )
        return

    receiver_id, kind, parent_id = route
    target = await db.get_user(int(receiver_id))
    if target is None or not _content_ok(message) or too_long(message):
        return
    if await db.is_blocked(int(target["user_id"]), message.from_user.id):
        return
    await relay_message(
        bot, message, message.from_user.id, target, kind=kind, parent_id=parent_id
    )


# ----------------------------------- boshqa har qanday xabar -> /start ekrani

@router.message()
async def on_any_message(message: Message, lang: str, user) -> None:
    link = user_link(user["code"])
    await message.answer(t(lang, "start_main", link=link), reply_markup=share_kb(lang, link))
