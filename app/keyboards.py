"""Inline tugmalar va callback ma'lumot fabrikalari.

Premium emoji tugmada `icon_custom_emoji_id` orqali ko'rsatiladi (Bot API 9.4+):
Telegram uni tugma yozuvidan oldin chizadi. Shuning uchun yozuvlar bu yerga
«xom» holda (asl emoji bilan) keladi va _b() ularni ajratadi.
"""
from __future__ import annotations

from urllib.parse import quote

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import config
from app import emoji_pack
from app.locales import LANG_NAMES, label

#: Eski aiogram versiyalarida bu maydonlar bo'lmasligi mumkin
_FIELDS = getattr(InlineKeyboardButton, "model_fields", {})
SUPPORTS_ICON = "icon_custom_emoji_id" in _FIELDS
SUPPORTS_STYLE = "style" in _FIELDS

#: Tugma ranglari (Bot API 9.4+)
GREEN = "success"   # ijobiy amal
RED = "danger"      # o'chirish / bekor qilish
BLUE = "primary"    # navigatsiya va qolgani


class MsgCB(CallbackData, prefix="msg"):
    action: str          # reply | block | img | del | again | unsend
    mid: int


class NavCB(CallbackData, prefix="nav"):
    to: str              # settings | lang | blocked | help | stats | link


class LangCB(CallbackData, prefix="lng"):
    code: str


class ToggleCB(CallbackData, prefix="tgl"):
    field: str           # accepting


class UnblockCB(CallbackData, prefix="unb"):
    uid: int


class CancelCB(CallbackData, prefix="cnl"):
    scope: str           # send | issue | reply


class UrlCB(CallbackData, prefix="url"):
    ok: int              # 1 = yangilansin, 0 = yo'q


class AdminCB(CallbackData, prefix="adm"):
    action: str          # home | stats | broadcast | admins | add | rm | owner | close
    arg: int = 0


class EmojiCB(CallbackData, prefix="emj"):
    action: str          # pick | reset | resetall | back
    idx: int = 0


def _style(style: str | None) -> dict:
    """Rang qo'llab-quvvatlansa — {'style': ...}, aks holda bo'sh."""
    if style and SUPPORTS_STYLE and config.BUTTON_COLORS:
        return {"style": style}
    return {}


def _b(raw: str, *, style: str | None = BLUE, **kwargs) -> InlineKeyboardButton:
    """Tugma yasaydi: premium emojini «icon» qilib ajratadi va rang beradi."""
    text, icon = emoji_pack.button_parts(raw)
    extra: dict = {}
    if icon and text and SUPPORTS_ICON:
        extra["icon_custom_emoji_id"] = icon
    else:
        text = emoji_pack.for_button(raw)
    if style and SUPPORTS_STYLE and config.BUTTON_COLORS:
        extra["style"] = style
    return InlineKeyboardButton(text=text, **extra, **kwargs)


def share_url(link: str, text: str) -> str:
    return f"https://t.me/share/url?url={quote(link, safe='')}&text={quote(text, safe='')}"


# ------------------------------------------------------- foydalanuvchi uchun

def share_kb(lang: str, link: str, extra: bool = True) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        _b(label(lang, "btn_share"), style=GREEN, url=share_url(link, label(lang, "share_text")))
    )
    if extra:
        kb.row(
            _b(label(lang, "btn_settings"), callback_data=NavCB(to="settings").pack())
        )
    return kb.as_markup()


