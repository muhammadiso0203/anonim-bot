"""FSM holatlari."""
from aiogram.fsm.state import State, StatesGroup


class AnonSend(StatesGroup):
    """Foydalanuvchi kimgadir anonim xabar yozyapti."""
    writing = State()


class AnonReply(StatesGroup):
    """Kelgan xabarga javob yozyapti."""
    writing = State()


class Issue(StatesGroup):
    """Foydalanuvchi g'oya / shikoyat yozyapti (/issue)."""
    writing = State()


class AdminBroadcast(StatesGroup):
    """Admin barchaga xabar yozyapti."""
    writing = State()


class AdminAdd(StatesGroup):
    """Yangi admin ID'si kutilyapti."""
    writing = State()


class EmojiSet(StatesGroup):
    """Yangi emoji kutilyapti."""
    waiting = State()
