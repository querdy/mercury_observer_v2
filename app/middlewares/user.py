from typing import Any, Dict, Awaitable, Callable

from aiogram import BaseMiddleware, types
from aiogram.types import CallbackQuery, TelegramObject

from app.schemas.user import UserCreateSchema


class UserMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: TelegramObject | CallbackQuery,
            data: Dict[str, Any],
    ) -> Any:
        try:
            user_id = event.message.from_user.id
            username = event.message.from_user.username
            fullname = event.message.from_user.full_name
        except AttributeError:
            user_id = event.callback_query.from_user.id
            username = event.callback_query.from_user.username
            fullname = event.callback_query.from_user.full_name
        data['user'] = await data['db'].user.update_or_create(
            UserCreateSchema(
                user_id=user_id,
                username=username,
                fullname=fullname
            )
        )
        return await handler(event, data)
