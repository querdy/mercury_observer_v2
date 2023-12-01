from aiogram.filters.callback_data import CallbackData


class EditMercuryAuthDataCallback(CallbackData, prefix="smad"):
    action: str


class MilkMainCallback(CallbackData, prefix="mm"):
    action: str


class MilkEditConfigCallback(CallbackData, prefix="mec"):
    action: str


class MilkEditEnterprisePatternsCallback(CallbackData, prefix="meep"):
    action: str
    value: str | None = None


class MilkEditScheduleEveryMinuteCallback(CallbackData, prefix="mesem"):
    action: str
    value: str


class MilkEditVerifiedProductsCallback(CallbackData, prefix="mevp"):
    action: str
    value: str | None = None


class MilkEditVerifiedTransactionTypeCallback(CallbackData, prefix="mevtt"):
    action: str
    value: str


class MilkEditVerifiedVetExaminationCallback(CallbackData, prefix="mevve"):
    action: str
    value: str
