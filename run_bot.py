import asyncio

from aiohttp import ClientSession
from decouple import config

from bot.client import APIClient
from bot.main import bot, dp
from bot.handlers.start import start_router


async def main():
    api_url = config('API_URL')
    async with ClientSession(
            base_url=api_url[:-1] if api_url.endswith('/') else api_url,
    ) as api_sess:
        dp['api_client'] = APIClient(api_sess)
        dp.include_router(start_router)
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
