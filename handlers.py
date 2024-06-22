import asyncio

from aiogram import Bot
from aiogram import Router
from aiogram.filters import IS_MEMBER
from aiogram.filters import IS_NOT_MEMBER
from aiogram.filters import ChatMemberUpdatedFilter
from aiogram.types import CallbackQuery
from aiogram.types import ChatMemberUpdated
from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup

from config import settings

router = Router()

scheduled_users = set()


@router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def is_bot(chat_member_update: ChatMemberUpdated, bot: Bot) -> None:
    member = chat_member_update.new_chat_member.user
    chat_id = chat_member_update.chat.id
    member_id = member.id

    if member and not member.is_bot:
        if member_id not in scheduled_users:
            scheduled_users.add(member_id)
            kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="I'm not a bot", callback_data=f"not_a_bot,{member_id}"
                        )
                    ]
                ]
            )
            message = await bot.send_message(
                chat_id,
                """Welcome to our group. Please click the "I'm not a bot" button to avoid getting kicked.""",
                reply_markup=kb,
            )
            await asyncio.create_task(
                kick_user(
                    bot, chat_id, member_id, message.message_id, settings.KICK_TIMEOUT
                )
            )


async def kick_user(
    bot: Bot, chat_id: int, user_id: int, message_id: int, timeout: int
) -> None:
    await asyncio.sleep(timeout)
    if user_id in scheduled_users:
        await bot.delete_message(chat_id, message_id)
        await bot.ban_chat_member(chat_id, user_id)
        await bot.unban_chat_member(chat_id, user_id)
        scheduled_users.discard(user_id)


@router.callback_query(lambda c: c.data and c.data.startswith("not_a_bot"))
async def process_callback_not_a_bot(callback_query: CallbackQuery, bot: Bot) -> None:
    user_id = int(callback_query.data.split(",")[1])
    if callback_query.from_user.id == user_id:
        chat_id = callback_query.message.chat.id
        message_id = callback_query.message.message_id
        if user_id in scheduled_users:
            scheduled_users.discard(user_id)
            await bot.delete_message(chat_id, message_id)
