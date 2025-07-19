from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter
import aiohttp

from bot.states import CreateCharacter, OnBoarding, CharactersManagementMenu, chat, SelectPreDefinedCharacter
from bot.templates import archs_mapping, chars_mapping, ONBOARDING_SELECT_PREDEFINED
from bot.keyboards.create_character import get_choice_inline_keyboard
from app.schemas import CharacterCreationRequest, HelloMessageRequest, CharacterSelectionRequest, MessageResponse, MessageRequest
from uuid import UUID
from config import FASTAPI_URL

router = Router()

# @router.message(F.text == "Мои персонажи")
# async def my_characters(message: types.Message, state: FSMContext):


@router.message(StateFilter(chat))
async def start_predefined_character(message: types.Message, state: FSMContext):
    try:
        async with aiohttp.ClientSession() as session:

            async with session.post(
                f"{FASTAPI_URL}/api/v1/chat/send_message",
                json=MessageRequest(user_id=message.from_user.id, message=message.text).model_dump(mode='json')
            ) as response:
                if response.status != 200:
                    await message.answer("Ошибка при генерации сообщения")
                    return
                bot_answer = MessageResponse(**(await response.json())).message
            await message.answer(bot_answer)
    except Exception as e:
        await message.answer(f"Ошибка {e}")

    await state.set_state(chat)