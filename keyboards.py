from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import KeyboardButton
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

topics = {"devops", "backend", "frontend"}

main = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Написать пост")]], resize_keyboard=True
)

contest_exit = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Отмена")]], resize_keyboard=True
)


like_dislike = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="👍", callback_data="like")],
        [InlineKeyboardButton(text="👎", callback_data="dislike")],
    ]
)


async def reply_topics():
    keyboard = ReplyKeyboardBuilder()
    for topic in topics:
        keyboard.add(KeyboardButton(text=topic))
    keyboard.add(KeyboardButton(text="Отмена"))
    return keyboard.adjust(3).as_markup(resize_keyboard=True)
