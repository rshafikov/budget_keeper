from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def choose_currency():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="RUB", callback_data='RUB'),
                InlineKeyboardButton(text="EUR", callback_data='EUR'),
                InlineKeyboardButton(text="USD", callback_data='USD'),
            ]
        ]
    )
