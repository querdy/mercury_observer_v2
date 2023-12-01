from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from app.schemas.milk_service import ScheduleEveryMinute, TransactionType
from app.tg.milk_service.callback import EditMercuryAuthDataCallback, MilkMainCallback, MilkEditConfigCallback, \
    MilkEditEnterprisePatternsCallback, MilkEditScheduleEveryMinuteCallback, MilkEditVerifiedProductsCallback, \
    MilkEditVerifiedTransactionTypeCallback


class ReplyKeyboard:
    @staticmethod
    def main():
        return ReplyKeyboardMarkup(
            one_time_keyboard=False,
            resize_keyboard=True,
            keyboard=[
                [
                    KeyboardButton(text="/milk")
                ],
            ],
        )
