from ...base import MaxObject, UNSET, UNSET_TYPE
from pydantic import Field


class UploadUrl(MaxObject):
    url: str = Field(..., description="The URL to which the file should be uploaded")
    token: str | UNSET_TYPE = Field(
        UNSET, description="Token for the upload, if applicable"
    )
