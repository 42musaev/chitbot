import asyncio

from aiogram import Bot
from aiogram import F
from aiogram import Router
from aiogram.filters import IS_MEMBER
from aiogram.filters import IS_NOT_MEMBER
from aiogram.filters import ChatMemberUpdatedFilter
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.fsm.state import StatesGroup
from aiogram.types import CallbackQuery
from aiogram.types import ChatMemberUpdated
from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import Message
from aiogram.types import ReplyKeyboardRemove

import keyboards as kb
from config import settings

router = Router()

scheduled_users = set()

chats = settings.CHATS
topics = settings.TOPICS

likes_dislikes = {}


class NewPost(StatesGroup):
    text = State()
    topic = State()


@router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def handle_new_member(chat_member_update: ChatMemberUpdated, bot: Bot) -> None:
    member = chat_member_update.new_chat_member.user
    chat_id = chat_member_update.chat.id
    member_id = member.id

    if member and not member.is_bot:
        if member_id not in scheduled_users:
            scheduled_users.add(member_id)
            keyboard = InlineKeyboardMarkup(
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
                reply_markup=keyboard,
            )
            await asyncio.create_task(
                schedule_user_kick(
                    bot, chat_id, member_id, message.message_id, settings.KICK_TIMEOUT
                )
            )


async def schedule_user_kick(
    bot: Bot, chat_id: int, user_id: int, message_id: int, timeout: int
) -> None:
    await asyncio.sleep(timeout)
    if user_id in scheduled_users:
        await bot.delete_message(chat_id, message_id)
        await bot.ban_chat_member(chat_id, user_id)
        await bot.unban_chat_member(chat_id, user_id)
        scheduled_users.discard(user_id)


@router.callback_query(lambda c: c.data and c.data.startswith("not_a_bot"))
async def process_not_a_bot_callback(callback_query: CallbackQuery, bot: Bot) -> None:
    user_id = int(callback_query.data.split(",")[1])
    if callback_query.from_user.id == user_id:
        chat_id = callback_query.message.chat.id
        message_id = callback_query.message.message_id
        if user_id in scheduled_users:
            scheduled_users.discard(user_id)
            await bot.delete_message(chat_id, message_id)


@router.message(CommandStart())
async def handle_start_command(message: Message):
    await message.answer(
        f"{message.from_user.first_name}, чем я могу тебе помочь?", reply_markup=kb.main
    )


@router.message(F.text == "Написать пост")
async def initiate_post_creation(message: Message, state: FSMContext) -> None:
    await state.set_state(NewPost.text)
    await message.answer("Напишите содержание поста.", reply_markup=kb.contest_exit)


@router.message(NewPost.text)
async def receive_post_content(message: Message, state: FSMContext) -> None:
    if message.text == "Отмена":
        await message.answer("Действие отменено!", reply_markup=ReplyKeyboardRemove())
        await state.clear()
        await handle_start_command(message)
    else:
        if message.photo or message.text:
            if message.photo:
                await state.update_data(photo=message.photo, caption=message.caption)
            elif message.text:
                await state.update_data(text=message.text)

            await state.set_state(NewPost.topic)
            await message.answer(
                "Выберите топик, куда хотите закинуть пост.",
                reply_markup=await kb.reply_topics(),
            )
        else:
            await message.answer("Неверный формат. Только текст или фото.")


@router.message(NewPost.topic)
async def receive_post_topic(message: Message, state: FSMContext, bot: Bot) -> None:
    if message.text == "Отмена":
        await message.answer("Действие отменено!", reply_markup=ReplyKeyboardRemove())
        await state.clear()
        await handle_start_command(message)
    else:
        if message.text in topics:
            await state.update_data(topic=message.text)
            data = await state.get_data()
            send_post = None
            if "photo" in data:
                send_post = await bot.send_photo(
                    chat_id=chats["chitcom"],
                    photo=data["photo"][-1].file_id,
                    caption=data["caption"],
                    message_thread_id=topics["ceo"],
                    reply_markup=kb.like_dislike,
                )
            elif "text" in data:
                send_post = await bot.send_message(
                    chat_id=chats["chitcom"],
                    text=data["text"],
                    message_thread_id=topics["ceo"],
                    reply_markup=kb.like_dislike,
                )

            sp_message_id = send_post.message_id
            likes_dislikes[send_post.message_id] = [0, 0]
            await message.answer(
                "Пост принят и отправлен на проверку!",
                reply_markup=ReplyKeyboardRemove(),
            )
            await asyncio.sleep(10)
            await bot.send_message(
                chat_id=chats["chitcom"],
                text="Время голосования за пост вышло",
                message_thread_id=topics["ceo"],
            )
            if (
                likes_dislikes[send_post.message_id][0]
                >= likes_dislikes[send_post.message_id][1]
            ):
                await message.answer(
                    f"Ваш пост одобрен и в скором времени окажется в топике {message.text}"
                )
                if "photo" in data:
                    await bot.send_photo(
                        chat_id=chats["chitcom"],
                        photo=data["photo"][-1].file_id,
                        caption=data["caption"],
                        message_thread_id=topics[message.text],
                    )
                elif "text" in data:
                    await bot.send_message(
                        chat_id=chats["chitcom"],
                        text=data["text"],
                        message_thread_id=topics[message.text],
                    )
            else:
                await message.answer("К сожалению, ваш пост не одобрили")

            del likes_dislikes[sp_message_id]
            await state.clear()
            await handle_start_command(message)
        else:
            await message.answer("Нет такого топика. Выбери из того, что я предлагаю.")


@router.callback_query(lambda c: c.data in ["like", "dislike"])
async def handle_like_dislike(callback_query: CallbackQuery, bot: Bot) -> None:
    action = callback_query.data
    if action == "like":
        likes_dislikes[callback_query.message.message_id][0] += 1
    else:
        likes_dislikes[callback_query.message.message_id][1] += 1
    await bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=None,
    )
    await callback_query.answer()
