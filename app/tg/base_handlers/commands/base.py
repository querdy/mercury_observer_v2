from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from loguru import logger

from app.schemas.user import UserSchema
from app.tg.keyboard import ReplyKeyboard

router = Router()


@router.message(Command('start'))
async def command_start_handler(message: Message, state: FSMContext, user: UserSchema) -> None:
    await state.clear()
    logger.info(f"user {user.username} {user.user_id} {user.fullname} push /start")
    await message.answer(f"Hi <b>{user.username}</b>!", reply_markup=ReplyKeyboard.main())
