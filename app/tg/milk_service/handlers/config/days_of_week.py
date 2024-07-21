from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery

from app.databases.mongo import Database
from app.schemas.base import PushSchema, PullSchema
from app.settings import saved_msg
from app.tg.milk_service.callback import MilkEditConfigCallback, MilkEditDaysOfWeekCallback
from app.tg.milk_service.keyboard import edit_days_of_week_kb
from app.tg.milk_service.utils import get_config_answer

router = Router()


@router.callback_query(MilkEditConfigCallback.filter(F.action == 'days_of_week'))
async def edit_verified_transaction_type_handler(callback: CallbackQuery, db: Database, bot: Bot):
    config = await db.milk_service_config.get_by_user_id(user_id=callback.from_user.id)
    await bot.edit_message_reply_markup(
        chat_id=saved_msg[callback.from_user.id]['chat_id'],
        message_id=saved_msg[callback.from_user.id]['msg_id'],
        reply_markup=edit_days_of_week_kb(days_of_week=config.days_of_week)
    )


@router.callback_query(MilkEditDaysOfWeekCallback.filter(F.action == "add"))
async def add_verified_transaction_type_handler(callback: CallbackQuery, db: Database):
    config = await db.milk_service_config.push(
        field="days_of_week",
        data=PushSchema(
            user_id=callback.from_user.id,
            items=[int(MilkEditDaysOfWeekCallback.unpack(callback.data).value)]
        )
    )
    try:
        await callback.message.edit_text(
            text=get_config_answer(config),
            reply_markup=edit_days_of_week_kb(days_of_week=config.days_of_week)
        )
    except TelegramBadRequest:
        pass


@router.callback_query(MilkEditDaysOfWeekCallback.filter(F.action == 'delete'))
async def delete_verified_transaction_type_handler(callback: CallbackQuery, db: Database):
    config = await db.milk_service_config.pull(
        field="days_of_week",
        data=PullSchema(
            user_id=callback.from_user.id,
            item=int(MilkEditDaysOfWeekCallback.unpack(callback.data).value)
        )
    )
    try:
        await callback.message.edit_text(
            text=get_config_answer(config),
            reply_markup=edit_days_of_week_kb(days_of_week=config.days_of_week)
        )
    except TelegramBadRequest:
        pass
