"""SQLite bazasi: foydalanuvchilar, xabarlar, bloklar."""
from __future__ import annotations

import secrets
import string
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import aiosqlite

import config

_CODE_ALPHABET = string.ascii_lowercase + string.digits
_db: Optional[aiosqlite.Connection] = None

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id        INTEGER PRIMARY KEY,
    code           TEXT    NOT NULL UNIQUE,
    username       TEXT,
    first_name     TEXT,
    lang           TEXT    NOT NULL DEFAULT 'uz',
    lang_chosen    INTEGER NOT NULL DEFAULT 0,
    accepting      INTEGER NOT NULL DEFAULT 1,
    stopped_bot    INTEGER NOT NULL DEFAULT 0,
    created_at     TEXT    NOT NULL,
    last_active    TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS messages (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id   INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    parent_id   INTEGER,
    kind        TEXT    NOT NULL DEFAULT 'anon',
    content     TEXT    NOT NULL DEFAULT 'text',
    body         TEXT,
    dest_msg_id  INTEGER,
    dest_msg_id2 INTEGER,
    created_at  TEXT    NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_msg_receiver ON messages(receiver_id);
CREATE INDEX IF NOT EXISTS idx_msg_sender   ON messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_msg_dest     ON messages(receiver_id, dest_msg_id);

CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS admins (
    user_id    INTEGER PRIMARY KEY,
    added_by   INTEGER,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS link_views (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id   INTEGER NOT NULL,
    visitor_id INTEGER NOT NULL,
    created_at TEXT    NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_views_owner ON link_views(owner_id);

CREATE TABLE IF NOT EXISTS blocks (
    owner_id   INTEGER NOT NULL,
    blocked_id INTEGER NOT NULL,
    created_at TEXT    NOT NULL,
    PRIMARY KEY (owner_id, blocked_id)
);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def db() -> aiosqlite.Connection:
    if _db is None:
        raise RuntimeError("Baza ishga tushirilmagan. init_db() ni chaqiring.")
    return _db


async def init_db(path: Path) -> None:
    global _db
    _db = await aiosqlite.connect(path)
    _db.row_factory = aiosqlite.Row
    await _db.execute("PRAGMA journal_mode=WAL")
    await _db.execute("PRAGMA foreign_keys=ON")
    await _db.executescript(SCHEMA)
    await _db.commit()
    await _migrate()


async def _migrate() -> None:
    """Eski bazaga yangi ustunlarni qo'shadi (ma'lumot yo'qolmaydi)."""
    cur = await db().execute("PRAGMA table_info(messages)")
    cols = {row["name"] for row in await cur.fetchall()}
    if "dest_msg_id2" not in cols:
        await db().execute("ALTER TABLE messages ADD COLUMN dest_msg_id2 INTEGER")
    if "body" not in cols:
        await db().execute("ALTER TABLE messages ADD COLUMN body TEXT")

    cur = await db().execute("PRAGMA table_info(users)")
    cols = {row["name"] for row in await cur.fetchall()}
    if "lang_chosen" not in cols:
        await db().execute(
            "ALTER TABLE users ADD COLUMN lang_chosen INTEGER NOT NULL DEFAULT 0"
        )
    await db().commit()


async def close_db() -> None:
    global _db
    if _db is not None:
        await _db.close()
        _db = None


# ---------------------------------------------------------------- users

async def _unique_code() -> str:
    while True:
        code = "".join(secrets.choice(_CODE_ALPHABET) for _ in range(8))
        cur = await db().execute("SELECT 1 FROM users WHERE code = ?", (code,))
        if await cur.fetchone() is None:
            return code


async def get_user(user_id: int) -> Optional[aiosqlite.Row]:
    cur = await db().execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    return await cur.fetchone()


async def get_user_by_code(code: str) -> Optional[aiosqlite.Row]:
    cur = await db().execute("SELECT * FROM users WHERE code = ?", (code.lower(),))
    return await cur.fetchone()


async def resolve_target(payload: str) -> Optional[aiosqlite.Row]:
    """Deep-link payload: kod yoki user_id bo'lishi mumkin."""
    payload = (payload or "").strip()
    if not payload:
        return None
    user = await get_user_by_code(payload)
    if user is not None:
        return user
    if payload.isdigit():
        return await get_user(int(payload))
    return None


async def ensure_user(
    user_id: int,
    username: Optional[str] = None,
    first_name: Optional[str] = None,
    lang_hint: Optional[str] = None,
) -> aiosqlite.Row:
    """Foydalanuvchini yaratadi yoki ma'lumotlarini yangilaydi."""
    from app.locales import normalize_lang

    row = await get_user(user_id)
    now = _now()

    if config.AUTO_DETECT_LANG:
        start_lang = normalize_lang(lang_hint)
    else:
        start_lang = normalize_lang(config.DEFAULT_LANG_CODE)

    if row is None:
        await db().execute(
            "INSERT INTO users (user_id, code, username, first_name, lang,"
            " created_at, last_active) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, await _unique_code(), username, first_name, start_lang, now, now),
        )
    else:
        await db().execute(
            "UPDATE users SET username = ?, first_name = ?, last_active = ?,"
            " stopped_bot = 0 WHERE user_id = ?",
            (username, first_name, now, user_id),
        )
        # Foydalanuvchi tilni o'zi tanlamagan bo'lsa — sozlamadagi tilga keltiramiz
        if not row["lang_chosen"] and row["lang"] != start_lang:
            await db().execute(
                "UPDATE users SET lang = ? WHERE user_id = ?", (start_lang, user_id)
            )
    await db().commit()
    row = await get_user(user_id)
    assert row is not None
    return row


async def regenerate_code(user_id: int) -> str:
    """/url — shaxsiy havolani yangilaydi, eskisi ishlamay qoladi."""
    code = await _unique_code()
    await db().execute("UPDATE users SET code = ? WHERE user_id = ?", (code, user_id))
    await db().commit()
    return code


async def add_link_view(owner_id: int, visitor_id: int) -> None:
    """Havola orqali o'tish (o'zi bosgani hisoblanmaydi)."""
    if owner_id == visitor_id:
        return
    await db().execute(
        "INSERT INTO link_views (owner_id, visitor_id, created_at) VALUES (?, ?, ?)",
        (owner_id, visitor_id, _now()),
    )
    await db().commit()


async def set_lang(user_id: int, lang: str) -> None:
    """Foydalanuvchi tilni o'zi tanladi — endi avtomatik o'zgarmaydi."""
    await db().execute(
        "UPDATE users SET lang = ?, lang_chosen = 1 WHERE user_id = ?", (lang, user_id)
    )
    await db().commit()


async def set_accepting(user_id: int, value: bool) -> None:
    await db().execute(
        "UPDATE users SET accepting = ? WHERE user_id = ?", (int(value), user_id)
    )
    await db().commit()


async def mark_stopped(user_id: int, value: bool = True) -> None:
    await db().execute(
        "UPDATE users SET stopped_bot = ? WHERE user_id = ?", (int(value), user_id)
    )
    await db().commit()


async def all_user_ids() -> list[int]:
    cur = await db().execute("SELECT user_id FROM users WHERE stopped_bot = 0")
    return [r["user_id"] for r in await cur.fetchall()]


# ------------------------------------------------------------- messages

async def add_message(
    sender_id: int,
    receiver_id: int,
    parent_id: Optional[int] = None,
    kind: str = "anon",
    content: str = "text",
    body: Optional[str] = None,
    dest_msg_id: Optional[int] = None,
) -> int:
    cur = await db().execute(
        "INSERT INTO messages (sender_id, receiver_id, parent_id, kind, content,"
        " body, dest_msg_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (sender_id, receiver_id, parent_id, kind, content,
         (body or "")[:1000] or None, dest_msg_id, _now()),
    )
    await db().commit()
    return int(cur.lastrowid)


async def set_dest_msg_id(
    message_row_id: int, dest_msg_id: int, dest_msg_id2: Optional[int] = None
) -> None:
    await db().execute(
        "UPDATE messages SET dest_msg_id = ?, dest_msg_id2 = ? WHERE id = ?",
        (dest_msg_id, dest_msg_id2, message_row_id),
    )
    await db().commit()


async def get_message_by_dest(receiver_id: int, dest_msg_id: int):
    """Foydalanuvchi «surib» javob berganda — qaysi xabarga javob berilyapti."""
    cur = await db().execute(
        "SELECT * FROM messages WHERE receiver_id = ?"
        " AND (dest_msg_id = ? OR dest_msg_id2 = ?) ORDER BY id DESC LIMIT 1",
        (receiver_id, dest_msg_id, dest_msg_id),
    )
    return await cur.fetchone()


async def get_message(message_row_id: int) -> Optional[aiosqlite.Row]:
    cur = await db().execute("SELECT * FROM messages WHERE id = ?", (message_row_id,))
    return await cur.fetchone()


# --------------------------------------------------------------- blocks

async def block_user(owner_id: int, blocked_id: int) -> None:
    await db().execute(
        "INSERT OR IGNORE INTO blocks (owner_id, blocked_id, created_at)"
        " VALUES (?, ?, ?)",
        (owner_id, blocked_id, _now()),
    )
    await db().commit()


async def unblock_user(owner_id: int, blocked_id: int) -> None:
    await db().execute(
        "DELETE FROM blocks WHERE owner_id = ? AND blocked_id = ?",
        (owner_id, blocked_id),
    )
    await db().commit()


async def is_blocked(owner_id: int, blocked_id: int) -> bool:
    cur = await db().execute(
        "SELECT 1 FROM blocks WHERE owner_id = ? AND blocked_id = ?",
        (owner_id, blocked_id),
    )
    return await cur.fetchone() is not None


async def blocked_list(owner_id: int) -> list[aiosqlite.Row]:
    cur = await db().execute(
        "SELECT b.blocked_id, b.created_at,"
        " (SELECT COUNT(*) FROM messages m WHERE m.sender_id = b.blocked_id"
        "   AND m.receiver_id = b.owner_id) AS msg_count"
        " FROM blocks b WHERE b.owner_id = ? ORDER BY b.created_at DESC",
        (owner_id,),
    )
    return list(await cur.fetchall())


# ------------------------------------------------- foydalanuvchilar ro'yxati

_USER_LIST_SQL = (
    "SELECT u.user_id, u.username, u.first_name, u.lang, u.accepting,"
    " u.stopped_bot, u.created_at, u.code,"
    " (SELECT COUNT(*) FROM messages m WHERE m.receiver_id = u.user_id) AS got,"
    " (SELECT COUNT(*) FROM messages m WHERE m.sender_id = u.user_id) AS sent"
    " FROM users u ORDER BY u.created_at DESC, u.user_id DESC"
)


async def users_count() -> int:
    return await _scalar("SELECT COUNT(*) FROM users")


async def users_page(limit: int, offset: int) -> list:
    """Yangi qo'shilganlar birinchi bo'lib."""
    cur = await db().execute(_USER_LIST_SQL + " LIMIT ? OFFSET ?", (limit, offset))
    return list(await cur.fetchall())


async def users_all() -> list:
    """CSV ga chiqarish uchun hammasi."""
    cur = await db().execute(_USER_LIST_SQL)
    return list(await cur.fetchall())


# ------------------------------------------------------------- settings

async def get_setting(key: str) -> Optional[str]:
    cur = await db().execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = await cur.fetchone()
    return row["value"] if row else None


async def set_setting(key: str, value: Optional[str]) -> None:
    if value is None:
        await db().execute("DELETE FROM settings WHERE key = ?", (key,))
    else:
        await db().execute(
            "INSERT INTO settings (key, value) VALUES (?, ?)"
            " ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )
    await db().commit()


async def settings_with_prefix(prefix: str) -> dict[str, str]:
    cur = await db().execute(
        "SELECT key, value FROM settings WHERE key LIKE ?", (prefix + "%",)
    )
    return {row["key"]: row["value"] for row in await cur.fetchall()}


# --------------------------------------------------------------- admins

async def add_admin(user_id: int, added_by: Optional[int] = None) -> None:
    await db().execute(
        "INSERT OR IGNORE INTO admins (user_id, added_by, created_at)"
        " VALUES (?, ?, ?)",
        (user_id, added_by, _now()),
    )
    await db().commit()


async def remove_admin(user_id: int) -> None:
    await db().execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
    await db().commit()


async def is_db_admin(user_id: int) -> bool:
    cur = await db().execute("SELECT 1 FROM admins WHERE user_id = ?", (user_id,))
    return await cur.fetchone() is not None


async def admin_rows() -> list:
    cur = await db().execute(
        "SELECT a.user_id, a.created_at, u.username, u.first_name"
        " FROM admins a LEFT JOIN users u ON u.user_id = a.user_id"
        " ORDER BY a.created_at",
    )
    return list(await cur.fetchall())


async def is_admin(user_id: int) -> bool:
    """Doimiy (.env) yoki qo'shilgan admin."""
    return user_id in config.ADMINS or await is_db_admin(user_id)


async def all_admin_ids() -> list[int]:
    ids = list(config.ADMINS)
    for row in await admin_rows():
        if row["user_id"] not in ids:
            ids.append(int(row["user_id"]))
    return ids


# ----------------------------------------------------------- statistics

async def _scalar(query: str, args: tuple[Any, ...] = ()) -> int:
    cur = await db().execute(query, args)
    row = await cur.fetchone()
    return int(row[0]) if row and row[0] is not None else 0


def _popularity(messages: int, views: int) -> int:
    """0..10 oraligʻidagi «mashhurlik» darajasi."""
    return max(0, min(10, (messages * 2 + views) // 10))


async def profile_stats(user_id: int) -> dict[str, int]:
    """/mystats uchun: bugungi va umumiy koʻrsatkichlar."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    msg_today = await _scalar(
        "SELECT COUNT(*) FROM messages WHERE receiver_id = ?"
        " AND substr(created_at, 1, 10) = ?",
        (user_id, today),
    )
    msg_total = await _scalar(
        "SELECT COUNT(*) FROM messages WHERE receiver_id = ?", (user_id,)
    )
    views_today = await _scalar(
        "SELECT COUNT(*) FROM link_views WHERE owner_id = ?"
        " AND substr(created_at, 1, 10) = ?",
        (user_id, today),
    )
    views_total = await _scalar(
        "SELECT COUNT(*) FROM link_views WHERE owner_id = ?", (user_id,)
    )
    return {
        "msg_today": msg_today,
        "views_today": views_today,
        "pop_today": _popularity(msg_today, views_today),
        "msg_total": msg_total,
        "views_total": views_total,
        "pop_total": _popularity(msg_total, views_total),
    }


async def global_stats() -> dict[str, int]:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return {
        "users": await _scalar("SELECT COUNT(*) FROM users"),
        "active_users": await _scalar("SELECT COUNT(*) FROM users WHERE stopped_bot = 0"),
        "new_today": await _scalar(
            "SELECT COUNT(*) FROM users WHERE substr(created_at, 1, 10) = ?", (today,)
        ),
        "messages": await _scalar("SELECT COUNT(*) FROM messages"),
        "messages_today": await _scalar(
            "SELECT COUNT(*) FROM messages WHERE substr(created_at, 1, 10) = ?", (today,)
        ),
        "blocks": await _scalar("SELECT COUNT(*) FROM blocks"),
        "views": await _scalar("SELECT COUNT(*) FROM link_views"),
    }


async def delete_message(message_row_id: int) -> None:
    await db().execute("DELETE FROM messages WHERE id = ?", (message_row_id,))
    await db().commit()
