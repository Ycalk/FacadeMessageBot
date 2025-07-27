from ....base import MaxObject
from pydantic import Field


class UploadedInfo(MaxObject):
    token: str | None = Field(None, description="The token of the uploaded file")
