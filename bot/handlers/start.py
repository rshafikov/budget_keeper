from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from redis import Redis

from bot.client import APIClient
from bot.keyboards.bot_utils import del_call_kb
from bot.keyboards.inline.currency import choose_currency
from bot.keyboards.main_menu import main_kb
from bot.middleware import AuthMiddleware

start_router = Router()
start_router.message.middleware(AuthMiddleware())


class CurrencyState(StatesGroup):
    currency = State()


@start_router.message(Command(commands=('start', )))
async def handle_start(message: Message, state: FSMContext):
    await message.answer(
        'Привет! Пожалуйста, выбери валюту для записи своих расходов',
        reply_markup=choose_currency()
    )
    await state.set_state(CurrencyState.currency)


@start_router.callback_query(F.data, CurrencyState.currency)
async def handle_currency(
        call: CallbackQuery,
        state: FSMContext,
        api_client: APIClient,
        token_storage: Redis | dict,
):
    await state.clear()
    await del_call_kb(call)

    if (token := token_storage.get(str(call.from_user.id))) is None:
        await call.answer('Telegram API error. Пожалуйста, попробуйте еще раз.')
        return

    await call.answer('Уведомляем Павла Дурова...')
    user_upd = await api_client.update_user(token, currency=str(call.data))
    await call.message.answer(
        text=(
            f'Установлена базовая валюта: <b>{user_upd.currency.value!r}</b>.'
            f'\nВы всегда можете изменить валюту в настройках'
        ),
        reply_markup=main_kb()
    )
