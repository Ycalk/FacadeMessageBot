from pydantic import BaseModel, Field, model_validator
from shared_models.enums import ModerationResult as ModerationResultEnum


class ModerationResult(BaseModel):
    message_id: int = Field(..., description="ID сообщения")
    result: ModerationResultEnum = Field(..., description="Результат модерации")
    time: int | None = Field(
        None,
        description="Время, когда будет опубликовано сообщение (timestamp in seconds)",
    )

    @model_validator(mode="after")
    def check_time_required_for_approved(self):
        if self.result == ModerationResultEnum.APPROVED and self.time is None:
            raise ValueError("Time field required, if result is APPROVED")
        if self.result == ModerationResultEnum.REJECTED and self.time is not None:
            raise ValueError("Time field must be None, if result is REJECTED")
        return self
