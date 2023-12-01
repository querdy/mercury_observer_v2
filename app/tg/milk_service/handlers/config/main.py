from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.tg.milk_service.callback import MilkMainCallback
from app.tg.milk_service.keyboard import edit_config_kb

router = Router()


@router.callback_query(MilkMainCallback.filter(F.action == 'edit'))
async def milk_service_edit_menu_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=edit_config_kb())
