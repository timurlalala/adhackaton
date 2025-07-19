from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter
import aiohttp

from bot.states import CreateCharacter, OnBoarding, CharactersManagementMenu, chat, SelectPreDefinedCharacter
from bot.templates import archs_mapping, chars_mapping, ONBOARDING_SELECT_PREDEFINED
from bot.keyboards.create_character import get_choice_inline_keyboard
from app.schemas import CharacterCreationRequest, HelloMessageRequest, CharacterSelectionRequest, MessageResponse
from uuid import UUID
from config import FASTAPI_URL


router = Router()

@router.message(StateFilter(OnBoarding.waiting_onboarding_menu, CharactersManagementMenu.waiting_for_option, chat), F.text == "Готовый персонаж")
async def select_predefined_character(message: types.Message, state: FSMContext):
    await message.answer(ONBOARDING_SELECT_PREDEFINED, reply_markup=get_choice_inline_keyboard(
        step="predef", options=["Геральт из Ривии", "Умный мальчик в очках", "Кошко-девочка Юки", "Пикми герл"]
    ))
    await state.set_state(SelectPreDefinedCharacter.waiting_for_selection)

@router.callback_query(StateFilter(SelectPreDefinedCharacter.waiting_for_selection))
async def start_predefined_character(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_reply_markup(reply_markup=None)
    try:
        async with aiohttp.ClientSession() as session:

            async with session.post(
                f"{FASTAPI_URL}/api/v1/select_character",
                json=CharacterSelectionRequest(user_id=callback_query.from_user.id,
                                                character_id=chars_mapping[int(callback_query.data.split('_')[1])]).model_dump(mode='json')
            ) as response:
                if response.status != 200:
                    await callback_query.answer("Ошибка при выборе персонажа")
                    return

            async with session.post(
                f"{FASTAPI_URL}/api/v1/chat/hello_message",
                json=HelloMessageRequest(user_id=callback_query.from_user.id).model_dump(mode='json')
            ) as response:
                if response.status != 200:
                    await callback_query.answer("Ошибка при генерации сообщения")
                    return
                bot_answer = MessageResponse(**(await response.json())).message
            await callback_query.bot.answer_callback_query(callback_query.id, text="персонаж выбран!", show_alert=True)
            await callback_query.answer(bot_answer)
    except Exception as e:
        await callback_query.answer(f"Ошибка {e}")

    await state.set_state(chat)