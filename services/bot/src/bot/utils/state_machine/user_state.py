from enum import StrEnum


class UserState(StrEnum):
    SEND_MESSAGE = "send_message"
    CONFIRM_TERMS_OF_USE = "confirm_terms_of_use"
    WRITE_MESSAGE = "write_message"
    GET_MESSAGE = "get_message"
    GET_NAME = "get_name"
    GET_CITY = "get_city"
    SELECT_CITY = "select_city"
    CONFIRM_CITY = "confirm_city"
    GET_PHOTO_SOLUTION = "get_photo_solution"
    CONFIRM_FIELDS = "confirm_fields"
