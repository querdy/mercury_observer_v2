from typing import Any, Dict, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, TelegramObject
from pydantic import MongoDsn

from app.databases.mongo import Database


class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, url: MongoDsn):
        self.url: MongoDsn = url

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject | CallbackQuery, 
        data: Dict[str, Any],
    ) -> Any:
        data['db'] = Database(url=self.url)
        return await handler(event, data)
