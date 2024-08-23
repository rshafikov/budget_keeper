import logging

from aiogram.types import CallbackQuery

from bot.main import bot

logger = logging.getLogger(__name__)


async def del_call_kb(call: CallbackQuery):
    try:
        await bot.edit_message_reply_markup(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            reply_markup=None
        )
    except Exception as e:
        logger.error('Unable to delete inline keyboard: %s', e)
