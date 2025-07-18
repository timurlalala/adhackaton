# handlers/manage_characters.py
from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from storage import user_data

router = Router()


@router.message(F.text == "📁 Мои персонажи")
async def show_characters(message: types.Message):
    uid = message.from_user.id
    chars = user_data.get(uid, {}).get("characters", [])
    if not chars:
        return await message.answer("Нет персонажей.")

    for c in chars:
        text = f"👤 {c['name']}\n📝 {c['description']}"
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
                    ),
                ],
            ]
        )
        await message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data.startswith("select_"))
async def select_character(callback: types.CallbackQuery):
    uid = callback.from_user.id
    cid = int(callback.data.split("_")[1])
    user_data[uid]["selected"] = cid
    await callback.answer("Выбрано ✅")


@router.callback_query(F.data.startswith("delete_"))
async def delete_character(callback: types.CallbackQuery):
    uid = callback.from_user.id
    cid = int(callback.data.split("_")[1])
    user_data[uid]["characters"] = [
        c for c in user_data[uid]["characters"] if c["id"] != cid
    ]
    if user_data[uid]["selected"] == cid:
        user_data[uid]["selected"] = None
    await callback.answer("Удалено 🗑")


@router.callback_query(F.data.startswith("details_"))
async def show_details(callback: types.CallbackQuery):
    uid = callback.from_user.id
    char_id = int(callback.data.split("_")[1])
    # ищем персонажа
    chars = user_data.get(uid, {}).get("characters", [])
    char = next((c for c in chars if c["id"] == char_id), None)
    if not char:
        return await callback.message.answer("❌ Персонаж не найден.")
    # формируем подробности
    text = (
        f"👤 <b>{char['name']}</b>\n\n"
        f"📝 <i>Описание:</i> {char['description']}\n\n"
        f"🛠️ <i>Инструкция для LLM:</i>\n{char.get('instruction','(нет)')}"
    )
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()
