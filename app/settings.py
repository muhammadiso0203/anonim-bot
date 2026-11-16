"""Ishlash paytidagi sozlamalar: bazadagi qiymat config.py dagidan ustun.

Admin panelidan o'zgartiriladi, serverga kirish shart emas.
"""
from __future__ import annotations

import logging

import config

log = logging.getLogger(__name__)

PREFIX = "set:"

#: Paneldan boshqariladigan yoqish/o'chirish sozlamalari:
#: (config nomi, matn kaliti)
TOGGLES: tuple[tuple[str, str], ...] = (
    ("SHOW_REPLY_BUTTON", "set_reply_btn"),
    ("SHOW_BLOCK_BUTTON", "set_block_btn"),
    ("SHOW_REPORT_BUTTON", "set_report_btn"),
    ("SHOW_IMAGE_BUTTON", "set_image_btn"),
    ("SHOW_DELETE_BUTTON", "set_delete_btn"),
    ("AUTO_IMAGE_CARD", "set_auto_image"),
    ("BUTTON_COLORS", "set_colors"),
)
TOGGLE_NAMES = tuple(name for name, _ in TOGGLES)

_cache: dict[str, bool] = {}


def default(name: str) -> bool:
    return bool(getattr(config, name, False))


def get(name: str) -> bool:
    """Bazadagi qiymat bo'lsa o'sha, bo'lmasa config.py dagi."""
    if name in _cache:
        return _cache[name]
    return default(name)


def set_cache(raw_settings: dict[str, str]) -> None:
    _cache.clear()
    for key, value in raw_settings.items():
        name = key[len(PREFIX):]
        if name in TOGGLE_NAMES:
            _cache[name] = value == "1"


async def load() -> None:
    from app import database as db

    try:
        set_cache(await db.settings_with_prefix(PREFIX))
    except Exception as exc:  # noqa: BLE001
        log.warning("Sozlamalar o'qilmadi: %s", exc)


async def toggle(name: str) -> bool:
    """Sozlamani teskarisiga o'zgartiradi va yangi qiymatni qaytaradi."""
    from app import database as db

    if name not in TOGGLE_NAMES:
        return False
    new_value = not get(name)
    await db.set_setting(PREFIX + name, "1" if new_value else "0")
    _cache[name] = new_value
    return new_value


async def reset_all() -> None:
    from app import database as db

    for name in TOGGLE_NAMES:
        await db.set_setting(PREFIX + name, None)
    _cache.clear()
