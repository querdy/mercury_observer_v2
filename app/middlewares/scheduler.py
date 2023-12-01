from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.tg.scheduler import SchedulerRepo


class SchedulerMiddleware(BaseMiddleware):
    def __init__(self, scheduler: SchedulerRepo):
        self.scheduler = scheduler
        self.scheduler.remove_all_jobs()

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        data['scheduler'] = self.scheduler
        return await handler(event, data)
