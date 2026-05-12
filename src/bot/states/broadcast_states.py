from aiogram.fsm.state import State, StatesGroup


class BroadcastAll(StatesGroup):
    waiting_for_message = State()


class BroadcastClass(StatesGroup):
    waiting_for_class = State()
    waiting_for_message = State()
