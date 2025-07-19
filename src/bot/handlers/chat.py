from aiogram import Router, types
from storage import user_data

router = Router()


@router.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    selected_id = user_data.get(user_id, {}).get("selected")
    if not selected_id:
        await message.reply("Сначала выбери персонажа через «Мои персонажи».")
        return
    character = next(
        (c for c in user_data[user_id]["characters"] if c["id"] == selected_id), None
    )
    if not character:
        await message.reply("Персонаж не найден.")
        return
    await message.reply(f"[{character['name']}]: Это тестовый ответ персонажа.")
