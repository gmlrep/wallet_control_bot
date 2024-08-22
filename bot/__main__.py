import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.handlers.handler import router, send_alert_user
from bot.middleware.apscheduler_middleware import SchedulerMiddleware
from bot.db.config import settings
from bot.middleware.ton_midlware import TonMiddleware
from bot.utils.ton_api import TonApi


async def main():

    logging.basicConfig(
        level=logging.INFO,
        filename='data/errors.log',
        format="%(asctime)s - %(name)s - %(message)s",
    )

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
    ton = TonApi(api_key=settings.api_token)

    dp.update.middleware.register(TonMiddleware(ton))
    dp.update.middleware.register(SchedulerMiddleware(scheduler))

    scheduler.start()
    time = settings.time_scheduler.split(':')
    scheduler.add_job(send_alert_user, 'cron', hour=time[0], minute=time[1],
                      kwargs={'bot': bot}, id='send_msg')

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
