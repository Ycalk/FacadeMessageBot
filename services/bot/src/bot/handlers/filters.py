from maxapi import F
from ..utils import UserState

send_message_filter = F.callback.payload == "send_message"
select_city_filter = F.callback.payload.startswith("select_city_")
confirm_city_filter = F.callback.payload == "confirm_city"
get_photo_solution_filter = F.callback.payload.startswith("accept_get_photo") | F.callback.payload.startswith("reject_get_photo")
confirm_fields_filter = F.callback.payload.in_(["confirm_fields", "edit_fields"])

# Фильтры для сообщений с проверкой состояния (используются через states= в декораторах)
get_message_states = [UserState.GET_MESSAGE]
get_name_states = [UserState.GET_NAME]
get_city_states = [UserState.GET_CITY]
select_city_states = [UserState.SELECT_CITY]
confirm_city_states = [UserState.CONFIRM_CITY]
get_photo_solution_states = [UserState.GET_PHOTO_SOLUTION]
confirm_fields_states = [UserState.CONFIRM_FIELDS]

# Фильтр для команды /create
create_command_filter = F.message.text == "/create"