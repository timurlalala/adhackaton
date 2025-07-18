from aiogram.fsm.state import StatesGroup, State


class CreateCharacter(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_archetype = State()
    waiting_for_intellect = State()
    waiting_for_emotionality = State()
    waiting_for_speech = State()
    waiting_for_conflict = State()
    waiting_for_taboo = State()
    waiting_for_features = State()
    waiting_for_custom_prompt = State()


class EditCharacter(StatesGroup):
    choosing_field = State()
    editing_value = State()
