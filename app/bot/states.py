"""FSM-состояния диалогов бота."""

from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    """Регистрация нового клиента."""

    waiting_for_name = State()
    waiting_for_phone = State()


class Checkout(StatesGroup):
    """Оформление заявки."""

    waiting_for_comment = State()
    confirming = State()
