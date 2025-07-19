from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from states import CreateCharacter
from aiogram.filters.state import StateFilter
from storage import user_data, character_id_counter
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from states import EditCharacter

router = Router()


# --- Хелпер для клавиатуры ---
def get_choice_keyboard(step: str, options: list[str]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=opt, callback_data=f"{step}_{i}")]
            for i, opt in enumerate(options)
        ]
        + [
            [InlineKeyboardButton(text="✍️ Напишу сам", callback_data=f"{step}_custom")],
            [
                InlineKeyboardButton(
                    text="🔄 Начать сначала", callback_data="restart_creation"
                )
            ],
        ]
    )


# --- Сброс создания персонажа ---
@router.callback_query(F.data == "restart_creation")
async def restart_creation(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(
        "🔄 Создание персонажа сброшено. Введи имя персонажа:"
    )
    await state.set_state(CreateCharacter.waiting_for_name)
    await callback.answer()


# --- Начало создания ---
@router.message(F.text == "🆕 Создать персонажа")
async def start_create(message: types.Message, state: FSMContext):
    await state.clear()
    # сохраняем user_id один раз
    await state.update_data(user_id=message.from_user.id)
    await message.answer("👤 Введи имя персонажа:")
    await state.set_state(CreateCharacter.waiting_for_name)


@router.message(CreateCharacter.waiting_for_name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(
        "📝 Введи краткое описание персонажа.\n\n"
        "👉 Подумай:\n• Кто он такой?\n• Зачем он тебе нужен?\n\n"
        "✨ Пример:\n«Бармен, который порекомендует напитки.»"
    )
    await state.set_state(CreateCharacter.waiting_for_description)


@router.message(CreateCharacter.waiting_for_description)
async def get_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(
        "🎭 Выбери архетип:",
        reply_markup=get_choice_keyboard(
            "arch", ["🤝 Друг", "🧙 Наставник", "😈 Враг", "💘 Романтик"]
        ),
    )
    await state.set_state(CreateCharacter.waiting_for_archetype)


# --- Универсальный хендлер выбора характеристики ---
@router.callback_query(
    StateFilter(CreateCharacter),  # ← добавили сюда
    F.data.regexp(r"^(arch|intellect|emot|speech|conflict|taboo|feat)_(\d+|custom)$"),
)
async def handle_choice(callback: types.CallbackQuery, state: FSMContext):
    step_map = {
        "arch": ("archetype", ["Друг", "Наставник", "Враг", "Романтик"]),
        "intellect": ("intellect", ["Простой", "Умный", "Философ"]),
        "emot": ("emotionality", ["Холодный", "Умеренный", "Эмоциональный"]),
        "speech": ("speech", ["Сухой", "Образный", "Шутливый", "Цитатный"]),
        "conflict": ("conflict", ["Спокоен", "Язвителен", "Уходит от темы"]),
        "taboo": ("taboo", ["Не матерится", "Не врет", "Не критикует"]),
        "feat": ("features", ["Повторяет фразу", "Мурчит", "Щёлкает пальцами"]),
    }

    key, label_list = step_map[callback.data.split("_")[0]]
    choice = callback.data.split("_")[1]

    if choice == "custom":
        await state.update_data(_custom_step=key)
        await state.set_state(CreateCharacter.waiting_for_custom_prompt)
        await callback.message.answer(f"✍️ Введи свой вариант:")
        return

    await state.update_data({key: label_list[int(choice)]})
    await callback.answer()
    await ask_next_step(callback.message, state)


# --- Хендлер для "напишу сам" ---
@router.message(CreateCharacter.waiting_for_custom_prompt)
async def handle_custom_input(message: types.Message, state: FSMContext):
    data = await state.get_data()
    key = data.get("_custom_step")
    if key:
        await state.update_data({key: message.text})
        await ask_next_step(message, state)


# --- Переход по шагам создания ---
async def ask_next_step(message: types.Message, state: FSMContext):
    data = await state.get_data()

    if "intellect" not in data:
        await message.answer(
            "🧠 Выбери уровень интеллекта:",
            reply_markup=get_choice_keyboard(
                "intellect", ["Простой", "Умный", "Философ"]
            ),
        )
        await state.set_state(CreateCharacter.waiting_for_intellect)

    elif "emotionality" not in data:
        await message.answer(
            "❤️ Эмоциональность персонажа:",
            reply_markup=get_choice_keyboard(
                "emot", ["Холодный", "Умеренный", "Эмоциональный"]
            ),
        )
        await state.set_state(CreateCharacter.waiting_for_emotionality)

    elif "speech" not in data:
        await message.answer(
            "🗣 Как говорит персонаж?",
            reply_markup=get_choice_keyboard(
                "speech", ["Сухо", "Образно", "Шутливо", "Цитатами"]
            ),
        )
        await state.set_state(CreateCharacter.waiting_for_speech)

    elif "conflict" not in data:
        await message.answer(
            "🧩 Как ведёт себя в конфликте?",
            reply_markup=get_choice_keyboard(
                "conflict", ["Спокоен", "Язвителен", "Уходит от темы"]
            ),
        )
        await state.set_state(CreateCharacter.waiting_for_conflict)

    elif "taboo" not in data:
        await message.answer(
            "🛑 Чего он никогда не делает?",
            reply_markup=get_choice_keyboard(
                "taboo", ["Не матерится", "Не врёт", "Не критикует"]
            ),
        )
        await state.set_state(CreateCharacter.waiting_for_taboo)

    elif "features" not in data:
        await message.answer(
            "🪄 Особенности персонажа? Повторяющиеся привычки, звуки, жесты, любимые фразы.",
            reply_markup=get_choice_keyboard(
                "feat", ["Повторяет фразу", "Мурчит", "Гавкает"]
            ),
        )
        await state.set_state(CreateCharacter.waiting_for_features)

    else:
        await finish_character(message, state)


# --- Финальное сохранение ---
async def finish_character(message: types.Message, state: FSMContext):
    global character_id_counter

    data = await state.get_data()
    # теперь берём именно тот user_id, который сохранили при старте
    user_id = data["user_id"]

    instruction = (
        f"🎭 Архетип: {data['archetype']}\n"
        f"🧠 Интеллект: {data['intellect']}\n"
        f"❤️ Эмоциональность: {data['emotionality']}\n"
        f"🗣 Манера речи: {data['speech']}\n"
        f"🧩 Поведение в конфликте: {data['conflict']}\n"
        f"🛑 Запреты: {data['taboo']}\n"
        f"🪄 Особенности: {data['features']}"
    )

    character = {
        "id": character_id_counter,
        "name": data["name"],
        "description": data["description"],
        "instruction": instruction,
    }
    character_id_counter += 1

    # сохраняем под тем самым user_id
    user_data.setdefault(user_id, {"characters": [], "selected": None})[
        "characters"
    ].append(character)

    # print("user_data теперь:", user_data)  # debug

    await message.answer(f"✅ Персонаж «{character['name']}» создан и сохранён!")
    await state.clear()
