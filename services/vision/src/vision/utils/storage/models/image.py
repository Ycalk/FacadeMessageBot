from pydantic import BaseModel, Field
from datetime import datetime
from ...config import Config
from typing import Annotated
from uuid import uuid4, UUID


class Image(BaseModel):
    id: Annotated[
        UUID,
        Field(
            description="Unique identifier for the image",
        ),
    ] = uuid4()
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
    ] = datetime.now(tz=Config.TIME_ZONE)
