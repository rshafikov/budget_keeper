import asyncio

from aiohttp import ClientSession
from decouple import config

from bot.client import APIClient
from bot.handlers.categories import category_router
from bot.handlers.records import record_router
from bot.handlers.tear_down import tear_down_router
from bot.main import bot, dp
from bot.handlers.start import start_router
from bot.middleware import AuthMiddleware


async def main():
    url = config('API_URL')

    async with ClientSession(base_url=url[:-1] if url.endswith('/') else url) as api_sess:
        dp['api_client'] = APIClient(api_sess)
        dp.message.middleware(AuthMiddleware())
        dp.include_router(start_router)
        dp.include_router(category_router)
        dp.include_router(record_router)
        dp.include_router(tear_down_router)

        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
