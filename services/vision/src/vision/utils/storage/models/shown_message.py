from shared_models.messaging import MessageInput
from pydantic import Field
from typing import Annotated
from datetime import datetime
from uuid import UUID, uuid4
from ...config import Config


class ShownMessage(MessageInput):
    id: Annotated[
        UUID,
        Field(
            description="Unique identifier for the image",
        ),
    ] = uuid4()
    show_at: Annotated[
        datetime,
        Field(
            description="Timestamp in seconds when the message was shown",
        ),
    ] = datetime.now(tz=Config.TIME_ZONE)
