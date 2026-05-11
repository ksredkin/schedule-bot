from aiogram.fsm.state import State, StatesGroup


class ReviewCreate(StatesGroup):
    waiting_for_review = State()


class ReviewReply(StatesGroup):
    waiting_for_reply_text = State()
