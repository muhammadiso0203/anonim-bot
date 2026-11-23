"""/start, /mystats, /url, /issue va sozlamalar."""
from __future__ import annotations

from aiogram import Bot, F, Router, html
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    BotCommand,
    BotCommandScopeChat,
    CallbackQuery,
    InlineKeyboardMarkup,
    Message,
)

import config
from app import database as db
from app.handlers.anon import start_anon_session
from app.keyboards import (
    LangCB,
    SubCB,
    NavCB,
    ToggleCB,
    UnblockCB,
    UrlCB,
    back_kb,
    blocked_kb,
    cancel_kb,
    lang_kb,
    settings_kb,
    share_kb,
    url_confirm_kb,
)
from app.locales import COMMANDS, LANG_NAMES, alert, t
from app.states import Issue
from app.utils import missing_channels, user_link

router = Router(name="menu")


# ------------------------------------------------------------- yordamchilar

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


async def _start_view(user, lang: str) -> tuple[str, InlineKeyboardMarkup]:
    link = user_link(user["code"])
    return t(lang, "start_main", link=link), share_kb(lang, link)


async def _stats_view(user, lang: str) -> tuple[str, InlineKeyboardMarkup]:
    link = user_link(user["code"])
    stats = await db.profile_stats(int(user["user_id"]))
    return t(lang, "mystats", link=link, **stats), share_kb(lang, link)


async def _settings_view(user, lang: str) -> tuple[str, InlineKeyboardMarkup]:
    rows = await db.blocked_list(int(user["user_id"]))
    text = t(
        lang,
        "settings_title",
        lang=LANG_NAMES.get(user["lang"], user["lang"]),
        accepting=t(lang, "on" if user["accepting"] else "off"),
        blocked=len(rows),
    )
    return text, settings_kb(lang, bool(user["accepting"]))


async def _blocked_view(user, lang: str) -> tuple[str, InlineKeyboardMarkup]:
    rows = await db.blocked_list(int(user["user_id"]))
    if not rows:
        return t(lang, "blocked_empty"), blocked_kb(lang, [])
    return t(lang, "blocked_list_title", count=len(rows)), blocked_kb(lang, rows)


# ------------------------------------------------------------------ /start

@router.message(CommandStart())
async def cmd_start(
    message: Message, command: CommandObject, state: FSMContext, lang: str, user
) -> None:
    await state.clear()
    payload = (command.args or "").strip()

    if payload:
        target = await db.resolve_target(payload)
        if target is None:
            await message.answer(t(lang, "user_not_found"))
        elif not target["accepting"] and int(target["user_id"]) != message.from_user.id:
            await message.answer(t(lang, "not_accepting"))
        elif await db.is_blocked(int(target["user_id"]), message.from_user.id):
            await message.answer(t(lang, "you_are_blocked"))
        else:
            await db.add_link_view(int(target["user_id"]), message.from_user.id)
            await start_anon_session(message, state, lang, target)
            return

    text, markup = await _start_view(user, lang)
    await message.answer(text, reply_markup=markup)


# --------------------------------------------------------------- /mystats

@router.message(Command("mystats", "stats"))
async def cmd_mystats(message: Message, state: FSMContext, lang: str, user) -> None:
    await state.clear()
    text, markup = await _stats_view(user, lang)
    await message.answer(text, reply_markup=markup)


# ------------------------------------------------------------------- /url

@router.message(Command("url", "link"))
async def cmd_url(message: Message, state: FSMContext, lang: str, user) -> None:
    await state.clear()
    await message.answer(
        t(lang, "url_ask", link=user_link(user["code"])),
        reply_markup=url_confirm_kb(lang),
    )


@router.callback_query(UrlCB.filter())
async def cb_url(call: CallbackQuery, callback_data: UrlCB, lang: str, user) -> None:
    if not callback_data.ok:
        text, markup = await _start_view(user, lang)
        await _safe_edit(call, text, markup)
        await call.answer(alert(lang, "cancelled"))
        return

    code = await db.regenerate_code(call.from_user.id)
    link = user_link(code)
    await _safe_edit(call, t(lang, "url_changed", link=link), share_kb(lang, link))
    await call.answer()


# ----------------------------------------------------------------- /issue

@router.message(Command("issue"))
async def cmd_issue(message: Message, state: FSMContext, lang: str) -> None:
    if not config.ADMINS:
        await message.answer(t(lang, "issue_nowhere"))
        return
    await state.set_state(Issue.writing)
    await message.answer(t(lang, "issue_prompt"), reply_markup=cancel_kb(lang, "issue"))


