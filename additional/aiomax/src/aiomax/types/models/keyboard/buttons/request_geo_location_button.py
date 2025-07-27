from .base import KeyboardButtonBase
from typing import Literal
from pydantic import Field


class RequestGeoLocationButton(KeyboardButtonBase):
    type: Literal["request_geo_location"] = "request_geo_location"
    quick: bool = Field(
        False,
        description="If True, send location without confirmation from the user",
    )
