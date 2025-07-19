from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Создать персонажа")],
            [KeyboardButton(text="Готовый персонаж")],
            [KeyboardButton(text="Мои персонажи")],
            [KeyboardButton(text="Рандомный персонаж")]
        ],
        resize_keyboard=True)