from openai import AsyncOpenAI
from typing import AsyncGenerator
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if OPENAI_API_KEY:
    openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    model_name = "gpt-4o-mini"
else:
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    if OPENROUTER_API_KEY:
        openai_client = AsyncOpenAI(base_url="https://openrouter.ai/api/v1",
                                api_key=OPENROUTER_API_KEY)
        model_name = "deepseek/deepseek-chat-v3-0324:free"
    else:
        raise ValueError("API_KEY не установлен в переменных окружения.")



async def get_openai_client() -> AsyncGenerator[AsyncOpenAI, None]:
    """
    Зависимость FastAPI для предоставления асинхронного клиента OpenAI.
    """
    try:
        yield openai_client
    finally:
        pass

async def get_llm_name() -> AsyncGenerator[str, None]:
    """
    Имя модели
    :return:
    """
    try:
        yield model_name
    finally:
        pass