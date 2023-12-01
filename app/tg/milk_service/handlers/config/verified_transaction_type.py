from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery

from app.databases.mongo import Database
from app.schemas.milk_service import MilkPullSchema, MilkPushSchema
from app.settings import saved_msg
from app.tg.milk_service.callback import MilkEditConfigCallback, MilkEditVerifiedTransactionTypeCallback
from app.tg.milk_service.keyboard import edit_verified_transaction_type_kb
from app.tg.milk_service.utils import get_config_answer

router = Router()


@router.callback_query(MilkEditConfigCallback.filter(F.action == 'verified_transaction_type'))
async def edit_verified_transaction_type_handler(callback: CallbackQuery, db: Database, bot: Bot):
    config = await db.milk_service_config.get_by_user_id(user_id=callback.from_user.id)
    await bot.edit_message_reply_markup(
        chat_id=saved_msg[callback.from_user.id]['chat_id'],
        message_id=saved_msg[callback.from_user.id]['msg_id'],
        reply_markup=edit_verified_transaction_type_kb(transaction_types=config.verified_transaction_types)
    )


@router.callback_query(MilkEditVerifiedTransactionTypeCallback.filter(F.action == "add"))
async def add_verified_transaction_type_handler(callback: CallbackQuery, db: Database):
    config = await db.milk_service_config.push(
        field="verified_transaction_types",
        data=MilkPushSchema(
            user_id=callback.from_user.id,
            items=[MilkEditVerifiedTransactionTypeCallback.unpack(callback.data).value]
        )
    )
    try:
        await callback.message.edit_text(
            text=get_config_answer(config),
            reply_markup=edit_verified_transaction_type_kb(transaction_types=config.verified_transaction_types)
        )
    except TelegramBadRequest:
        pass


@router.callback_query(MilkEditVerifiedTransactionTypeCallback.filter(F.action == 'delete'))
async def delete_verified_transaction_type_handler(callback: CallbackQuery, db: Database):
    config = await db.milk_service_config.pull(
        field="verified_transaction_types",
        data=MilkPullSchema(
            user_id=callback.from_user.id,
            item=MilkEditVerifiedTransactionTypeCallback.unpack(callback.data).value
        )
    )
    try:
        await callback.message.edit_text(
            text=get_config_answer(config),
            reply_markup=edit_verified_transaction_type_kb(transaction_types=config.verified_transaction_types)
        )
    except TelegramBadRequest:
        pass
