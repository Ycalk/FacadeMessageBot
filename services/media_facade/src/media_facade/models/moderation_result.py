from pydantic import BaseModel, Field, model_validator
from shared_models.enums import ModerationResult as ModerationResultEnum


class ModerationResult(BaseModel):
    message_id: int = Field(..., description="ID сообщения")
    result: ModerationResultEnum = Field(..., description="Результат модерации")
    ts_from: int | None = Field(
        None,
        description="Начальное время показа (timestamp in seconds)",
    )
    ts_to: int | None = Field(
        None,
        description="Конечное время показа (timestamp in seconds)",
    )
    reason: str | None = Field(
        None,
        description="Причина отклонения, если результат REJECTED",
    )

    @model_validator(mode="after")
    def check_time_required_for_approved(self):
        if self.result == ModerationResultEnum.APPROVED and (
            self.ts_from is None or self.ts_to is None
        ):
            raise ValueError("ts_from and ts_to must be set if result is APPROVED")
        if self.result == ModerationResultEnum.REJECTED and (
            self.ts_from is not None or self.ts_to is not None
        ):
            raise ValueError("ts_from and ts_to must not be set if result is REJECTED")
        return self
