from ...base import MaxObject
from typing import Literal
from pydantic import Field


class LocationAttachment(MaxObject):
    type: Literal["location"] = "location"
    latitude: float = Field(..., description="Latitude of the location")
    longitude: float = Field(..., description="Longitude of the location")
