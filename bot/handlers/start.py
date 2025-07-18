from aiogram import Router, types, F
from keyboards.main_menu import get_main_menu

router = Router()


@router.message(F.text == "/start")
async def start_cmd(message: types.Message):
    await message.answer("Привет! Я бот с персонажами", reply_markup=get_main_menu())
