from ..base import MaxObject
from pydantic import Field


class Image(MaxObject):
    url: str = Field(
        ...,
        description="The URL of the image. Must be a valid URL pointing to an image file.",
    )
