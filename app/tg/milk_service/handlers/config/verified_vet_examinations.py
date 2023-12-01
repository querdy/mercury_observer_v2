from aiogram import Router, Bot, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery

from app.databases.mongo import Database
from app.schemas.milk_service import MilkPushSchema, MilkPullSchema, VetExamination
from app.settings import saved_msg
from app.tg.milk_service.callback import MilkEditConfigCallback, MilkEditVerifiedVetExaminationCallback
from app.tg.milk_service.keyboard import edit_verified_vet_examination_kb
from app.tg.milk_service.utils import get_config_answer

router = Router()


@router.callback_query(MilkEditConfigCallback.filter(F.action == 'verified_vet_examination'))
async def edit_verified_vet_examination_handler(callback: CallbackQuery, db: Database, bot: Bot):
    config = await db.milk_service_config.get_by_user_id(user_id=callback.from_user.id)
    await bot.edit_message_reply_markup(
        chat_id=saved_msg[callback.from_user.id]['chat_id'],
        message_id=saved_msg[callback.from_user.id]['msg_id'],
        reply_markup=edit_verified_vet_examination_kb(vet_examinations=config.verified_vet_examinations)
    )


@router.callback_query(MilkEditVerifiedVetExaminationCallback.filter(F.action == "add"))
async def add_verified_transaction_type_handler(callback: CallbackQuery, db: Database):
    config = await db.milk_service_config.push(
        field="verified_vet_examinations",
        data=MilkPushSchema(
            user_id=callback.from_user.id,
            items=[VetExamination[f"{MilkEditVerifiedVetExaminationCallback.unpack(callback.data).value}"].value]
        )
    )
    try:
        await callback.message.edit_text(
            text=get_config_answer(config),
            reply_markup=edit_verified_vet_examination_kb(vet_examinations=config.verified_vet_examinations)
        )
    except TelegramBadRequest:
        pass


@router.callback_query(MilkEditVerifiedVetExaminationCallback.filter(F.action == 'delete'))
async def delete_verified_transaction_type_handler(callback: CallbackQuery, db: Database):
    config = await db.milk_service_config.pull(
        field="verified_vet_examinations",
        data=MilkPullSchema(
            user_id=callback.from_user.id,
            item=VetExamination[f"{MilkEditVerifiedVetExaminationCallback.unpack(callback.data).value}"].value
        )
    )
    try:
        await callback.message.edit_text(
            text=get_config_answer(config),
            reply_markup=edit_verified_vet_examination_kb(vet_examinations=config.verified_vet_examinations)
        )
    except TelegramBadRequest:
        pass
