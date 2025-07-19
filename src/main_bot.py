import time
time.sleep(10)


import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN

# from handlers.character import router as character_router
from bot.handlers.onboarding import router as onboarding_router
from bot.handlers.create_character import router as create_router
from bot.handlers.chat import router as chat_router
from bot.handlers.select_predefined_character import router as select_predef_router
from bot.handlers.random_character import router as rand_char_r

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

dp.include_router(onboarding_router)
dp.include_router(create_router)
dp.include_router(select_predef_router)
dp.include_router(rand_char_r)
dp.include_router(chat_router)


if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
