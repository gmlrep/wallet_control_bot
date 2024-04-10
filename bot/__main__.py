import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

from bot.handlers.handler import router, send_alert_user
from bot.middleware.apscheduler_middleware import SchedulerMiddleware

load_dotenv()


async def main():

    logging.basicConfig(
        level=logging.ERROR,
        filename='data/errors.log',
        format="%(asctime)s - %(name)s - %(message)s",
    )

    bot = Bot(token=os.getenv('BOT_TOKEN'))
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')

    dp.update.middleware.register(SchedulerMiddleware(scheduler))

    scheduler.start()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
