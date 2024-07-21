from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.databases.mongo import Database
from app.schemas.base import PushSchema, PullSchema
from app.settings import saved_msg
from app.tg.milk_service.callback import MilkEditEnterprisePatternsCallback, MilkEditConfigCallback
from app.tg.milk_service.keyboard import edit_enterprise_patterns_kb
from app.tg.milk_service.utils import get_config_answer
from app.tg.states import EditEnterprisePatternsState

router = Router()


@router.callback_query(MilkEditConfigCallback.filter(F.action == 'enterprise_patterns'))
async def edit_enterprise_patterns_handler(callback: CallbackQuery, state: FSMContext, db: Database):
    await state.clear()
    config = await db.milk_service_config.get_by_user_id(user_id=callback.from_user.id)
    await callback.message.edit_reply_markup(
        reply_markup=edit_enterprise_patterns_kb(enterprises=config.enterprise_patterns)
    )


@router.callback_query(MilkEditEnterprisePatternsCallback.filter(F.action == 'delete'))
async def delete_enterprise_pattern_handler(callback: CallbackQuery, db: Database):
    config = await db.milk_service_config.pull(
        field="enterprise_patterns",
        data=PullSchema(
            user_id=callback.from_user.id,
            item=MilkEditEnterprisePatternsCallback.unpack(callback.data).value
        )
    )
    try:
        await callback.message.edit_text(
            text=get_config_answer(config),
            reply_markup=edit_enterprise_patterns_kb(enterprises=config.enterprise_patterns)
        )
    except TelegramBadRequest:
        pass


@router.callback_query(MilkEditEnterprisePatternsCallback.filter(F.action == 'add'))
async def add_enterprise_pattern_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditEnterprisePatternsState.get_value)
    await callback.answer()
    await callback.message.answer(
        text=f"Введите название площадки для добавления",
    )


@router.message(EditEnterprisePatternsState.get_value)
async def get_new_enterprise_pattern_handler(message: Message, db: Database, bot: Bot):
    try:
        MilkEditEnterprisePatternsCallback(action="delete", value=message.text).pack()
    except ValueError:
        await message.answer(
            text=f"Шаблон названия площадки слишком длинный. Максимум 52 символа (кириллица занимает 2 символа)",
        )
        return
    else:
        config = await db.milk_service_config.push(
            field="enterprise_patterns",
            data=PushSchema(
                user_id=message.from_user.id,
                items=[message.text]
            )
        )
        try:
            await bot.edit_message_text(
                chat_id=saved_msg[message.from_user.id]['chat_id'],
                message_id=saved_msg[message.from_user.id]['msg_id'],
                text=get_config_answer(config),
                reply_markup=edit_enterprise_patterns_kb(enterprises=config.enterprise_patterns)
            )
        except TelegramBadRequest:
            pass
