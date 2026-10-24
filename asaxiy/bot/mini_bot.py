import asyncio
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from asaxiy.config import Settings

router = Router()

@router.message(CommandStart())
async def start(message: Message):
    await message.answer("Asaxiy do‘koniga xush kelibsiz!")

async def main():
    secret = Settings().bot_token
    if secret is None or not secret.get_secret_value():
        raise RuntimeError("BOT_TOKEN .env ichida yo‘q")
    dispatcher = Dispatcher()
    dispatcher.include_router(router)
    async with Bot(token=secret.get_secret_value()) as bot:
        await dispatcher.start_polling(bot, handle_as_tasks=False)

if __name__ == "__main__":
    asyncio.run(main())