import asyncio
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender


class AuthMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: dict[str, Any]
    ) -> Any:
        async with ChatActionSender.typing(bot=event.bot, chat_id=event.chat.id):
            await asyncio.sleep(0.8)

            if (token := data['token_storage'].get(str(event.chat.id))) is None:
                token = await data['api_client'].get_token(event.chat.id)

                if token is None:
                    await data['api_client'].create_user(
                        telegram_id=event.chat.id,
                        name=event.chat.username,
                        lastname=event.chat.first_name,
                    )
                    token = await data['api_client'].get_token(event.chat.id)

                data['token_storage'].set(str(event.chat.id), token, ex=600_000)

            data['user_token'] = token
            return await handler(event, data)
