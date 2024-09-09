from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from redis import Redis

from bot.client import APIClient
from bot.keyboards.categories import user_categories_kb
from bot.keyboards.helpers import cancel_kb, del_call_kb, yes_or_no_kb
from bot.keyboards.main_menu import main_kb
from bot.util import create_table, is_number

record_router = Router()


class CreateRecord(StatesGroup):
    category_name = State()
    amount = State()


@record_router.message(F.text.lower() == 'записать расход')
async def create_record_welcome(message: Message, state: FSMContext, user: dict):
    await message.answer(
        'Пожалуйста, выберите <b>категорию</b> для внесения расхода. ',
        reply_markup=user_categories_kb(user['categories'])
    )
    await state.set_state(CreateRecord.category_name)


@record_router.message(F.text, CreateRecord.category_name)
async def create_record_get_category(
        message: Message,
        state: FSMContext,
        user: dict
):
    if message.text not in user['categories']:
        await message.answer(
            f'Извините, категория <b>{message.text}</b> не найдена. '
            f'Проверьте название и повторите попытку.',
            reply_markup=user_categories_kb(user['categories'])
        )
        await state.clear()
        return

    new_record_table = create_table(
        rows=[(message.text, '...')],
        field_names=('Категория', f'Сумма, {user["currency"]}'),
        align='c'
    )
    await state.update_data(category_name=message.text)
    await message.answer(
        f'Пожалуйста, введите <b>сумму</b> расхода:\n<pre>{new_record_table}</pre>',
        reply_markup=cancel_kb('record.create.cancel')
    )
    await state.set_state(CreateRecord.amount)


@record_router.message(F.text, CreateRecord.amount)
async def create_record_get_amount(
        message: Message,
        state: FSMContext,
        user: dict
):
    if not is_number(message.text):
        await message.answer(
            f'Пожалуйста, введите корректное значение вашего расхода: <b>{message.text}</b>.',
            reply_markup=cancel_kb('record.create.cancel')
        )
        return

    await state.update_data(amount=message.text)
    data = await state.get_data()
    category = data.get('category_name')

    new_record_table = create_table(
        rows=[(category, message.text)],
        field_names=('Категория', f'Сумма, {user["currency"]}'),
        align='c'
    )
    await message.answer(
        f'Пожалуйста, <b>подтвердите</b> создание:\n<pre>{new_record_table}</pre>',
        reply_markup=yes_or_no_kb('record.create.yes', 'record.create.no')
    )


@record_router.callback_query(F.data.startswith('record.create'), CreateRecord.amount)
async def create_record_callback(
        call: CallbackQuery,
        state: FSMContext,
        api_client: APIClient,
        token_storage: Redis
):
    await del_call_kb(call)
    data = await state.get_data()
    category_name, amount = data.get('category_name'), data.get('amount')
    await state.clear()

    if call.data in ('record.create.no', 'record.create.cancel'):
        await call.message.answer(
            'Создание расхода отменено.',
            reply_markup=main_kb()
        )
        return

    if (token := token_storage.get(str(call.from_user.id))) is None:
        await call.answer(
            'Ваша предыдущая сессия истекла. Пожалуйста, попробуйте еще раз.',
            reply_markup=main_kb()
        )
        return

    new_record = await api_client.create_record(token, amount=amount, category_name=category_name)

    if new_record is not None:
        await call.message.answer('Запись успешно создана: ☑️', reply_markup=main_kb())
        return

    await call.message.answer(
        'Произошла ошибка во время создания расхода. Пожалуйста, попробуйте еще раз.',
        reply_markup=main_kb()
    )