def incoming_kb(lang: str, mid: int, can_block: bool = True) -> InlineKeyboardMarkup:
    """Kelgan anonim xabar ostidagi tugmalar (config.py dan boshqariladi)."""
    kb = InlineKeyboardBuilder()
    top = []
    if config.SHOW_REPLY_BUTTON:
        top.append(
            _b(label(lang, "btn_reply"), style=GREEN, callback_data=MsgCB(action="reply", mid=mid).pack())
        )
    if can_block and config.SHOW_BLOCK_BUTTON:
        top.append(
            _b(label(lang, "btn_block"), style=RED, callback_data=MsgCB(action="block", mid=mid).pack())
        )
    if top:
        kb.row(*top)

    bottom = []
    if config.SHOW_IMAGE_BUTTON:
        bottom.append(
            _b(label(lang, "btn_make_image"), callback_data=MsgCB(action="img", mid=mid).pack())
        )
    if config.SHOW_DELETE_BUTTON:
        bottom.append(
            _b(label(lang, "btn_delete"), style=RED, callback_data=MsgCB(action="del", mid=mid).pack())
        )
    if bottom:
        kb.row(*bottom)
    return kb.as_markup()


def sent_kb(lang: str, mid: int) -> InlineKeyboardMarkup:
    """«Xabar yuborildi» ostidagi tugmalar — yuboruvchi uchun."""
    kb = InlineKeyboardBuilder()
    kb.row(_b(label(lang, "btn_send_more"), style=GREEN, callback_data=MsgCB(action="again", mid=mid).pack()))
    kb.row(_b(label(lang, "btn_unsend"), style=RED, callback_data=MsgCB(action="unsend", mid=mid).pack()))
    return kb.as_markup()


def cancel_send_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(_b(label(lang, "btn_cancel_send"), style=RED, callback_data=CancelCB(scope="send").pack()))
    return kb.as_markup()


def cancel_kb(lang: str, scope: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(_b(label(lang, "btn_cancel"), style=RED, callback_data=CancelCB(scope=scope).pack()))
    return kb.as_markup()


def url_confirm_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        _b(label(lang, "btn_yes"), style=GREEN, callback_data=UrlCB(ok=1).pack()),
        _b(label(lang, "btn_no"), style=RED, callback_data=UrlCB(ok=0).pack()),
    )
    return kb.as_markup()


def back_kb(lang: str, to: str = "settings") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(_b(label(lang, "btn_back"), callback_data=NavCB(to=to).pack()))
    return kb.as_markup()


def settings_kb(lang: str, accepting: bool) -> InlineKeyboardMarkup:
    state = emoji_pack.for_button(label(lang, "on" if accepting else "off"))
    kb = InlineKeyboardBuilder()
    kb.row(
        _b(
            label(lang, "btn_accepting", state=state),
            style=GREEN if accepting else RED,
            callback_data=ToggleCB(field="accepting").pack(),
        )
    )
    kb.row(
        _b(label(lang, "btn_lang"), callback_data=NavCB(to="lang").pack()),
        _b(label(lang, "btn_blocked"), callback_data=NavCB(to="blocked").pack()),
    )
    kb.row(
        _b(label(lang, "btn_stats"), callback_data=NavCB(to="stats").pack()),
        _b(label(lang, "btn_help"), callback_data=NavCB(to="help").pack()),
    )
    return kb.as_markup()


def lang_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for code, name in LANG_NAMES.items():
        mark = " ✅" if code == lang else ""
        kb.row(
            InlineKeyboardButton(
                text=name + mark,
                callback_data=LangCB(code=code).pack(),
                **_style(GREEN if code == lang else BLUE),
            )
        )
    kb.row(_b(label(lang, "btn_back"), callback_data=NavCB(to="settings").pack()))
    return kb.as_markup()


def blocked_kb(lang: str, rows: list) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for num, row in enumerate(rows, start=1):
        kb.row(
            _b(
                "✅ " + label(lang, "blocked_item", num=num, count=row["msg_count"]),
                style=GREEN,
                callback_data=UnblockCB(uid=row["blocked_id"]).pack(),
            )
        )
    kb.row(_b(label(lang, "btn_back"), callback_data=NavCB(to="settings").pack()))
    return kb.as_markup()


# ------------------------------------------------------------ admin panel

