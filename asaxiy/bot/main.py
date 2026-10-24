"""Botning kirish nuqtasi: uch handler guruhini bitta Routerga ulash."""


from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage

from .cart import register_cart_handlers
from .catalog import register_catalog_handlers
from .registration import register_registration_handlers
from ..config import Settings
from ..database import make_engine


def build_router(engine) -> Router:
    router = Router()
    register_registration_handlers(router, engine)
    register_catalog_handlers(router, engine)
    register_cart_handlers(router, engine)
    return router


async def main() -> None:
    secret = Settings().bot_token
    if secret is None or not secret.get_secret_value():
        raise RuntimeError("BOT_TOKEN .env yoki muhitda berilmagan")
    token = secret.get_secret_value()
    engine = make_engine()
    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher.include_router(build_router(engine))
    try:
        async with Bot(token=token) as bot:
            await dispatcher.start_polling(bot, handle_as_tasks=False)
    finally:
        engine.dispose()

