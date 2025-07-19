from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from bot.keyboards.onboarding import get_onboarding_confirm, get_onboarding_menu
from bot.templates import ONBOARDING_HELLO_TEMPLATE, ONBOARDING_MENU
from bot.states import OnBoarding
import aiohttp
from config import FASTAPI_URL
from app.schemas import CharacterAddRequest
from bot.templates import chars_mapping

router = Router()

@router.message(Command("start"))
async def start_cmd(message: types.Message, state: FSMContext):
    await message.answer(ONBOARDING_HELLO_TEMPLATE.format(
        name=message.from_user.first_name),
        reply_markup=get_onboarding_confirm())
    await state.set_state(OnBoarding.waiting_for_start)
    try:
        async with aiohttp.ClientSession() as session:
            for i in chars_mapping:
                async with session.post(
                    f"{FASTAPI_URL}/api/v1/add_character",
                    json=CharacterAddRequest(user_id=message.from_user.id,
                                                character_id=i).model_dump(mode='json')
                ) as response:
                    if response.status != 200:
                        await message.answer("Ошибка при выборе персонажа")
                        return
    except Exception as e:
        await message.answer(f"Ошибка {e}")


@router.message(F.text == "Как это работает?", StateFilter(OnBoarding.waiting_for_start))
async def start_cmd(message: types.Message, state: FSMContext):
    await message.answer(ONBOARDING_MENU,
                         reply_markup=get_onboarding_menu())
    await state.set_state(OnBoarding.waiting_onboarding_menu)