def admin_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        _b(label(lang, "btn_adm_stats"), callback_data=AdminCB(action="stats").pack()),
        _b(label(lang, "btn_adm_users"), callback_data=AdminCB(action="users").pack()),
    )
    kb.row(
        _b(label(lang, "btn_adm_broadcast"), callback_data=AdminCB(action="broadcast").pack()),
        _b(label(lang, "btn_adm_admins"), callback_data=AdminCB(action="admins").pack()),
    )
    kb.row(
        _b(label(lang, "btn_adm_emoji"), callback_data=EmojiCB(action="back").pack()),
    )
    kb.row(
        _b(label(lang, "btn_refresh"), callback_data=AdminCB(action="home").pack()),
        _b(label(lang, "btn_close"), style=RED, callback_data=AdminCB(action="close").pack()),
    )
    return kb.as_markup()


def admin_back_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(_b(label(lang, "btn_back"), callback_data=AdminCB(action="home").pack()))
    return kb.as_markup()


def admins_kb(lang: str, rows: list, owners: list[int]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for row in rows:
        uid = int(row["user_id"])
        name = row["first_name"] or row["username"] or str(uid)
        kb.row(_b(f"❌ {name} ({uid})", style=RED, callback_data=AdminCB(action="rm", arg=uid).pack()))
    for uid in owners:
        kb.row(_b(f"🔒 {uid}", callback_data=AdminCB(action="owner", arg=uid).pack()))
    kb.row(_b(label(lang, "btn_adm_add"), style=GREEN, callback_data=AdminCB(action="add").pack()))
    kb.row(_b(label(lang, "btn_back"), callback_data=AdminCB(action="home").pack()))
    return kb.as_markup()


def users_kb(lang: str, page: int, pages: int) -> InlineKeyboardMarkup:
    """Foydalanuvchilar ro'yxati: sahifalash + CSV."""
    kb = InlineKeyboardBuilder()
    if pages > 1:
        kb.row(
            InlineKeyboardButton(
                text="◀️",
                callback_data=AdminCB(action="users", arg=(page - 1) % pages).pack(),
                **_style(BLUE),
            ),
            InlineKeyboardButton(
                text=f"{page + 1}/{pages}",
                callback_data=AdminCB(action="users", arg=page).pack(),
                **_style(BLUE),
            ),
            InlineKeyboardButton(
                text="▶️",
                callback_data=AdminCB(action="users", arg=(page + 1) % pages).pack(),
                **_style(BLUE),
            ),
        )
    kb.row(
        _b(
            label(lang, "btn_users_csv"),
            style=GREEN,
            callback_data=AdminCB(action="users_csv").pack(),
        )
    )
    kb.row(_b(label(lang, "btn_back"), callback_data=AdminCB(action="home").pack()))
    return kb.as_markup()


def emoji_list_kb(lang: str, items: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    """items: (indeks, asl emoji). 5 tadan qatorga.

    Premium qilib qo'yilganlari tugmada haqiqiy premium emoji bilan chiqadi.
    """
    kb = InlineKeyboardBuilder()
    row: list[InlineKeyboardButton] = []
    for idx, emoji in items:
        data = EmojiCB(action="pick", idx=idx).pack()
        current = emoji_pack.current(emoji)
        if current and current[0] == "custom" and SUPPORTS_ICON:
            button = InlineKeyboardButton(
                text="⭑",
                icon_custom_emoji_id=current[1],
                callback_data=data,
                **_style(GREEN),
            )
        else:
            button = InlineKeyboardButton(
                text=emoji_pack.describe(emoji), callback_data=data, **_style(BLUE)
            )
        row.append(button)
        if len(row) == 5:
            kb.row(*row)
            row = []
    if row:
        kb.row(*row)
    kb.row(_b(label(lang, "btn_emoji_resetall"), style=RED, callback_data=EmojiCB(action="resetall").pack()))
    kb.row(_b(label(lang, "btn_back"), callback_data=AdminCB(action="home").pack()))
    return kb.as_markup()


def emoji_item_kb(lang: str, idx: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(_b(label(lang, "btn_emoji_reset"), style=RED, callback_data=EmojiCB(action="reset", idx=idx).pack()))
    kb.row(_b(label(lang, "btn_back"), callback_data=EmojiCB(action="back").pack()))
    return kb.as_markup()
