import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

from bot.handlers.handler import router, send_alert_user

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

    time = os.getenv("TIME").split(':')
    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
    scheduler.start()
    scheduler.add_job(send_alert_user, 'cron', hour=time[0], minute=time[1])

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
