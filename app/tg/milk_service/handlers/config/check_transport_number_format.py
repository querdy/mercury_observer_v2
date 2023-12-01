from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery

from app.databases.mongo import Database
from app.schemas.milk_service import MilkReverseBooleanSchema
from app.tg.milk_service.callback import MilkEditConfigCallback
from app.tg.milk_service.keyboard import edit_config_kb
from app.tg.milk_service.utils import get_config_answer

router = Router()


@router.callback_query(MilkEditConfigCallback.filter(F.action == 'check_transport_number_format'))
async def edit_check_transport_number_format_handler(callback: CallbackQuery, db: Database):
    config = await db.milk_service_config.reverse_boolean_field(data=MilkReverseBooleanSchema(
        user_id=callback.from_user.id,
        field="check_transport_number_format"
    ))
    try:
        await callback.message.edit_text(
            text=get_config_answer(config),
            reply_markup=edit_config_kb()
        )
    except TelegramBadRequest:
        pass
    await callback.answer()
