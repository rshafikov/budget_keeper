from aiogram import Router
from aiogram.types import CallbackQuery

from bot.keyboards.helpers import del_call_kb

tear_down_router = Router()


@tear_down_router.callback_query()
async def clean_wrong_callback(call: CallbackQuery):
    await call.answer('Удаляем неактуальное событие...')
    await del_call_kb(call)
    await call.message.delete()
