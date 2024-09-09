from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from redis import Redis

from bot.client import APIClient
from bot.keyboards.helpers import del_call_kb
from bot.keyboards.inline.currency import choose_currency
from bot.keyboards.main_menu import main_kb

start_router = Router()


class CurrencyState(StatesGroup):
    currency = State()


@start_router.message(F.text.lower() == 'меню')
async def main_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Выберите действие:', reply_markup=main_kb(one_time=True))


@start_router.message(Command(commands=('start', )))
async def handle_start(message: Message, state: FSMContext):
    await message.answer(
        'Привет! Пожалуйста, выбери валюту для записи своих расходов',
        reply_markup=choose_currency()
    )
    await state.set_state(CurrencyState.currency)


@start_router.callback_query(CurrencyState.currency)
async def handle_currency(
        call: CallbackQuery,
        state: FSMContext,
        api_client: APIClient,
        token_storage: Redis | dict,
        user_storage: dict
):
    await state.clear()
    await del_call_kb(call)

    if (token := token_storage.get(str(call.from_user.id))) is None:
        await call.answer('Ваша предыдущая сессия истекла. Пожалуйста, попробуйте еще раз.')
        return

    await call.answer('Уведомляем Павла Дурова...')
    user_upd = await api_client.update_user(token, currency=str(call.data))
    await call.message.answer(
        text=(
            f'Установлена базовая валюта: <b>{user_upd['currency']!r}</b>.'
            f'\nВы всегда можете изменить валюту в настройках'
        ),
        reply_markup=main_kb()
    )
    user_storage[call.from_user.id] = user_upd
