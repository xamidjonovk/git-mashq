"""Kontakt va yangi mijozni FSM orqali ro‘yxatdan o‘tkazish."""

import asyncio
import logging

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from pydantic import ValidationError

from .data import mijozni_qoshish, mijozni_telefon_bilan_topish, telefonni_tozalash
from .ui import menyuni_korsat
from ..schemas import MijozKirish

logger = logging.getLogger(__name__)


class Royxat(StatesGroup):
    kontakt = State()
    ism = State()
    manzil = State()


def register_registration_handlers(router: Router, engine) -> None:
    @router.message(CommandStart())
    async def start(message: Message, state: FSMContext) -> None:
        if message.chat.type != ChatType.PRIVATE:
            await message.answer("Botdan shaxsiy chatda foydalaning.")
            return
        await state.clear()
        await state.set_state(Royxat.kontakt)
        tugma = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="📱 O‘z telefonimni ulashish", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        await message.answer("Boshlash uchun o‘z kontaktingizni ulashing.", reply_markup=tugma)

    @router.message(Royxat.kontakt, F.contact)
    async def kontakt(message: Message, state: FSMContext) -> None:
        if not message.from_user or message.contact.user_id != message.from_user.id:
            await message.answer("Faqat o‘z kontaktingizni Telegram tugmasi bilan yuboring.")
            return
        try:
            telefon = telefonni_tozalash(message.contact.phone_number)
        except ValueError as exc:
            await message.answer(str(exc))
            return
        mijoz_id = await asyncio.to_thread(mijozni_telefon_bilan_topish, engine, telefon)
        if mijoz_id is not None:
            await state.update_data(mijoz_id=mijoz_id, savat={})
            await state.set_state(None)
            await message.answer("Xush kelibsiz!", reply_markup=ReplyKeyboardRemove())
            await menyuni_korsat(message)
            return
        await state.update_data(telefon=telefon)
        await state.set_state(Royxat.ism)
        await message.answer(
            "Ism va familiyangizni yozing. Masalan: Ali Valiyev", reply_markup=ReplyKeyboardRemove()
        )

    @router.message(Royxat.kontakt)
    async def kontakt_kerak(message: Message) -> None:
        await message.answer("Pastdagi tugma orqali o‘z kontaktingizni yuboring.")

    @router.message(Royxat.ism, F.text)
    async def ism(message: Message, state: FSMContext) -> None:
        bolaklar = message.text.strip().split(maxsplit=1)
        if len(bolaklar) != 2 or min(map(len, bolaklar)) < 2:
            await message.answer("Ism va familiyani alohida yozing. Masalan: Ali Valiyev")
            return
        await state.update_data(ism=bolaklar[0], familiya=bolaklar[1])
        await state.set_state(Royxat.manzil)
        await message.answer("Yetkazish manzilini yozing.")

    @router.message(Royxat.manzil, F.text)
    async def manzil(message: Message, state: FSMContext) -> None:
        data = await state.get_data()
        try:
            kirish = MijozKirish(
                ism=data["ism"],
                familiya=data["familiya"],
                telefon=data["telefon"],
                manzil=message.text.strip(),
            )
        except (ValidationError, KeyError):
            await message.answer("Manzilni aniqroq yozing.")
            return
        try:
            mijoz_id = await asyncio.to_thread(mijozni_qoshish, engine, kirish)
        except Exception:
            logger.exception("Mijozni ro‘yxatdan o‘tkazish xatosi")
            await message.answer("Ro‘yxatdan o‘tishda xato bo‘ldi. Keyinroq qayta urinib ko‘ring.")
            return
        await state.update_data(mijoz_id=mijoz_id, savat={})
        await state.set_state(None)
        await message.answer("Ro‘yxatdan o‘tdingiz!")
        await menyuni_korsat(message)

    @router.message(Command("menu"))
    async def menu(message: Message, state: FSMContext) -> None:
        data = await state.get_data()
        if data.get("mijoz_id") is None:
            await message.answer("Avval /start orqali ro‘yxatdan o‘ting.")
            return
        await menyuni_korsat(message)