from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter
import aiohttp

from bot.states import CreateCharacter, OnBoarding, CharactersManagementMenu, chat
from bot.templates import archs_mapping, ONBOARDING_CREATION_HELLO
from bot.keyboards.create_character import get_choice_inline_keyboard, get_one_button
from app.schemas import CharacterCreationRequest, HelloMessageRequest, CharacterSelectionRequest, MessageResponse
from uuid import UUID
from config import FASTAPI_URL


router = Router()

# --- Начало создания ---
@router.message(F.text == "Свой персонаж", StateFilter(OnBoarding.waiting_onboarding_menu))
async def start_create_character(message: types.Message, state: FSMContext):
    await message.answer(ONBOARDING_CREATION_HELLO, reply_markup=get_one_button())
    await state.set_state(CharactersManagementMenu.waiting_for_option)


@router.message(StateFilter(CharactersManagementMenu.waiting_for_option,  chat), F.text == "Создать персонажа")
async def start_create_character(message: types.Message, state: FSMContext):
    # сохраняем user_id один раз
    await state.update_data(user_id=message.from_user.id)
    await message.answer("Как зовут вашего персонажа?")
    await state.set_state(CreateCharacter.waiting_for_name)


@router.message(StateFilter(CreateCharacter.waiting_for_name))
async def register_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("На кого похож этот персонаж по своей сути?",
                         reply_markup=get_choice_inline_keyboard('arch', options=[
                             'Наставник',
                             'Понимающий',
                             'Мотиватор',
                             'Клоун',
                             'Провокатор',
                             'Романтик',
                             'Исследователь',
                             'Монипулятор',
                         ]))
    await state.set_state(CreateCharacter.waiting_for_archetype)

@router.callback_query(StateFilter(CreateCharacter.waiting_for_archetype))
async def register_arch(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(
        personality="Вопрос: На кого похож этот персонаж по своей сути?\nОтвет: "
                    + archs_mapping[int(callback_query.data.split('_')[1])]
    )
    await callback_query.message.edit_reply_markup(reply_markup=None)
    await callback_query.bot.answer_callback_query(callback_query.id, text=f"Вы выбрали вариант {archs_mapping[int(callback_query.data.split('_')[1])]}", show_alert=False)
    await callback_query.answer(f"Опишите характер персонажа и манеру общения.")
    await state.set_state(CreateCharacter.waiting_for_personality)

@router.message(StateFilter(CreateCharacter.waiting_for_personality))
async def register_personality(message: types.Message, state: FSMContext):
    await state.update_data(
        personality="\nВопрос: Опишите характер персонажа и манеру общения.\nОтвет: "
                    + message.text
    )
    await message.answer("Какие у вашего персонажа особые привычки или увлечения?")
    await state.set_state(CreateCharacter.waiting_for_hobbies)

@router.message(StateFilter(CreateCharacter.waiting_for_hobbies))
async def register_hobbies(message: types.Message, state: FSMContext):
    await state.update_data(
        personality="\nВопрос: Какие у вашего персонажа особые привычки или увлечения?\nОтвет: "
                    + message.text
    )
    await message.answer("Как персонаж реагирует на комплименты и критику?")
    await state.set_state(CreateCharacter.waiting_for_critique_tolerance)

@router.message(StateFilter(CreateCharacter.waiting_for_critique_tolerance))
async def register_critique_tolerance(message: types.Message, state: FSMContext):
    await state.update_data(
        personality="\nВопрос: Как персонаж реагирует на комплименты и критику?\nОтвет: "
                    + message.text
    )
    await message.answer("О чем ваш персонаж никогда не будет говорить?")
    await state.set_state(CreateCharacter.waiting_for_taboo)

@router.message(StateFilter(CreateCharacter.waiting_for_taboo))
async def register_taboo(message: types.Message, state: FSMContext):
    await state.update_data(
        personality="\nВопрос: О чем ваш персонаж никогда не будет говорить?\nОтвет: "
                    + message.text
    )
    data = await state.get_data()
    request = CharacterCreationRequest(user_id=int(data['user_id']), name=data['name'], personality=data['personality'], params=None)
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

            async with session.post(
                f"{FASTAPI_URL}/api/v1/select_character",
                json=CharacterSelectionRequest(user_id=int(data['user_id']),
                                                character_id=char_id).model_dump(mode='json')
            ) as response:
                if response.status != 200:
                    await message.answer("Ошибка при выборе персонажа")
                    return

            async with session.post(
                f"{FASTAPI_URL}/api/v1/chat/hello_message",
                json=HelloMessageRequest(user_id=int(data['user_id'])).model_dump(mode='json')
            ) as response:
                if response.status != 200:
                    await message.answer("Ошибка при генерации сообщения")
                    return
                bot_answer = MessageResponse(**(await response.json())).message
            await message.answer(bot_answer)
    except Exception as e:
        await message.answer(f"Ошибка {e}")

    await state.set_state(chat)