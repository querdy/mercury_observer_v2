from aiogram import Router, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from app.databases.mongo import Database
from app.schemas.milk_service import DefaultMilkServiceConfigSchema
from app.schemas.user import UserSchema
from app.settings import saved_msg, messages_for_delete
from app.tg.keyboard import not_mercury_auth_data_kb
from app.tg.milk_service.keyboard import main_kb
from app.tg.milk_service.utils import get_config_answer
from app.tg.scheduler import SchedulerRepo

router = Router()


@router.message(Command('milk'))
async def milk_service_handler(message: Message, user: UserSchema, db: Database, scheduler: SchedulerRepo):
    if user.mercury_auth_data is None:
        await message.answer(
            text=f"Отсутствуют данные для авторизации в Меркурии",
            reply_markup=not_mercury_auth_data_kb()
        )
    else:
        config = await db.milk_service_config.get_or_create(
            DefaultMilkServiceConfigSchema(user_id=message.from_user.id)
        )
        msg = await message.answer(
            text=get_config_answer(config),
            reply_markup=main_kb(is_schedule=bool(scheduler.get_user_jobs(message.from_user.id, service_name="milk")))
        )
        saved_msg.update({message.from_user.id: {"msg_id": msg.message_id, "chat_id": msg.chat.id}})
        # messages_for_delete.append({"message_id": msg.message_id, "chat_id": msg.chat.id})


@router.callback_query(lambda callback: callback.data == 'milk_main')
async def milk_service_back_handler(callback: CallbackQuery, bot: Bot, scheduler: SchedulerRepo):
    try:
        await bot.edit_message_reply_markup(
            chat_id=saved_msg[callback.from_user.id]['chat_id'],
            message_id=saved_msg[callback.from_user.id]['msg_id'],
            reply_markup=main_kb(is_schedule=bool(scheduler.get_user_jobs(callback.from_user.id, service_name="milk")))
        )
    except TelegramBadRequest:
        pass
