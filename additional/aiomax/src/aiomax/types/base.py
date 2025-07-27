from pydantic import BaseModel, ConfigDict, model_validator
from typing import Dict, Any, Final
from abc import ABC


class UnsetType:
    def __repr__(self):
        return "<UNSET>"

    def __bool__(self):
        return False


UNSET: Final[UnsetType] = UnsetType()
UNSET_TYPE = UnsetType


class MaxObject(BaseModel, ABC):
    model_config = ConfigDict(
        extra="allow",
        arbitrary_types_allowed=True,
        frozen=True,
    )

    @model_validator(mode="before")
    def remove_unset_fields(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(values, dict):
            return values
        return {k: v for k, v in values.items() if v is not UNSET}

    def model_dump(self, *args, **kwargs) -> dict:
        original = super().model_dump(*args, **kwargs)
        return {k: v for k, v in original.items() if v is not UNSET}
