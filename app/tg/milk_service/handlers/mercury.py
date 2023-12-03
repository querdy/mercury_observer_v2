from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery
from loguru import logger

from app.databases.mongo import Database
from app.schemas.milk_service import MilkConfigSchema
from app.schemas.user import UserSchema
from app.settings import saved_msg
from app.tg.milk_service.callback import MilkMainCallback
from app.tg.milk_service.keyboard import main_kb
from app.tg.milk_service.utils import get_observer_answer
from app.tg.scheduler import SchedulerRepo
from app.vetis.mercury import Mercury
from app.vetis.schemas.milk import MilkRequestSchema, config_context

router = Router()


async def run_observer(db: Database, callback: CallbackQuery, user: UserSchema, config: MilkConfigSchema):
    mercury = Mercury(db=db, user_id=callback.from_user.id)
    await mercury.login(user.mercury_auth_data.login, user.mercury_auth_data.password)
    enterprises_with_request = mercury.filter_enterprises_by_patterns(
        mercury.filter_enterprises_with_request(
            await mercury.get_enterprises_from_main_page()),
        config.enterprise_patterns
    )
    if not enterprises_with_request:
        logger.info(f"{callback.from_user.full_name} - Заявки отсутствуют")
    for enterprise in enterprises_with_request:
        await mercury.select_enterprise(enterprise.number)
        transaction_numbers = await mercury.get_request_transactions_numbers()
        with config_context(config):
            requests: list[MilkRequestSchema] = [MilkRequestSchema(
                **(await mercury.get_transaction_data(transaction_number)), number=transaction_number
            ) for transaction_number in transaction_numbers]
        for request in requests:
            if request.is_valid():
                transaction = await mercury.accept_request(request=request)
                request.confirmed = await mercury.confirm_transaction(transaction=transaction)
        for msg in get_observer_answer(enterprise=enterprise, requests=requests):
            await callback.message.answer(msg)


@router.callback_query(MilkMainCallback.filter(F.action == 'single'))
async def start_single_parse_handler(callback: CallbackQuery, db: Database):
    user = await db.user.get_by_user_id(callback.from_user.id)
    config = await db.milk_service_config.get_by_user_id(callback.from_user.id)
    await run_observer(db=db, callback=callback, user=user, config=config)
    await callback.answer()


@router.callback_query(MilkMainCallback.filter(F.action == 'loop'))
async def start_loop_parse_handler(callback: CallbackQuery, db: Database, scheduler: SchedulerRepo, bot: Bot):
    user = await db.user.get_by_user_id(callback.from_user.id)
    config = await db.milk_service_config.get_by_user_id(callback.from_user.id)
    if scheduler.create_job(run_observer, {'db': db, 'callback': callback, 'user': user, 'config': config},
                            every_minute=config.schedule_every_minute, user_id=callback.from_user.id,
                            hour_start=config.start_hour, hour_end=config.end_hour, minute_start=config.start_minute,
                            minute_end=config.end_minute, days_of_week=config.days_of_week):
        try:
            await bot.edit_message_reply_markup(
                chat_id=saved_msg[callback.from_user.id]['chat_id'],
                message_id=saved_msg[callback.from_user.id]['msg_id'],
                reply_markup=main_kb(is_schedule=bool(scheduler.get_user_jobs(callback.from_user.id)))
            )
        except TelegramBadRequest:
            pass
    else:
        await callback.message.answer(f"Не удалось запустить периодическую проверку!")
        await callback.answer()


@router.callback_query(MilkMainCallback.filter(F.action == 'stop_loop'))
async def stop_loop_parse_handler(callback: CallbackQuery, scheduler: SchedulerRepo, bot: Bot):
    scheduler.remove_user_jobs(user_id=callback.from_user.id)
    try:
        await bot.edit_message_reply_markup(
            chat_id=saved_msg[callback.from_user.id]['chat_id'],
            message_id=saved_msg[callback.from_user.id]['msg_id'],
            reply_markup=main_kb(is_schedule=bool(scheduler.get_user_jobs(callback.from_user.id)))
        )
    except TelegramBadRequest:
        pass
