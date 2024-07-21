from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.databases.mongo import Database
from app.schemas.base import PushSchema, PullSchema
from app.settings import saved_msg
from app.tg.milk_service.callback import MilkEditConfigCallback, MilkEditVerifiedProductsCallback
from app.tg.milk_service.keyboard import edit_verified_products_kb
from app.tg.milk_service.utils import get_config_answer
from app.tg.states import EditVerifiedProductsState

router = Router()


@router.callback_query(MilkEditConfigCallback.filter(F.action == 'verified_products'))
async def edit_verified_products_handler(callback: CallbackQuery, state: FSMContext, db: Database):
    await state.clear()
    config = await db.milk_service_config.get_by_user_id(user_id=callback.from_user.id)
    await callback.message.edit_reply_markup(
        reply_markup=edit_verified_products_kb(verified_products=config.verified_products)
    )


@router.callback_query(MilkEditVerifiedProductsCallback.filter(F.action == 'delete'))
async def delete_verified_product_handler(callback: CallbackQuery, db: Database):
    config = await db.milk_service_config.pull(
        field="verified_products",
        data=PullSchema(
            user_id=callback.from_user.id,
            item=MilkEditVerifiedProductsCallback.unpack(callback.data).value
        )
    )
    try:
        await callback.message.edit_text(
            text=get_config_answer(config),
            reply_markup=edit_verified_products_kb(verified_products=config.verified_products)
        )
    except TelegramBadRequest:
        pass


@router.callback_query(MilkEditVerifiedProductsCallback.filter(F.action == 'add'))
async def add_verified_products_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditVerifiedProductsState.get_value)
    await callback.answer()
    await callback.message.answer(
        text=f"Введите название продукта (часть названия) для добавления",
    )


@router.message(EditVerifiedProductsState.get_value)
async def get_new_verified_product_handler(message: Message, db: Database, bot: Bot):
    config = await db.milk_service_config.push(
        field="verified_products",
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
            reply_markup=edit_verified_products_kb(verified_products=config.verified_products)
        )
    except TelegramBadRequest:
        pass
