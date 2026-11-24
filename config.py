"""Bot sozlamalari — barchasi .env faylidan o'qiladi."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "").strip()

_raw_admins = os.getenv("ADMINS", "")
ADMINS: list[int] = [
    int(x) for x in _raw_admins.replace(" ", "").split(",") if x.strip().isdigit()
]

_db = os.getenv("DB_PATH", "data/anonbot.db").strip() or "data/anonbot.db"
DB_PATH: Path = Path(_db) if Path(_db).is_absolute() else BASE_DIR / _db
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Log fayli. Bo'sh qoldirilsa faqat ekranga yoziladi (Docker/systemd uchun qulay)
_log = os.getenv("LOG_FILE", "bot.log").strip()
LOG_FILE: Path | None = (
    (Path(_log) if Path(_log).is_absolute() else BASE_DIR / _log) if _log else None
)

# Flood himoyasi: bir xabar orasidagi minimal vaqt (sekund)
THROTTLE_RATE: float = 0.7

# Bir xabardagi maksimal matn uzunligi (Telegram limiti bilan bir xil)
MAX_TEXT_LEN: int = 4000

# TIL SOZLAMASI
# False  -> hamma uchun bitta til (pastdagi DEFAULT_LANG_CODE). Tavsiya etiladi.
# True   -> har kimning Telegram tiliga qarab avtomatik (uz/ru/en)
# Foydalanuvchi /settings orqali o'zi ham tilni almashtira oladi.
AUTO_DETECT_LANG: bool = False
DEFAULT_LANG_CODE: str = "uz"

# Rasm imkoniyati umuman yoqilganmi (xabar tagidagi «Rasm qilish» tugmasi)
SEND_IMAGE_CARD: bool = True

# Rasmni so'ramasdan avtomatik yuborish. False bo'lsa — faqat tugma bosilganda.
AUTO_IMAGE_CARD: bool = False

# MODERATSIYA: adminlar xabar muallifini ko'ra oladimi.
# Har bir so'rov bot.log ga yoziladi.
#   DEANON_OWNERS_ONLY = True  -> faqat .env dagi asosiy adminlar
DEANON_ENABLED: bool = True
DEANON_OWNERS_ONLY: bool = False

# Anonim yozish taklifida "qoidabuzarlikda admin aniqlay oladi" degan
# ogohlantirish chiqsinmi. Halol bo'lgani uchun yoqilgan.
SHOW_MODERATION_NOTICE: bool = False

# Tugmalarni rangli qilish (Bot API 9.4+):
#   yashil — ijobiy amallar, qizil — o'chirish/bekor qilish, ko'k — qolgani.
# Eski Telegram versiyalarida ranglar e'tiborsiz qoldiriladi, bot buzilmaydi.
BUTTON_COLORS: bool = True

# Kelgan anonim xabar ostidagi tugmalar
SHOW_IMAGE_BUTTON: bool = True     # 🖼 Rasm qilish
SHOW_REPLY_BUTTON: bool = False    # ✍️ Javob berish (tugmasiz ham: xabarni surib javob yoziladi)
SHOW_BLOCK_BUTTON: bool = False    # 🚫 Bloklash (tugmasiz: xabarni surib /block deb yoziladi)
SHOW_DELETE_BUTTON: bool = False   # 🗑 Xabarni o'chirish (qabul qiluvchida)
SHOW_REPORT_BUTTON: bool = True     # ⚠️ Shikoyat (adminlarga)


PLACEHOLDER_TOKEN = "123456789:AAE"


def validate() -> None:
    """Token bor-yo'qligini va shaklini tekshiradi."""
    token = BOT_TOKEN
    problem = ""
    if not token:
        problem = "BOT_TOKEN bo'sh."
    elif token.startswith(PLACEHOLDER_TOKEN):
        problem = "BOT_TOKEN hali namunaviy qiymatda turibdi."
    elif ":" not in token or not token.split(":", 1)[0].isdigit():
        problem = "BOT_TOKEN noto'g'ri shaklda."

    if problem:
        raise SystemExit(
            "\n[XATO] " + problem + "\n\n"
            "  1) Shu papkadagi .env faylini Notepad'da oching\n"
            "  2) BOT_TOKEN= dan keyin @BotFather bergan tokenni qo'ying\n"
            "  3) Ctrl+S bosib saqlang va start.bat ni qaytadan ishga tushiring\n\n"
            "  Namuna:  BOT_TOKEN=8123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw\n"
        )
