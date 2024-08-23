from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_kb(one_time: bool = False):
    kb = [
        [
            KeyboardButton(text='Записать расход')
        ],
        [
            KeyboardButton(text='Категории'),
            KeyboardButton(text='Отчеты'),
            KeyboardButton(text='Настройки')
        ],
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb, resize_keyboard=True, one_time_keyboard=one_time
    )
