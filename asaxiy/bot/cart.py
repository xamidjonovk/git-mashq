"""Vaqtinchalik savat va 14-darsdagi buyurtma servisiga ulanish."""

import asyncio
import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from pydantic import ValidationError

from .data import savat_mazmuni
from .ui import menyu_tugmalari
from ..schemas import BuyurtmaSorovi, SavatQatori
from ..service import buyurtma_ber

logger = logging.getLogger(__name__)


def register_cart_handlers(router: Router, engine) -> None:
    @router.callback_query(F.data == "savat")
    async def savatni_korsat(callback: CallbackQuery, state: FSMContext) -> None:
        await callback.answer()
        savat = (await state.get_data()).get("savat", {})
        if not savat:
            await callback.message.answer("Savat bo‘sh.", reply_markup=menyu_tugmalari())
            return
        qatorlar, jami = await asyncio.to_thread(savat_mazmuni, engine, savat)
        tugmalar = InlineKeyboardBuilder()
        tugmalar.button(text="✅ Buyurtma berish", callback_data="buyurtma")
        tugmalar.button(text="🗑 Savatni tozalash", callback_data="tozala")
        tugmalar.adjust(1)
        await callback.message.answer(
            "Savat:\n"
            + "\n".join(qatorlar)
            + f"\nTaxminiy jami: {jami:,} so‘m\nYakuniy narx buyurtmada DBdan olinadi.",
            reply_markup=tugmalar.as_markup(),
        )

    @router.callback_query(F.data == "tozala")
    async def savatni_tozalash(callback: CallbackQuery, state: FSMContext) -> None:
        await callback.answer()
        await state.update_data(savat={})
        await callback.message.answer("Savat tozalandi.", reply_markup=menyu_tugmalari())

    @router.callback_query(F.data == "buyurtma")
    async def buyurtma(callback: CallbackQuery, state: FSMContext) -> None:
        await callback.answer()
        data = await state.get_data()
        if data.get("mijoz_id") is None:
            await callback.message.answer("Avval /start orqali ro‘yxatdan o‘ting.")
            return
        savat = data.get("savat", {})
        if not savat:
            await callback.message.answer("Savat bo‘sh.")
            return
        try:
            sorov = BuyurtmaSorovi(
                mijoz_id=data["mijoz_id"],
                qatorlar=[
                    SavatQatori(mahsulot_id=int(id), soni=soni) for id, soni in savat.items()
                ],
            )
            natija = await asyncio.to_thread(buyurtma_ber, engine, sorov)
        except (ValidationError, ValueError) as exc:
            await callback.message.answer(f"Buyurtma bajarilmadi: {exc}")
            return
        except Exception:
            logger.exception("Buyurtmani yaratish xatosi")
            await callback.message.answer("Buyurtmani saqlashda xato bo‘ldi. Qayta tekshiring.")
            return
        await state.update_data(savat={})
        await callback.message.answer(
            f"Buyurtma #{natija.id} qabul qilindi.\nJami: {natija.umumiy_summa:,} so‘m.",
            reply_markup=menyu_tugmalari(),
        )