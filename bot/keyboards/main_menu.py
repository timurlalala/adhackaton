from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🆕 Создать персонажа")],
            [
                KeyboardButton(text="📁 Мои персонажи"),
                KeyboardButton(text="🌍 Глобальный каталог"),
            ],
        ],
        resize_keyboard=True,
    )
