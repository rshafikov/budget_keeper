from typing import Iterable

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def categories_main_kb(one_time: bool = False):
    kb = [
        [
            KeyboardButton(text='Новая категория'),
            KeyboardButton(text='Изменить категорию'),
            KeyboardButton(text='Удалить категорию')
        ],
        [
            KeyboardButton(text='Мои категории'),
            KeyboardButton(text='Меню')
        ],
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb, resize_keyboard=True, one_time_keyboard=one_time
    )


def user_categories_kb(categories: Iterable, one_time: bool = False):
    kb = []
    row = []
    for c in categories:
        row.append(KeyboardButton(text=c))
        if len(row) == 4:
            kb.append(row)
            row = []

    row.append(KeyboardButton(text='Категории'))
    kb.append(row)

    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=one_time)
