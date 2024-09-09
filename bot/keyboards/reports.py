from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def report_kb(one_time: bool = False):
    kb = [
        [
            KeyboardButton(text='Отчет за день'),
            KeyboardButton(text='Отчет за неделю'),
            KeyboardButton(text='Отчет за месяц')
        ],
        [
            KeyboardButton(text='Отчет за период'),
            KeyboardButton(text='Меню')
        ],
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb, resize_keyboard=True, one_time_keyboard=one_time
    )
