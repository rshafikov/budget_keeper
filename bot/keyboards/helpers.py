import logging

from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup)

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


def yes_or_no_kb(cb_yes: str = 'yes', cb_no: str = 'no'):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='yes', callback_data=cb_yes),
                InlineKeyboardButton(text='no', callback_data=cb_no)
            ]
        ]
    )


def cancel_kb(callback_data: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='отменить', callback_data=callback_data),
            ]
        ]
    )
