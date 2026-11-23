"""Middleware'lar: foydalanuvchini ro'yxatga olish va flood himoyasi."""
from __future__ import annotations

import time
import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject, User

import config
from app import database as db
from app.keyboards import sub_kb
from app.utils import missing_channels
from app.locales import DEFAULT_LANG, alert, t

log = logging.getLogger(__name__)


class UserMiddleware(BaseMiddleware):
    """Har bir yangilanishda foydalanuvchini bazaga yozadi va tilini beradi."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        tg_user: User | None = data.get("event_from_user")
        if tg_user is not None and not tg_user.is_bot:
            row = await db.ensure_user(
                user_id=tg_user.id,
                username=tg_user.username,
                first_name=tg_user.first_name,
                lang_hint=tg_user.language_code,
            )
            data["user"] = row
            data["lang"] = row["lang"]
        else:
            data["user"] = None
            data["lang"] = DEFAULT_LANG
        return await handler(event, data)


class ThrottleMiddleware(BaseMiddleware):
    """Bir foydalanuvchidan juda tez kelgan xabarlarni to'xtatadi."""

    def __init__(self, rate: float = config.THROTTLE_RATE) -> None:
        self.rate = rate
        self._last: Dict[int, float] = {}
        self._warned: Dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        tg_user: User | None = data.get("event_from_user")
        if tg_user is None or tg_user.id in config.ADMINS:
            return await handler(event, data)

        # Albom (bir nechta rasm birga) elementlari bir zumda keladi —
        # ularni to'xtatib bo'lmaydi, aks holda faqat bittasi yetib boradi.
        if getattr(event, "media_group_id", None):
            self._last[tg_user.id] = time.monotonic()
            return await handler(event, data)

        now = time.monotonic()
        if now - self._last.get(tg_user.id, 0.0) < self.rate:
            if isinstance(event, Message) and now - self._warned.get(tg_user.id, 0.0) > 5:
                self._warned[tg_user.id] = now
                try:
                    await event.answer(t(data.get("lang"), "flood"))
                except Exception:
                    pass
            return None

        self._last[tg_user.id] = now
        if len(self._last) > 20_000:
            cutoff = now - 600
            self._last = {k: v for k, v in self._last.items() if v > cutoff}
            self._warned = {k: v for k, v in self._warned.items() if v > cutoff}
        return await handler(event, data)


class GateMiddleware(BaseMiddleware):
    """Ban va majburiy obunani tekshiradi.

    Adminlar tekshiruvdan o'tkazilmaydi. A'zolik natijasi qisqa vaqt
    eslab qolinadi — har bir xabarda Telegram'ga so'rov ketmasligi uchun.
    """

    MEMBER_TTL = 300.0

    def __init__(self) -> None:
        self._subscribed: Dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        tg_user: User | None = data.get("event_from_user")
        if tg_user is None or tg_user.is_bot:
            return await handler(event, data)

        lang = data.get("lang")
        bot = data.get("bot")

        # Adminlar tekshiruvlardan ozod — o'zlarini qulflab qo'ymasliklari uchun
        if await db.is_admin(tg_user.id):
            return await handler(event, data)

        if await db.is_banned(tg_user.id):
            if isinstance(event, Message):
                await event.answer(t(lang, "you_are_banned"))
            elif isinstance(event, CallbackQuery):
                await event.answer(alert(lang, "you_are_banned"), show_alert=True)
            return None

        # --- «Tekshirish» tugmasining o'zi o'tkazib yuboriladi
        if isinstance(event, CallbackQuery) and (event.data or "").startswith("sub:"):
            return await handler(event, data)

        if bot is None or await db.channels_count() == 0:
            return await handler(event, data)

        now = time.monotonic()
        if now - self._subscribed.get(tg_user.id, 0.0) < self.MEMBER_TTL:
            return await handler(event, data)

        missing = await missing_channels(bot, tg_user.id)
        if not missing:
            self._subscribed[tg_user.id] = now
            if len(self._subscribed) > 20_000:
                cutoff = now - self.MEMBER_TTL
                self._subscribed = {
                    k: v for k, v in self._subscribed.items() if v > cutoff
                }
            return await handler(event, data)

        text = t(lang, "sub_required")
        markup = sub_kb(lang, missing)
        if isinstance(event, Message):
            await event.answer(text, reply_markup=markup)
        elif isinstance(event, CallbackQuery):
            await event.answer()
            if event.message is not None:
                await event.message.answer(text, reply_markup=markup)
        return None
