from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.databases.mongo import Database
from app.schemas.mercury_auth import UpdateLoginAndPasswordSchema
from app.tg.keyboard import not_mercury_auth_data_kb
from app.tg.states import MercuryAuthDataState
from app.tg.user_service.callback import EditMercuryAuthDataCallback
from app.vetis.mercury import Mercury

router = Router()


@router.callback_query(EditMercuryAuthDataCallback.filter(F.action.lower() == "edit"))
async def set_mercury_login_callback_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(MercuryAuthDataState.login)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer('Введите логин:')


@router.message(Command('mercury_auth'))
async def set_mercury_login_command_handler(message: Message, state: FSMContext):
    await state.set_state(MercuryAuthDataState.login)
    await message.answer('Введите логин:')


@router.message(MercuryAuthDataState.login)
async def set_mercury_password_handler(message: Message, state: FSMContext):
    await state.update_data(login=message.text)
    await state.set_state(MercuryAuthDataState.password)
    await message.answer('Введите пароль:')


@router.message(MercuryAuthDataState.password)
async def check_and_save_mercury_auth_data_handler(message: Message, state: FSMContext, db: Database):
    await state.update_data(password=message.text)
    state_data = await state.get_data()
    msg = await message.answer(f"Подождите...")
    mercury = Mercury(
        db=db,
        user_id=message.from_user.id
    )
    if await mercury.login(state_data.get('login'), state_data.get('password'), new_auth=True):
        await db.mercury_auth.update_login_and_password(
            UpdateLoginAndPasswordSchema(
                user_id=message.from_user.id,
                login=state_data.get('login'),
                password=state_data.get('password')
            )
        )
        await msg.edit_text(f"Данные для входа в Меркурий сохранены")
    else:
        await msg.edit_text(
            text=f"Не удалось авторизоваться в системе Меркурий.",
            reply_markup=not_mercury_auth_data_kb()
        )
    await state.clear()
