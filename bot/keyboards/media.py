from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def provide_text_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("Использовать случайный текст", callback_data="random-text")],
            [InlineKeyboardButton("Вернуться назад", callback_data="cancel")]
        ]
    )
