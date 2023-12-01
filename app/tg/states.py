from aiogram.fsm.state import State, StatesGroup


class MercuryAuthDataState(StatesGroup):
    last_msg = State()
    login = State()
    password = State()


class EditEnterprisePatternsState(StatesGroup):
    get_value = State()


class EditVerifiedProductsState(StatesGroup):
    get_value = State()


class EditIntervalState(StatesGroup):
    get_interval = State()
