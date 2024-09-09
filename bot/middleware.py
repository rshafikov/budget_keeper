import asyncio
from typing import Any, Awaitable, Callable

import redis
from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender

from bot.client import APIClient


class AuthMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: dict[str, Any]
    ) -> Any:
        async with ChatActionSender.typing(bot=event.bot, chat_id=event.chat.id):
            await asyncio.sleep(0.3)

            client: APIClient = data['api_client']
            token_storage: redis.Redis = data['token_storage']
            user_storage: dict = data['user_storage']

            if (token := token_storage.get(f'{event.chat.id}')) is None:
                token = await client.get_token(event.chat.id)

                if token is None:
                    await client.create_user(
                        telegram_id=event.chat.id,
                        name=event.chat.username,
                        lastname=event.chat.first_name,
                    )
                    token = await client.get_token(event.chat.id)

                token_storage.set(f'{event.chat.id}', token, ex=600_000)

            if (user := user_storage.get(event.from_user.id)) is None:
                user = await client.user_profile(token)
                user_storage.update({event.from_user.id: user})

            data['user_token'] = token
            data['user'] = user
            return await handler(event, data)
