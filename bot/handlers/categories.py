from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from redis import Redis

from bot.client import APIClient
from bot.keyboards.categories import categories_main_kb, user_categories_kb
from bot.keyboards.helpers import cancel_kb, del_call_kb, yes_or_no_kb

category_router = Router()


class NewCategoryState(StatesGroup):
    name = State()


class DeleteCategoryState(StatesGroup):
    name = State()


class ChangeCategory(StatesGroup):
    old_name = State()
    new_name = State()


@category_router.message(F.text.lower() == 'категории')
async def categories_main_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        'Пожалуйста, выберите действие:',
        reply_markup=categories_main_kb()
    )


@category_router.message(Command(commands=('categories', )))
@category_router.message(F.text.lower() == 'мои категории')
async def get_user_categories(message: Message, user_categories: list):
    await message.answer(
        'Ваши текущие категории:',
        reply_markup=user_categories_kb(user_categories, one_time=True)
    )


@category_router.message(F.text.lower() == 'новая категория')
async def create_category_welcome(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Пожалуйста, напишите название вашей <b>новой</b> категории.')
    await state.set_state(NewCategoryState.name)


@category_router.message(F.text.lower() == 'изменить категорию')
async def change_category_welcome(message: Message, state: FSMContext, user_categories: list):
    await state.clear()
    await message.answer(
        'Пожалуйста, выберите категорию, которую хотите <b>изменить</b>. ',
        reply_markup=user_categories_kb(user_categories, one_time=True)
     )
    await state.set_state(ChangeCategory.old_name)


@category_router.message(F.text.lower() == 'удалить категорию')
async def delete_category_welcome(message: Message, state: FSMContext, user_categories: list):
    await state.clear()
    await message.answer(
        'Пожалуйста, выберите категорию для <b>удаления</b>.',
        reply_markup=user_categories_kb(user_categories, one_time=True)
    )
    await state.set_state(DeleteCategoryState.name)


@category_router.message(F.text, NewCategoryState.name)
async def create_category_get_name(message: Message, state: FSMContext, user_categories: list):
    if message.text in user_categories:
        await message.reply(
            'Извините, данная категория уже существует.',
            reply_markup=categories_main_kb()
        )
        await state.clear()
        return

    await state.update_data(name=message.text)
    await message.reply(
        f'Пожалуйста, подтвердите создание категории, нажмите <b>"yes"</b> или <b>"no"</b>:\n\n'
        f'Новая категория: <b>{message.text}</b>\n\n'
        f'Если же вы хотите другое имя, пожалуйста, напишите его.',
        reply_markup=yes_or_no_kb(f'category.create.{message.text}', 'category.create.no')
    )


@category_router.message(F.text, ChangeCategory.old_name)
async def change_category_get_old_name(message: Message, state: FSMContext, user_categories: list):
    if message.text not in user_categories:
        await message.reply(
            f'Извините, категория <b>{message.text}</b> не найдена. '
            f'Проверьте название и повторите попытку.',
            reply_markup=user_categories_kb(user_categories, one_time=True)
        )
        return

    await message.reply(
        f'Пожалуйста, введите <b>новое</b> имя для выбранной категории:\n\n<b>{message.text}</b>',
        reply_markup=cancel_kb('category.change.cancel')
    )
    await state.set_state(ChangeCategory.new_name)


@category_router.message(F.text, ChangeCategory.new_name)
async def change_category_get_new_name(message: Message, state: FSMContext):
    data = await state.get_data()
    old_name = data.get('old_name')

    await state.update_data(new_name=message.text)
    await message.reply(
        f'Пожалуйста, подтвердите изменение категории, нажмите <b>"yes"</b> или <b>"no"</b>:\n\n'
        f'<b>{old_name}</b> --> <b>{message.text}</b>\n\n'
        f'Если же вы хотите другое имя, пожалуйста, напишите его.',
        reply_markup=yes_or_no_kb('category.change.yes', 'category.change.no')
    )


@category_router.message(F.text, DeleteCategoryState.name)
async def delete_category_get_name(message: Message, state: FSMContext, user_categories: list):
    if message.text not in user_categories:
        await message.reply(
            f'Извините, категория <b>{message.text}</b> не найдена. '
            f'Проверьте название и повторите попытку.',
            reply_markup=user_categories_kb(user_categories, one_time=True)
        )
        await state.clear()
        return

    await state.update_data(name=message.text)
    await message.reply(
        f'Пожалуйста, подтвердите удаление категории нажмите <b>"yes"</b> или <b>"no"</b>:\n\n'
        f'Категория для удаления: <b>{message.text}</b>',
        reply_markup=yes_or_no_kb('category.delete.yes', 'category.delete.no')
    )


@category_router.callback_query(F.data.startswith('category.create'), NewCategoryState.name)
async def create_category_callback(
        call: CallbackQuery,
        state: FSMContext,
        api_client: APIClient,
        token_storage: Redis,
        category_storage: dict
):
    await del_call_kb(call)
    await state.clear()

    if call.data == 'category.create.no':
        await call.message.reply('Создание категории отменено.')
        return

    if (token := token_storage.get(str(call.from_user.id))) is None:
        await call.answer('Ваша предыдущая сессия истекла. Пожалуйста, попробуйте еще раз.')
        return

    new_category = await api_client.create_category(token, call.data.split('.')[-1])

    if new_category is not None:
        await call.message.reply(
            f'Категория <b>{new_category.name}</b> успешно создана.\n',
            reply_markup=categories_main_kb(one_time=True)
        )
        user_categories = await api_client.get_categories(token)
        category_storage[call.from_user.id] = user_categories
        return

    await call.message.reply('Произошла ошибка во время создания категории. '
                             'Пожалуйста, попробуйте еще раз.')


@category_router.callback_query(F.data.startswith('category.change'), ChangeCategory.new_name)
async def change_category_callback(
        call: CallbackQuery,
        state: FSMContext,
        api_client: APIClient,
        token_storage: Redis,
        category_storage: dict
):
    await del_call_kb(call)
    data = await state.get_data()
    old_name, new_name = data.get('old_name'), data.get('new_name')
    await state.clear()

    if call.data in ('category.change.no', 'category.change.cancel'):
        await call.message.reply(
            'Изменение категории отменено.',
            reply_markup=categories_main_kb()
        )
        return

    if (token := token_storage.get(str(call.from_user.id))) is None:
        await call.answer(
            'Ваша предыдущая сессия истекла. Пожалуйста, попробуйте еще раз.',
            reply_markup=categories_main_kb()
        )
        return

    updated_category = await api_client.update_category(token, old_name, name=new_name)

    if updated_category:
        await call.message.reply(
            f'Категория <b>{new_name}</b> успешно изменена.\n',
            reply_markup=categories_main_kb(one_time=True)
        )
        user_categories = await api_client.get_categories(token)
        category_storage[call.from_user.id] = user_categories
        return

    await call.message.reply(
        'Произошла ошибка во время изменения категории. Пожалуйста, попробуйте еще раз.',
        reply_markup=categories_main_kb()
    )


@category_router.callback_query(F.data.startswith('category.delete'), DeleteCategoryState.name)
async def delete_category_callback(
        call: CallbackQuery,
        state: FSMContext,
        api_client: APIClient,
        token_storage: Redis,
        category_storage: dict
):
    await del_call_kb(call)
    data = await state.get_data()
    category_name = data.get('name')
    await state.clear()

    if call.data == 'category.delete.no':
        await call.message.reply(
            'Удаление категории отменено.',
            reply_markup=categories_main_kb()
        )
        return

    if (token := token_storage.get(str(call.from_user.id))) is None:
        await call.answer(
            'Ваша предыдущая сессия истекла. Пожалуйста, попробуйте еще раз.',
            reply_markup=categories_main_kb()
        )
        return

    is_category_deleted = await api_client.delete_category(token, category_name)

    if is_category_deleted:
        await call.message.reply(
            f'Категория <b>{category_name}</b> успешно удалена.\n',
            reply_markup=categories_main_kb()
        )
        user_categories = await api_client.get_categories(token)
        category_storage[call.from_user.id] = user_categories
        return

    await call.message.reply(
        'Произошла ошибка во время удаления категории. Пожалуйста, попробуйте еще раз.',
        reply_markup=categories_main_kb()
    )
