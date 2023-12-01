from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.databases.mongo import Database
from app.schemas.milk_service import MilkConfigSchema
from app.settings import saved_msg
from app.tg.milk_service.callback import MilkEditConfigCallback
from app.tg.milk_service.keyboard import edit_config_kb
from app.tg.milk_service.utils import get_config_answer
from app.tg.states import EditIntervalState

router = Router()


@router.callback_query(MilkEditConfigCallback.filter(F.action == 'interval'))
async def edit_interval_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditIntervalState.get_interval)
    await callback.message.answer(
        text=f'Введите интервал проверки в формате <b>ЧЧ.ММ-ЧЧ.ММ</b>.\nНапример, "00.00-23.59"',
    )
    await callback.answer()


@router.message(EditIntervalState.get_interval)
async def set_interval_handler(message: Message, db: Database, bot: Bot):
    time = [time.split('.') for time in message.text.replace(' ', '').split('-')]
    try:
        config = await db.milk_service_config.update(
            MilkConfigSchema(
                user_id=message.from_user.id,
                start_hour=time[0][0],
                start_minute=time[0][1],
                end_hour=time[1][0],
                end_minute=time[1][1]
            )
        )
        try:
            await bot.edit_message_text(
                chat_id=saved_msg[message.from_user.id]['chat_id'],
                message_id=saved_msg[message.from_user.id]['msg_id'],
                text=get_config_answer(config),
                reply_markup=edit_config_kb()
            )
        except TelegramBadRequest:
            pass
    except (ValueError, IndexError):
        await message.answer(f"Неверный формат ввода. Введите интервал проверки в формате <b>ЧЧ.ММ-ЧЧ.ММ</b>")
