from ..base import MaxObject
from pydantic import Field


class Result(MaxObject):
    success: bool = Field(
        ...,
        description="Indicates whether the operation was successful",
    )
    message: str | None = Field(
        None,
        description="Message if result is not successful",
    )
