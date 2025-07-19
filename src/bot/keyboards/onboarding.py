from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_onboarding_confirm():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Как это работает?")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_onboarding_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Свой персонаж")],
            [KeyboardButton(text="Готовый персонаж")],
            [KeyboardButton(text="Рандомный персонаж")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