@router.message(Issue.writing)
async def on_issue(message: Message, state: FSMContext, lang: str, bot: Bot) -> None:
    await state.clear()
    body = message.text or message.caption or "—"
    for admin_id in config.ADMINS:
        try:
            await bot.send_message(
                admin_id,
                t(lang, "admin_issue", uid=message.from_user.id, text=html.quote(body)),
            )
        except Exception:  # noqa: BLE001
            pass
    await message.answer(t(lang, "issue_sent"))


# -------------------------------------------------------- qolgan buyruqlar

@router.message(Command("settings"))
async def cmd_settings(message: Message, state: FSMContext, lang: str, user) -> None:
    await state.clear()
    text, markup = await _settings_view(user, lang)
    await message.answer(text, reply_markup=markup)


@router.message(Command("blocked", "block"))
async def cmd_blocked(message: Message, state: FSMContext, lang: str, user) -> None:
    await state.clear()
    text, markup = await _blocked_view(user, lang)
    await message.answer(text, reply_markup=markup)


@router.message(Command("help"))
async def cmd_help(message: Message, state: FSMContext, lang: str) -> None:
    await state.clear()
    await message.answer(t(lang, "help"), reply_markup=back_kb(lang))


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext, lang: str) -> None:
    if await state.get_state() is None:
        await message.answer(t(lang, "nothing_to_cancel"))
        return
    await state.clear()
    await message.answer(t(lang, "cancelled"))


# ------------------------------------------------- majburiy obunani tekshirish

@router.callback_query(SubCB.filter())
async def cb_sub_check(call: CallbackQuery, lang: str, user, bot: Bot) -> None:
    if await missing_channels(bot, call.from_user.id):
        await call.answer(alert(lang, "sub_fail"), show_alert=True)
        return

    await call.answer(alert(lang, "sub_ok"))
    if call.message is not None:
        try:
            await call.message.delete()
        except Exception:  # noqa: BLE001
            pass
    text, markup = await _start_view(user, lang)
    await bot.send_message(call.from_user.id, text, reply_markup=markup)


# ------------------------------------------------------------ navigatsiya

@router.callback_query(NavCB.filter())
async def cb_nav(
    call: CallbackQuery, callback_data: NavCB, state: FSMContext, lang: str, user
) -> None:
    await state.clear()
    to = callback_data.to

    if to == "settings":
        text, markup = await _settings_view(user, lang)
    elif to == "lang":
        text, markup = t(lang, "lang_choose"), lang_kb(lang)
    elif to == "blocked":
        text, markup = await _blocked_view(user, lang)
    elif to == "stats":
        text, markup = await _stats_view(user, lang)
    elif to == "help":
        text, markup = t(lang, "help"), back_kb(lang)
    elif to == "link":
        text, markup = await _start_view(user, lang)
    else:
        await call.answer()
        return

    await _safe_edit(call, text, markup)
    await call.answer()


@router.callback_query(LangCB.filter())
async def cb_lang(call: CallbackQuery, callback_data: LangCB, lang: str, bot: Bot) -> None:
    if callback_data.code not in LANG_NAMES:
        await call.answer()
        return
    await db.set_lang(call.from_user.id, callback_data.code)
    try:
        await bot.set_my_commands(
            [
                BotCommand(command=c, description=d)
                for c, d in COMMANDS.get(callback_data.code, [])
            ],
            scope=BotCommandScopeChat(chat_id=call.from_user.id),
        )
    except Exception:  # noqa: BLE001
        pass
    user = await db.get_user(call.from_user.id)
    new_lang = callback_data.code
    text, markup = await _settings_view(user, new_lang)
    await _safe_edit(call, text, markup)
    await call.answer(alert(new_lang, "lang_set"))


@router.callback_query(ToggleCB.filter(F.field == "accepting"))
async def cb_toggle_accepting(call: CallbackQuery, lang: str, user) -> None:
    new_value = not bool(user["accepting"])
    await db.set_accepting(call.from_user.id, new_value)
    user = await db.get_user(call.from_user.id)
    text, markup = await _settings_view(user, lang)
    await _safe_edit(call, text, markup)
    await call.answer(alert(lang, "accepting_on" if new_value else "accepting_off"))


@router.callback_query(UnblockCB.filter())
async def cb_unblock(call: CallbackQuery, callback_data: UnblockCB, lang: str, user) -> None:
    await db.unblock_user(call.from_user.id, callback_data.uid)
    text, markup = await _blocked_view(user, lang)
    await _safe_edit(call, text, markup)
    await call.answer(alert(lang, "unblocked_ok"))
