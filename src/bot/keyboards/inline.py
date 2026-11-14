from collections.abc import Sequence
from maxapi.types import Attachment, CallbackButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder


def _build_keyboard(
    buttons: dict[str, str],
    sizes: Sequence[int] = (1,),
) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    for text, callback_payload in buttons.items():
        builder.add(CallbackButton(text=text, payload=callback_payload))
    builder.adjust(*sizes)
    return builder


def create_inline_keyboard(
    buttons: dict[str, str],
    sizes: Sequence[int] = (1,),
) -> Attachment:
    return _build_keyboard(buttons, sizes).as_markup()


def create_cancel_inline_keyboard(
    buttons: dict[str, str],
    sizes: Sequence[int] = (1,),
) -> Attachment:
    builder = _build_keyboard(buttons, sizes)
    builder.row(CallbackButton(text="🚫 Отмена", payload="cancel"))
    return builder.as_markup()
