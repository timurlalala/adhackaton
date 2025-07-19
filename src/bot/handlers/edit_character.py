# handlers/edit_character.py

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from storage import user_data
from states import EditCharacter

router = Router()


# 1) Меню полей по нажатию «edit_<id>»
@router.callback_query(F.data.regexp(r"^edit_(\d+)$"))
async def edit_menu(callback: types.CallbackQuery, state: FSMContext):
    cid = int(callback.data.split("_")[1])
    await state.update_data(editing_id=cid)

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👤 Имя", callback_data="field_name")],
            [
                InlineKeyboardButton(
                    text="📝 Описание", callback_data="field_description"
                )
            ],
            [InlineKeyboardButton(text="🎭 Архетип", callback_data="field_arch")],
            [
                InlineKeyboardButton(
                    text="🧠 Интеллект", callback_data="field_intellect"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❤️ Эмоциональность", callback_data="field_emotionality"
                )
            ],
            [InlineKeyboardButton(text="🗣 Манера речи", callback_data="field_speech")],
            [InlineKeyboardButton(text="🧩 Конфликт", callback_data="field_conflict")],
            [InlineKeyboardButton(text="🛑 Запреты", callback_data="field_taboo")],
            [
                InlineKeyboardButton(
                    text="🪄 Особенности", callback_data="field_features"
                )
            ],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_edit")],
        ]
    )

    await callback.message.answer("✏️ Что редактируем?", reply_markup=kb)
    await state.set_state(EditCharacter.choosing_field)
    await callback.answer()


# 2) Пользователь выбрал поле (только в choosing_field)
@router.callback_query(
    StateFilter(EditCharacter.choosing_field), F.data.startswith("field_")
)
async def choose_field(callback: types.CallbackQuery, state: FSMContext):
    step = callback.data.split("_", 1)[1]
    await state.update_data(editing_field=step)

    if step in ("name", "description"):
        prompt = "Введите новое имя:" if step == "name" else "Введите новое описание:"
        await callback.message.answer(f"✍️ {prompt}")
    else:
        options_map = {
            "arch": ["🤝 Друг", "🧙 Наставник", "😈 Враг", "💘 Романтик"],
            "intellect": ["Простой", "Умный", "Философ"],
            "emotionality": ["Холодный", "Умеренный", "Эмоциональный"],
            "speech": ["Сухой", "Образный", "Шутливый", "Цитатный"],
            "conflict": ["Спокоен", "Язвителен", "Уходит от темы"],
            "taboo": ["Не матерится", "Не врет", "Не критикует"],
            "features": ["Повторяет фразу", "Мурчит", "Щёлкает пальцами"],
        }
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=opt, callback_data=f"{step}_{i}")]
                for i, opt in enumerate(options_map[step])
            ]
        )
        # Добавляем вариант "Напишу сам"
        kb.inline_keyboard.append(
            [InlineKeyboardButton(text="✍️ Напишу сам", callback_data=f"{step}_custom")]
        )
        await callback.message.answer(
            f"Выберите новое значение для {step}:", reply_markup=kb
        )

    await state.set_state(EditCharacter.editing_value)
    await callback.answer()


# 2b) Пользователь нажал "..._custom"
@router.callback_query(
    StateFilter(EditCharacter.choosing_field),
    F.data.regexp(
        r"^(name|description|arch|intellect|emotionality|speech|conflict|taboo|features)_custom$"
    ),
)
async def choose_custom_field(callback: types.CallbackQuery, state: FSMContext):
    step = callback.data.split("_", 1)[0]
    await state.update_data(editing_field=step)
    await callback.message.answer("✍️ Введите свой вариант:")
    await state.set_state(EditCharacter.editing_value)
    await callback.answer()


