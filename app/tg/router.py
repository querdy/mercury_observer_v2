from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from app.tg.base_handlers.commands import base
from app.tg.milk_service.router import milk_service_router
from app.tg.user_service.router import user_router


base_router = Router()
base_router.include_router(base.router)
base_router.include_router(milk_service_router)
base_router.include_router(user_router)


@base_router.message(F.text.lower() == 'отмена')
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    # await message.reply("Ок~", reply_markup=Keyboard.get_main_keyboard())


@base_router.callback_query(lambda callback: callback.data == 'cancel')
async def cancel_callback_handler(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    await callback.message.edit_reply_markup(reply_markup=None)
    # await callback.message.delete()
    if current_state is None:
        return
    await state.clear()
