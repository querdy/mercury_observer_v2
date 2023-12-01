from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery

from app.databases.mongo import Database
from app.schemas.milk_service import ScheduleEveryMinute, MilkConfigSchema
from app.settings import saved_msg
from app.tg.milk_service.callback import MilkEditConfigCallback, MilkEditScheduleEveryMinuteCallback
from app.tg.milk_service.keyboard import edit_schedule_every_minute_kb, edit_config_kb
from app.tg.milk_service.utils import get_config_answer

router = Router()


@router.callback_query(MilkEditConfigCallback.filter(F.action == 'schedule_every_minute'))
async def edit_schedule_every_minute_handler(callback: CallbackQuery, bot: Bot):
    try:
        await bot.edit_message_reply_markup(
            chat_id=saved_msg[callback.from_user.id]['chat_id'],
            message_id=saved_msg[callback.from_user.id]['msg_id'],
            reply_markup=edit_schedule_every_minute_kb()
        )
    except TelegramBadRequest:
        pass


@router.callback_query(MilkEditScheduleEveryMinuteCallback.filter(F.action == "schedule"))
async def set_schedule_every_time_handler(callback: CallbackQuery, db: Database, bot: Bot):
    config = await db.milk_service_config.update(MilkConfigSchema(
        user_id=callback.from_user.id,
        schedule_every_minute=ScheduleEveryMinute(int(MilkEditScheduleEveryMinuteCallback.unpack(callback.data).value))
    ))
    try:
        await bot.edit_message_text(
            chat_id=saved_msg[callback.from_user.id]['chat_id'],
            message_id=saved_msg[callback.from_user.id]['msg_id'],
            text=get_config_answer(config),
            reply_markup=edit_config_kb()
        )
    except TelegramBadRequest:
        pass
