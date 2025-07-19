from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_choice_inline_keyboard(step: str, options: list[str]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=opt, callback_data=f"{step}_{i}")]
            for i, opt in enumerate(options)
        ]
    )

def get_one_button():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Создать персонажа")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )