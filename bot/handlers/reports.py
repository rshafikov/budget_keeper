from datetime import datetime, timedelta

from aiogram import F, Router
from aiogram.types import Message

from bot.client import APIClient
from bot.keyboards.reports import report_kb
from bot.util import create_report_table

report_router = Router()


@report_router.message(F.text.lower() == 'отчеты')
async def create_report_welcome(message: Message):
    await message.answer('Пожалуйста, выберите период отчета:', reply_markup=report_kb())


@report_router.message(F.text.lower() == 'отчет за день')
async def create_daily_report(
        message: Message,
        api_client: APIClient,
        user_token: str,
        user: dict
):
    today = datetime.now()
    raw_records = await api_client.get_records(
        user_token, from_date=today.strftime('%Y-%m-%d'), )
    table = create_report_table(records=raw_records, main_currency=user['currency'])
    await message.answer(
        f'{message.text}: <b>{today.strftime('%d-%m-%Y')}</b>\n<pre>'f'{table}</pre>',
        reply_markup=report_kb()
    )


@report_router.message(F.text.lower() == 'отчет за неделю')
async def create_weekly_report(
        message: Message,
        api_client: APIClient,
        user_token: str,
        user: dict
):
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    raw_records = await api_client.get_records(
        user_token, from_date=week_start.strftime('%Y-%m-%d')
    )
    table = create_report_table(records=raw_records, main_currency=user['currency'])
    await message.answer(
        f'{message.text}: <b>c {week_start.strftime('%d-%m-%Y')}</b>\n<pre>'f'{table}</pre>',
        reply_markup=report_kb()
    )


@report_router.message(F.text.lower() == 'отчет за месяц')
async def create_monthly_report(
        message: Message,
        api_client: APIClient,
        user_token: str,
        user: dict
):
    today = datetime.now()
    month_start = today.replace(day=1)
    raw_records = await api_client.get_records(
        user_token, from_date=month_start.strftime('%Y-%m-%d')
    )
    table = create_report_table(records=raw_records, main_currency=user['currency'])
    await message.answer(
        f'{message.text}: <b>c {month_start.strftime('%d-%m-%Y')}</b>\n<pre>'f'{table}</pre>',
        reply_markup=report_kb()
    )


@report_router.message(F.text.lower() == 'отчет за период')
async def create_custom_report_welcome(message: Message):
    await message.answer(
        'Пожалуйста, напишите границы отчета в формате:\n<b>год-месяц-день:год-месяц-день</b>\n'
        'Например: 2024-01-01:2024-02-02\nВам будет возврщен отчет за указанный период.',
        reply_markup=report_kb()
    )
