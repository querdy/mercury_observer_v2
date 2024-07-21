from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from app.tg.user_service.callback import EditMercuryAuthDataCallback


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


def not_mercury_auth_data_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"Ввести данные",
                callback_data=EditMercuryAuthDataCallback(action="edit").pack()
            ),
        ],
    ])
