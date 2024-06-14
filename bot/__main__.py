import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from prometheus_client import start_http_server, make_asgi_app, start_wsgi_server

from bot.handlers.handler import router
from bot.middleware.apscheduler_middleware import SchedulerMiddleware
from bot.db.config import settings


async def main():

    logging.basicConfig(
        level=logging.INFO,
        # filename='data/errors.log',
        format="%(asctime)s - %(name)s - %(message)s",
    )

    bot = Bot(token=settings.bot_token)
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
