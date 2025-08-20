from pydantic import BaseModel, Field
from datetime import datetime
from typing import Annotated
from uuid import UUID


class Image(BaseModel):
    id: Annotated[
        UUID,
        Field(
            description="Unique identifier for the image",
        ),
    ]
    image_base64: Annotated[
        str,
        Field(
            ...,
            description="Base64 encoded image data",
        ),
    ]
    text: Annotated[str, Field(..., description="Recognized text")]
    created_at: Annotated[
        datetime,
        Field(
            description="Datetime of when the image was created",
        ),
    ]

    def __str__(self) -> str:
        return self.text
