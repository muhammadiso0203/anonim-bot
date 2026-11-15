"""Anonim savol-javob boti (@anonAskBot uslubida).

Ishga tushirish:
    1) .env.example -> .env  va BOT_TOKEN ni yozing
    2) pip install -r requirements.txt
    3) python bot.py
"""
from __future__ import annotations

import asyncio
import logging
import sys
from logging.handlers import RotatingFileHandler

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.exceptions import TelegramNetworkError, TelegramUnauthorizedError
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats, ErrorEvent

import config
from app import database as db, emoji_pack
from app.handlers import admin, anon, menu
from app.locales import COMMANDS
from app.middlewares import ThrottleMiddleware, UserMiddleware
from app.utils import set_bot_username

log = logging.getLogger("anonbot")

def setup_logging() -> None:
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    if config.LOG_FILE:
        # Serverda disk to'lib qolmasligi uchun aylanma log: 5 MB x 3 fayl
        handlers.append(
            RotatingFileHandler(
                config.LOG_FILE,
                maxBytes=5 * 1024 * 1024,
                backupCount=3,
                encoding="utf-8",
            )
        )
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
    )
    logging.getLogger("aiogram.event").setLevel(logging.WARNING)


def _commands(lang: str) -> list[BotCommand]:
    items = COMMANDS.get(lang) or COMMANDS["uz"]
    return [BotCommand(command=c, description=d) for c, d in items]


async def set_commands(bot: Bot) -> None:
    """Telegram menyusidagi buyruqlar ro'yxati."""
    scope = BotCommandScopeAllPrivateChats()
    base_lang = "uz" if config.AUTO_DETECT_LANG else config.DEFAULT_LANG_CODE
    await bot.set_my_commands(_commands(base_lang), scope=scope)

    if config.AUTO_DETECT_LANG:
        for lang in COMMANDS:
            if lang != base_lang:
                await bot.set_my_commands(_commands(lang), scope=scope, language_code=lang)
    else:
        # Avval o'rnatilgan boshqa tillardagi menyuni olib tashlaymiz,
        # aks holda ruscha Telegramda ruscha menyu ko'rinaveradi
        for lang in COMMANDS:
            if lang != base_lang:
                try:
                    await bot.delete_my_commands(scope=scope, language_code=lang)
                except Exception:  # noqa: BLE001
                    pass


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())

    # Middleware'lar
    dp.update.outer_middleware(UserMiddleware())
    dp.message.outer_middleware(ThrottleMiddleware())
    dp.callback_query.outer_middleware(ThrottleMiddleware())

    # Router'lar: tartib muhim — admin, keyin menyu (buyruqlar), keyin anonim
    dp.include_router(admin.router)
    dp.include_router(menu.router)
    dp.include_router(anon.router)

    @dp.errors()
    async def on_error(event: ErrorEvent) -> bool:
        from app.utils import custom_emoji_problem

        log.exception("Kutilmagan xatolik: %s", event.exception)
        try:
            await custom_emoji_problem(event.exception)
        except Exception:  # noqa: BLE001
            pass
        return True

    return dp


async def main() -> None:
    setup_logging()
    config.validate()

    await db.init_db(config.DB_PATH)
    await emoji_pack.load()

    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
            link_preview_is_disabled=True,
        ),
    )
    dp = build_dispatcher()

    try:
        try:
            me = await bot.get_me()
        except TelegramUnauthorizedError:
            print(
                "\n[XATO] Telegram tokenni qabul qilmadi (401 Unauthorized).\n"
                "  Token noto'g'ri yoki bot @BotFather da o'chirilgan.\n"
                "  .env faylidagi BOT_TOKEN ni tekshiring yoki /newbot bilan "
                "yangi bot oching.\n"
            )
            return
        except TelegramNetworkError as exc:
            print(
                "\n[XATO] Telegram serveriga ulanib bo'lmadi: " + str(exc) + "\n"
                "  Internet aloqasini tekshiring. Telegram bloklangan bo'lsa "
                "VPN kerak bo'lishi mumkin.\n"
            )
            return
        set_bot_username(me.username or "")
        await set_commands(bot)
        log.info("Bot ishga tushdi: @%s (id=%s)", me.username, me.id)
        if not config.ADMINS:
            log.warning("ADMINS bo'sh — admin panel ishlamaydi (.env ga ID yozing)")

        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await db.close_db()
        await bot.session.close()
        log.info("Bot to'xtadi.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit) as exc:
        if isinstance(exc, SystemExit) and exc.code:
            print(exc.code)
