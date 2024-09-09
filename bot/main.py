import logging
import os
from logging.handlers import TimedRotatingFileHandler

import redis
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters.exception import ExceptionTypeFilter
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import ErrorEvent, Message
from aiohttp.client_exceptions import ClientError
from decouple import config

logging.basicConfig(
    level=config('DEBUG_LVL', 'DEBUG'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        TimedRotatingFileHandler(
            # filename=f'{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log',
            filename='bot.log',
            when='midnight',
            interval=1,
            backupCount=1,
        ),
        logging.StreamHandler(),
    ],
)

if (env_url := config('REDIS_URL', None)) or (os.getenv('REDIS_URL', None)):
    redis_url = env_url or os.getenv('REDIS_URL', None)
    token_storage = redis.Redis.from_url(f'{redis_url}/0')
    state_storage = RedisStorage.from_url(f'{redis_url}/1', {'decode_responses': True})
else:
    raise AssertionError('Пожалуйста, укажите корректный путь до Redis')

try:
    token_storage.ping()
except redis.exceptions.ConnectionError:
    raise AssertionError('Убедитесь, что Redis запущен.')

bot = Bot(
    token=config('BOT_TOKEN'),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher(storage=state_storage, bot=bot, token_storage=token_storage, user_storage={})


@dp.error(ExceptionTypeFilter(ClientError), F.update.message.as_("message"))
async def handle_client_error(event: ErrorEvent, message: Message):
    await message.answer(
        'Проблемы с API, пожалуйста попробуйте позже или обратитесь к администратору.'
    )
