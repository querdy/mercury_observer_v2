from aiogram.filters.callback_data import CallbackData


class EditMercuryAuthDataCallback(CallbackData, prefix="smad"):
    action: str
