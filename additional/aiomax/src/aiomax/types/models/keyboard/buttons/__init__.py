from .callback_button import CallbackButton
from .link_button import LinkButton
from .message_button import MessageButton
from .open_app_button import OpenAppButton
from .request_contact_button import RequestContactButton
from .request_geo_location_button import RequestGeoLocationButton
from typing import Union, Annotated
from pydantic import Field


KeyboardButton = Annotated[
    Union[
        CallbackButton,
        LinkButton,
        MessageButton,
        OpenAppButton,
        RequestContactButton,
        RequestGeoLocationButton,
    ],
    Field(discriminator="type", description="Type of the button"),
]

__all__ = [
    "KeyboardButton",
    "CallbackButton",
    "LinkButton",
    "MessageButton",
    "OpenAppButton",
    "RequestContactButton",
    "RequestGeoLocationButton",
]
