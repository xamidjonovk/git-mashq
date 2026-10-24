"""Telegram tugmalari va callback IDni ajratish."""

from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder


def menyu_tugmalari():
    tugmalar = InlineKeyboardBuilder()
    tugmalar.button(text="📚 Kategoriyalar", callback_data="kategoriyalar")
    tugmalar.button(text="🛒 Savat", callback_data="savat")
    tugmalar.adjust(2)
    return tugmalar.as_markup()


async def menyuni_korsat(message: Message) -> None:
    await message.answer("Asaxiy do‘koni: bo‘limni tanlang.", reply_markup=menyu_tugmalari())


def callback_id(data: str | None) -> int | None:
    try:
        qiymat = int((data or "").split(":", 1)[1])
    except (IndexError, ValueError):
        return None
    return qiymat if qiymat > 0 else None