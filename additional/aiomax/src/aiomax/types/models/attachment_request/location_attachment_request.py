from ...base import MaxObject
from typing import Literal


class LocationAttachmentRequest(MaxObject):
    type: Literal["location"] = "location"
    latitude: float
    longitude: float
