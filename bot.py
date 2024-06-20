import asyncio
import logging

from aiogram import Bot
from aiogram import Dispatcher

from config import settings


async def main() -> None:
    if settings.DEBUG:
        logging.basicConfig(level=logging.INFO)

    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
