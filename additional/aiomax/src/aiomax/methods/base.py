from typing import Any, Dict, Generic, TypeVar
from pydantic import BaseModel, ConfigDict
from ..types.base import MaxObject, UNSET
from abc import ABC, abstractmethod

ResponseT = TypeVar("ResponseT", bound=MaxObject)


class QueryParameterMarker:
    """Marker class for query parameters in Pydantic models."""

    pass


class BodyParameterMarker:
    """Marker class for body parameters in Pydantic models."""

    pass


class MaxMethod(BaseModel, Generic[ResponseT], ABC):
    model_config = ConfigDict(
        extra="allow",
        arbitrary_types_allowed=True,
        frozen=True,
    )

    @property
    @abstractmethod
    def endpoint(self) -> str:
        """Get method endpoint

        Returns:
            str: Endpoint URL for the method, e.g. "/method"
        """
        ...

    @property
    @abstractmethod
    def method(self) -> str:
        """Get method name

        Returns:
            str: Name of the method, e.g. "POST", "GET", etc.
        """
        ...

    @abstractmethod
    def load_response(self, json_data: str | bytes | bytearray) -> ResponseT:
        """Decode the response from the API.

        Args:
            response (Any): The raw response from the API.

        Returns:
            ResponseT: Decoded response as a Pydantic model.
        """
        ...

    @property
    def query_parameters(self) -> Dict[str, str]:
        return self._get_parameter(QueryParameterMarker)

    @property
    def body(self) -> Dict[str, Any]:
        return self._get_parameter(BodyParameterMarker)

    def _get_parameter(
        self, marker: type[QueryParameterMarker | BodyParameterMarker]
    ) -> Dict[str, Any]:
        """Get parameters marked with a specific marker.

        Args:
            marker (type): The marker class to filter parameters.

        Returns:
            Dict[str, Any]: Dictionary of parameters filtered by the marker.
        """
        result: Dict[str, Any] = {}

        for field_name, model_field in self.__class__.model_fields.items():
            if model_field.metadata:
                if any(isinstance(meta, marker) for meta in model_field.metadata):
                    value = getattr(self, field_name, UNSET)
                    if value is not UNSET:
                        result[field_name] = value
        return result