# Обработка  текста (только в editing_value)
@router.message(StateFilter(EditCharacter.editing_value))
async def apply_custom_edit(message: types.Message, state: FSMContext):
    data = await state.get_data()
    uid = message.from_user.id
    cid = data["editing_id"]
    field = data["editing_field"]
    new_value = message.text

    for c in user_data.get(uid, {}).get("characters", []):
        if c["id"] == cid:
            c[field] = new_value
            break

    # Кнопки столбиком
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔁 Ещё одно поле", callback_data=f"edit_{cid}"
                )
            ],
            [InlineKeyboardButton(text="✔️ Готово", callback_data="edit_finish")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_edit")],
        ]
    )
    await message.answer(f"✅ Поле «{field}» обновлено!", reply_markup=kb)
    await state.set_state(EditCharacter.choosing_field)


# 3b) Обработка выбора готовой опции (только в editing_value)
@router.callback_query(
    StateFilter(EditCharacter.editing_value),
    F.data.regexp(
        r"^(arch|intellect|emotionality|speech|conflict|taboo|features)_(\d+)$"
    ),
)
async def apply_choice_edit(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    uid = callback.from_user.id
    cid = data["editing_id"]
    field = data["editing_field"]
    idx = int(callback.data.split("_")[1])

    options_map = {
        "arch": ["🤝 Друг", "🧙 Наставник", "😈 Враг", "💘 Романтик"],
        "intellect": ["Простой", "Умный", "Философ"],
        "emotionality": ["Холодный", "Умеренный", "Эмоциональный"],
        "speech": ["Сухой", "Образный", "Шутливый", "Цитатный"],
        "conflict": ["Спокоен", "Язвителен", "Уходит от темы"],
        "taboo": ["Не матерится", "Не врет", "Не критикует"],
        "features": ["Повторяет фразу", "Мурчит", "Щёлкает пальцами"],
    }
    for c in user_data.get(uid, {}).get("characters", []):
        if c["id"] == cid:
            c[field] = options_map[field][idx]
            break

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔁 Ещё одно поле", callback_data=f"edit_{cid}"
                )
            ],
            [InlineKeyboardButton(text="✔️ Готово", callback_data="edit_finish")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_edit")],
        ]
    )
    await callback.message.answer(f"✅ Поле «{field}» обновлено!", reply_markup=kb)
    await state.set_state(EditCharacter.choosing_field)
    await callback.answer()


# 4) Завершение редактирования
@router.callback_query(F.data == "edit_finish")
async def finish_edit(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("✅ Редактирование завершено.")

    # Сразу отрисовываем обновлённый список персонажей для пользователя
    uid = callback.from_user.id
    chars = user_data.get(uid, {}).get("characters", [])
    if not chars:
        return await callback.message.answer("У тебя пока нет персонажей.")
    for c in chars:
        text = f"👤 <b>{c['name']}</b>\n📝 {c['description']}"
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ Выбрать", callback_data=f"select_{c['id']}"
                    ),
                    InlineKeyboardButton(
                        text="✏️ Редактировать", callback_data=f"edit_{c['id']}"
                    ),
                    InlineKeyboardButton(
                        text="❌ Удалить", callback_data=f"delete_{c['id']}"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="🔍 Подробнее", callback_data=f"details_{c['id']}"
                    )
                ],
            ]
        )
        await callback.message.answer(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


# 5) Отмена редактирования
@router.callback_query(F.data == "cancel_edit")
async def cancel_edit(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("❌ Редактирование отменено.")

    # И снова показываем список
    uid = callback.from_user.id
    chars = user_data.get(uid, {}).get("characters", [])
    if not chars:
        return await callback.message.answer("У тебя пока нет персонажей.")
    for c in chars:
        text = f"👤 <b>{c['name']}</b>\n📝 {c['description']}"
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ Выбрать", callback_data=f"select_{c['id']}"
                    ),
                    InlineKeyboardButton(
                        text="✏️ Редактировать", callback_data=f"edit_{c['id']}"
                    ),
                    InlineKeyboardButton(
                        text="❌ Удалить", callback_data=f"delete_{c['id']}"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="🔍 Подробнее", callback_data=f"details_{c['id']}"
                    )
                ],
            ]
        )
        await callback.message.answer(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()
