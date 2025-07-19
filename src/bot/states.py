from aiogram.fsm.state import StatesGroup, State\

class OnBoarding(StatesGroup):
    waiting_for_start = State()
    waiting_onboarding_menu = State()

class CreateCharacter(StatesGroup):
    waiting_for_name = State()
    waiting_for_archetype = State()
    waiting_for_personality = State()
    waiting_for_hobbies = State()
    waiting_for_critique_tolerance = State()
    waiting_for_taboo = State()

class SelectPreDefinedCharacter(StatesGroup):
    waiting_for_selection = State()

class CharactersManagementMenu(StatesGroup):
    waiting_for_option = State()
    waiting_for_chat_selection_confirmation = State()
    waiting_for_delete_selection = State()
    waiting_for_sharing_selection = State()

chat = State()