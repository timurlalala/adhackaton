from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_characters_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Геральт из Ривии")],
            [KeyboardButton(text="Умный мальчик в очках")],
            [KeyboardButton(text="Кошко-девочка Юки")],
            [KeyboardButton(text="Пикми герл")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
