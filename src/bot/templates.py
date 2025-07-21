from app.schemas import CharacterCreationRequest
from uuid import UUID
import requests

from config import FASTAPI_URL
from app.prompts import PICKME_PROMPT, GERALT_PROMPT, NEKO_PROMPT, SMART_PROMPT


ONBOARDING_HELLO_TEMPLATE = """{name}, добро пожаловать!
"Фабрика Персонажей" поможет тебе:

- Понять любого человека  
- Прокачать навыки общения
- Разнообразить досуг  
- Освободиться от неловких пауз"""

ONBOARDING_MENU = """У тебя три варианта:

1. Создать своего персонажа
2. Воспользоваться готовым персонажем
3. Создать рандомного персонажа"""

ONBOARDING_CREATION_HELLO = """Прямо здесь ты можешь дать жизнь AI-персонажу, наделив его характером и уникальным стилем общения. 

Чем точнее ты его опишешь, тем интереснее и глубже станет ваше общение."""

archs_mapping = [
                 'Наставник',
                 'Понимающий',
                 'Мотиватор',
                 'Клоун',
                 'Провокатор',
                 'Романтик',
                 'Исследователь',
                 'Манипулятор',
                         ]

def get_char_mapping():

    chars_mapping = []

    for prompt, name in zip(
            [GERALT_PROMPT, SMART_PROMPT, NEKO_PROMPT, PICKME_PROMPT],
            ["Геральт из Ривии", "Умный мальчик в очках", "Кошко-девочка Юки", "Пикми герл"]
    ):
        request = CharacterCreationRequest(user_id=0, name=name, params=prompt, personality=None)

        try:
            response = requests.post(
                f"{FASTAPI_URL}/api/v1/create_character",
                json=request.model_dump(mode='json'),
                headers={"Content-Type": "application/json"}  # Often needed for JSON data
            )
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

            if response.status_code != 201:
                # This part might be redundant if raise_for_status() is used,
                # but good for explicit checking if needed.
                print(f"Ошибка при создании персонажа: {response.status_code}")
                # If `message.answer` was used in an async context,
                # you'll need a synchronous alternative here.
                # For now, we'll just print.
                continue  # Move to the next iteration

            char_id = response.json()
            char_id = UUID(char_id['character_id'])
            chars_mapping.append(char_id)
            print(f"Персонаж '{name}' успешно создан с ID: {char_id}")


        except requests.exceptions.RequestException as e:
            print(f"Ошибка при создании персонажа для '{name}': {e}")
            # Synchronous alternative for `message.answer`
            # For now, we'll just print.
            continue  # Move to the next iteration
    return chars_mapping

chars_mapping = get_char_mapping()

ONBOARDING_SELECT_PREDEFINED = """Знакомься с разными характерами. Выбери, кто тебе больше по душе, 
или кого хочешь лучше понять."""