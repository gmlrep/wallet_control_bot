from typing import Dict, Any, Callable, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bot.utils.ton_api import TonApi


class TonMiddleware(BaseMiddleware):
    def __init__(self, ton: TonApi):
        self.ton = ton

    async def __call__(self,
                       handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any],
                       ) -> Any:
        data['ton'] = self.ton
        return await handler(event, data)
