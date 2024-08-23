import datetime
import logging
import os
from logging.handlers import TimedRotatingFileHandler

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from decouple import config
from redis import Redis

logging.basicConfig(
    level=config('DEBUG_LVL', 'DEBUG'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        TimedRotatingFileHandler(
            filename=f'{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log',
            when='midnight',
            interval=1,
            backupCount=1,
        ),
        logging.StreamHandler(),
    ],
)

if (env_url := config('REDIS_URL', None)) or (os.getenv('REDIS_URL', None)):
    redis_url = env_url or os.getenv('REDIS_URL', None)
    token_storage = Redis.from_url(f'{redis_url}/0')
    state_storage = RedisStorage.from_url(f'{redis_url}/1', {'decode_responses': True})
else:
    state_storage = MemoryStorage()
    token_storage = {}

bot = Bot(
    token=config('BOT_TOKEN'),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher(storage=state_storage, bot=bot, token_storage=token_storage)
