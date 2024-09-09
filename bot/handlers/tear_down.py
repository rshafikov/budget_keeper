import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.handlers.records import CreateRecord
from bot.keyboards.helpers import cancel_kb, del_call_kb
from bot.keyboards.main_menu import main_kb

logger = logging.getLogger(__name__)

tear_down_router = Router()


@tear_down_router.message(F.text)
async def handle_category_or_unknown(message: Message, state: FSMContext, user: dict):
    if message.text in user['categories']:
        await state.update_data(category_name=message.text)
        await message.answer(
            f'Пожалуйста, введите <b>сумму</b> расхода:\n\n'
            f'Выбранная категория: <b>{message.text}</b>',
            reply_markup=cancel_kb('record.create.cancel')
        )
        await state.set_state(CreateRecord.amount)
        return

    await message.answer(
        'Я вас не понимаю, пожалуйста, выберите действие:',
        reply_markup=main_kb()
    )


@tear_down_router.callback_query()
async def clean_wrong_callback(call: CallbackQuery):
    try:
        await call.answer('Удаляем неактуальное событие...')
        await del_call_kb(call)
        await call.message.delete()
    except TelegramBadRequest as e:
        logger.warning('Ошибка при удалении: %s', e)
