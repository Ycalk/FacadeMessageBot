from maxapi.context import State, StatesGroup


class UserStates(StatesGroup):
    get_message = State()  # Ввод текста поздравления (первый шаг)
    get_name = State()  # Ввод имени
    get_city = State()  # Ввод города
    confirm_city = State()  # Подтверждение города
    choose_background = State()  # Выбор фона (вместо рамки)
    preview = State()  # Предпросмотр с кнопками "Назад" и "Отправить"
