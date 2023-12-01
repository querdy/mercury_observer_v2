from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.schemas.milk_service import ScheduleEveryMinute, TransactionType, VetExamination
from app.tg.milk_service.callback import MilkMainCallback, MilkEditScheduleEveryMinuteCallback, \
    MilkEditVerifiedTransactionTypeCallback, MilkEditEnterprisePatternsCallback, MilkEditVerifiedProductsCallback, \
    MilkEditConfigCallback, EditMercuryAuthDataCallback, MilkEditVerifiedVetExaminationCallback


def edit_schedule_every_minute_kb():
    buttons = [
        [InlineKeyboardButton(
            text=f"{minute} минут(-а)",
            callback_data=MilkEditScheduleEveryMinuteCallback(action="schedule", value=str(minute.value)).pack()
        )] for minute in ScheduleEveryMinute
    ]
    buttons.append([
        InlineKeyboardButton(
            text=f"Назад",
            callback_data=MilkMainCallback(action='edit').pack()
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def edit_verified_vet_examination_kb(vet_examinations: list[str]):
    buttons = []
    for vet_examination in VetExamination:
        if vet_examination.value in vet_examinations:
            buttons.append(
                [InlineKeyboardButton(
                    text=f"Удалить: {vet_examination.value}",
                    callback_data=MilkEditVerifiedVetExaminationCallback(
                        action="delete", value=str(vet_examination.name)
                    ).pack()
                )]
            )
        else:
            buttons.append(
                [InlineKeyboardButton(
                    text=f"Добавить: {vet_examination.value}",
                    callback_data=MilkEditVerifiedVetExaminationCallback(
                        action="add", value=str(vet_examination.name)
                    ).pack()
                )]
            )
    buttons.append([
        InlineKeyboardButton(
            text=f"Назад",
            callback_data=MilkMainCallback(action='edit').pack()
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def edit_verified_transaction_type_kb(transaction_types: list[str]):
    buttons = []
    for transaction_type in TransactionType:
        if transaction_type.value in transaction_types:
            buttons.append(
                [InlineKeyboardButton(
                    text=f"Удалить: {transaction_type.value}",
                    callback_data=MilkEditVerifiedTransactionTypeCallback(
                        action="delete", value=str(transaction_type.value)
                    ).pack()
                )]
            )
        else:
            buttons.append(
                [InlineKeyboardButton(
                    text=f"Добавить: {transaction_type.value}",
                    callback_data=MilkEditVerifiedTransactionTypeCallback(
                        action="add", value=str(transaction_type.value)
                    ).pack()
                )]
            )
    buttons.append([
        InlineKeyboardButton(
            text=f"Назад",
            callback_data=MilkMainCallback(action='edit').pack()
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def edit_enterprise_patterns_kb(enterprises: list[str]):
    buttons = [
        [InlineKeyboardButton(
            text=f"Удалить: {enterprise}",
            callback_data=MilkEditEnterprisePatternsCallback(action="delete", value=enterprise).pack()
        )] for enterprise in enterprises
    ]
    buttons.append([
        InlineKeyboardButton(
            text=f"Добавить",
            callback_data=MilkEditEnterprisePatternsCallback(action="add").pack()
        ),
    ])
    buttons.append([
        InlineKeyboardButton(
            text=f"Назад",
            callback_data=MilkMainCallback(action='edit').pack()
        ),
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def edit_verified_products_kb(verified_products: list[str]):
    buttons = [
        [InlineKeyboardButton(
            text=f"Удалить: {product}",
            callback_data=MilkEditVerifiedProductsCallback(action="delete", value=product).pack()
        )] for product in verified_products
    ]
    buttons.append([
        InlineKeyboardButton(
            text=f"Добавить",
            callback_data=MilkEditVerifiedProductsCallback(action="add").pack()
        ),
    ])
    buttons.append([
        InlineKeyboardButton(
            text=f"Назад",
            callback_data=MilkMainCallback(action='edit').pack()
        ),
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def edit_config_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"Периодичность проверки",
                callback_data=MilkEditConfigCallback(action='schedule_every_minute').pack()
            ),
        ],
        [
            InlineKeyboardButton(
                text=f"Отслеживаемые площадки",
                callback_data=MilkEditConfigCallback(action='enterprise_patterns').pack()
            ),
        ],
        [
            InlineKeyboardButton(
                text=f"Допустимые названия продуктов",
                callback_data=MilkEditConfigCallback(action='verified_products').pack()
            ),
        ],
        [
            InlineKeyboardButton(
                text=f"Допустимые термические состояния",
                callback_data=MilkEditConfigCallback(action='verified_transaction_type').pack()
            ),
        ],
        [
            InlineKeyboardButton(
                text=f"Допустимые статусы ВСЭ",
                callback_data=MilkEditConfigCallback(action='verified_vet_examination').pack()
            ),
        ],
        [
            InlineKeyboardButton(
                text=f"Проверка формата номера транспорта (RU)",
                callback_data=MilkEditConfigCallback(action='check_transport_number_format').pack()
            )
        ],
        [
            InlineKeyboardButton(
                text=f"Временной интервал проверки",
                callback_data=MilkEditConfigCallback(action='interval').pack()
            ),
        ],
        [
            InlineKeyboardButton(
                text=f"Назад",
                callback_data='milk_main'
            ),
        ],
    ])


def main_kb(is_schedule: bool):
    if is_schedule:
        buttons = [
            [
                InlineKeyboardButton(
                    text=f"Остановить",
                    callback_data=MilkMainCallback(action='stop_loop').pack()
                ),
            ]
        ]
    else:
        buttons = [
            [
                InlineKeyboardButton(
                    text=f"Запустить однократно",
                    callback_data=MilkMainCallback(action='single').pack()
                ),
                InlineKeyboardButton(
                    text=f"Запустить периодически",
                    callback_data=MilkMainCallback(action='loop').pack()
                ),
            ],
        ]
    buttons.append(
        [
            InlineKeyboardButton(
                text=f"Редактировать",
                callback_data=MilkMainCallback(action='edit').pack()
            ),
        ],
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def not_mercury_auth_data_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"Ввести данные",
                callback_data=EditMercuryAuthDataCallback(action="edit").pack()
            ),
        ],
    ])
