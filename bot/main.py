import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from handlers.start import router as start_router

# from handlers.character import router as character_router
from handlers.chat import router as chat_router
from handlers.create_character import router as create_router
from handlers.manage_characters import router as manage_router
from handlers.edit_character import router as edit_router

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

dp.include_router(start_router)
# dp.include_router(character_router)
dp.include_router(create_router)
# dp.include_router(create_router)
dp.include_router(manage_router)
dp.include_router(chat_router)
dp.include_router(edit_router)

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
