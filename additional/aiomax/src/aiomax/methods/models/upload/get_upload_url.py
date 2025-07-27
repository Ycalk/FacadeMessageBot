from ...base import MaxMethod, QueryParameterMarker
from ....types import UploadUrl
from ....types import UploadType
from pydantic import Field
from typing import Annotated


class GetUploadUrl(MaxMethod[UploadUrl]):
    """Get an upload URL for uploading files.

    Args:
        type (UploadType): The type of upload. This is a required field.
    """

    type: Annotated[
        UploadType,
        QueryParameterMarker(),
        Field(..., description="Upload type"),
    ]

    @property
    def endpoint(self) -> str:
        return "/uploads"

    @property
    def method(self) -> str:
        return "POST"

    def load_response(self, json_data: str | bytes | bytearray) -> UploadUrl:
        return UploadUrl.model_validate_json(json_data)
