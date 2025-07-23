from typing import Any, Dict, Generic, Optional, TypeVar
from pydantic import BaseModel
from typing import get_args, get_origin, Annotated
from abc import ABC, abstractmethod

ResponseT = TypeVar("ResponseT", bound=BaseModel)


class QueryParameterMarker:
    """Marker class for query parameters in Pydantic models."""

    pass


class BodyParameterMarker:
    """Marker class for body parameters in Pydantic models."""

    pass


class MaxMethod(BaseModel, Generic[ResponseT], ABC):
    access_token: Optional[str] = None

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

    def _get_parameter(
        self, marker: type[QueryParameterMarker | BodyParameterMarker]
    ) -> Dict[str, Any]:
        """Get parameters marked with a specific marker.

        Args:
            marker (type): The marker class to filter parameters.

        Returns:
            Dict[str, Any]: Dictionary of parameters filtered by the marker.
        """
        return {
            field_name: getattr(self, field_name)
            for field_name, model_field in self.__class__.model_fields.items()
            if model_field.annotation
            and get_origin(model_field.annotation) is Annotated
            and any(
                isinstance(meta, marker) for meta in get_args(model_field.annotation)
            )
        }

    @property
    def query_parameters(self) -> Dict[str, str]:
        return self._get_parameter(QueryParameterMarker)

    @property
    def body_parameters(self) -> Dict[str, Any]:
        return self._get_parameter(BodyParameterMarker)
