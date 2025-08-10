from aiogram.fsm.state import State, StatesGroup


class AdminState(StatesGroup):
    add_admin_set_telegram_id = State()
    remove_admin_set_telegram_id = State()
    remove_admin_confirm = State()

    add_moderator_set_telegram_id = State()
    remove_moderator_set_telegram_id = State()
    remove_moderator_confirm = State()
