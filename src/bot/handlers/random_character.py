from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter
import aiohttp

from bot.states import CreateCharacter, OnBoarding, CharactersManagementMenu, chat
from bot.templates import archs_mapping, ONBOARDING_CREATION_HELLO
from bot.keyboards.create_character import get_choice_inline_keyboard
from app.schemas import CharacterCreationRequest, HelloMessageRequest, CharacterSelectionRequest, MessageResponse
from uuid import UUID
from config import FASTAPI_URL

router = Router()

@router.message(StateFilter(OnBoarding.waiting_onboarding_menu, CharactersManagementMenu.waiting_for_option, chat), F.text == "Рандомный персонаж")
async def start_random_character(message: types.Message, state: FSMContext):
    request = CharacterCreationRequest(user_id=message.from_user.id, params=None, personality=None, name=None)
    try:
        async with aiohttp.ClientSession() as session:

            async with session.post(
                    f"{FASTAPI_URL}/api/v1/create_character",
                    json=request.model_dump(mode='json')
            ) as response:
                if response.status != 201:
                    await message.answer("Ошибка при создании персонажа")
                    return
                char_id = await response.json()
                char_id = UUID(char_id['character_id'])
                # await message.answer(f"Ошибка при создании персонажа {char_id}")

            async with session.post(
                    f"{FASTAPI_URL}/api/v1/select_character",
                    json=CharacterSelectionRequest(user_id=message.from_user.id,
                                                   character_id=char_id).model_dump(mode='json')
            ) as response:
                if response.status != 200:
                    await message.answer("Ошибка при выборе персонажа")
                    return

            async with session.post(
                    f"{FASTAPI_URL}/api/v1/chat/hello_message",
                    json=HelloMessageRequest(user_id=message.from_user.id).model_dump(mode='json')
            ) as response:
                if response.status != 200:
                    await message.answer("Ошибка при генерации сообщения")
                    return
                bot_answer = MessageResponse(**(await response.json())).message
            await message.answer(bot_answer)
    except Exception as e:
        await message.answer(f"Ошибка {e}")

    await state.set_state(chat)
