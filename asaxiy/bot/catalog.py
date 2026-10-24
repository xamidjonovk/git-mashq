"""Kategoriya va mahsulot callbacklari hamda savatga qo‘shish."""

import asyncio

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .data import kategoriyalarni_olish, mahsulotlarni_olish, mahsulotni_olish
from .ui import callback_id, menyu_tugmalari


def register_catalog_handlers(router: Router, engine) -> None:
    @router.callback_query(F.data == "kategoriyalar")
    async def kategoriyalar(callback: CallbackQuery, state: FSMContext) -> None:
        await callback.answer()
        if (await state.get_data()).get("mijoz_id") is None:
            await callback.message.answer("Avval /start orqali ro‘yxatdan o‘ting.")
            return
        royxat = await asyncio.to_thread(kategoriyalarni_olish, engine)
        if not royxat:
            await callback.message.answer(
                "Hozircha kategoriya yo‘q. Avval katalogga mahsulot qo‘shing."
            )
            return
        tugmalar = InlineKeyboardBuilder()
        for id, nomi in royxat:
            tugmalar.button(text=nomi, callback_data=f"kat:{id}")
        tugmalar.adjust(1)
        await callback.message.answer("Kategoriyani tanlang:", reply_markup=tugmalar.as_markup())

    @router.callback_query(F.data.startswith("kat:"))
    async def mahsulotlar(callback: CallbackQuery, state: FSMContext) -> None:
        await callback.answer()
        if (await state.get_data()).get("mijoz_id") is None:
            await callback.message.answer("Avval /start orqali ro‘yxatdan o‘ting.")
            return
        kategoriya_id = callback_id(callback.data)
        if kategoriya_id is None:
            await callback.message.answer("Kategoriya topilmadi.")
            return
        royxat = await asyncio.to_thread(mahsulotlarni_olish, engine, kategoriya_id)
        if not royxat:
            await callback.message.answer("Bu kategoriyada mahsulot yo‘q.")
            return
        tugmalar = InlineKeyboardBuilder()
        for id, nomi, narxi, qoldiq in royxat:
            tugmalar.button(
                text=f"{nomi} — {narxi:,} so‘m ({qoldiq} dona)",
                callback_data=f"mah:{id}",
            )
        tugmalar.adjust(1)
        await callback.message.answer("Mahsulotni tanlang:", reply_markup=tugmalar.as_markup())

    @router.callback_query(F.data.startswith("mah:"))
    async def mahsulot(callback: CallbackQuery, state: FSMContext) -> None:
        await callback.answer()
        if (await state.get_data()).get("mijoz_id") is None:
            await callback.message.answer("Avval /start orqali ro‘yxatdan o‘ting.")
            return
        mahsulot_id = callback_id(callback.data)
        if mahsulot_id is None:
            await callback.message.answer("Mahsulot topilmadi.")
            return
        topildi = await asyncio.to_thread(mahsulotni_olish, engine, mahsulot_id)
        if topildi is None:
            await callback.message.answer("Mahsulot topilmadi.")
            return
        nomi, narxi, qoldiq = topildi
        tugmalar = InlineKeyboardBuilder()
        if qoldiq > 0:
            tugmalar.button(text="➕ 1 dona savatga", callback_data=f"add:{mahsulot_id}")
        tugmalar.button(text="🛒 Savat", callback_data="savat")
        tugmalar.adjust(1)
        await callback.message.answer(
            f"{nomi}\nNarxi: {narxi:,} so‘m\nOmborda: {qoldiq} dona",
            reply_markup=tugmalar.as_markup(),
        )

    @router.callback_query(F.data.startswith("add:"))
    async def savatga_qoshish(callback: CallbackQuery, state: FSMContext) -> None:
        await callback.answer()
        data = await state.get_data()
        if data.get("mijoz_id") is None:
            await callback.message.answer("Avval /start orqali ro‘yxatdan o‘ting.")
            return
        mahsulot_id = callback_id(callback.data)
        if mahsulot_id is None:
            await callback.message.answer("Mahsulot topilmadi.")
            return
        topildi = await asyncio.to_thread(mahsulotni_olish, engine, mahsulot_id)
        if topildi is None:
            await callback.message.answer("Mahsulot topilmadi.")
            return
        nomi, _, qoldiq = topildi
        savat = dict(data.get("savat", {}))
        kalit = str(mahsulot_id)
        yangi_son = savat.get(kalit, 0) + 1
        if yangi_son > qoldiq:
            await callback.message.answer("Omborda buncha mahsulot yo‘q.")
            return
        savat[kalit] = yangi_son
        await state.update_data(savat=savat)
        await callback.message.answer(
            f"{nomi}: savatda {yangi_son} dona.", reply_markup=menyu_tugmalari()
        )