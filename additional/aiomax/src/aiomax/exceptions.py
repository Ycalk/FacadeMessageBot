from typing import Any


class MaxError(Exception):
    """Base class for all Max-related exceptions."""

    pass


class DecodeModelError(MaxError):
    """Raised when decoding fails."""

    def __init__(self, original_exception: Exception, model: type, data: Any):
        self.original_exception = original_exception
        self.model = model
        self.data = data

    def __str__(self):
        original_exception_type = type(self.original_exception)
        return (
            f"Failed to decode model: {self.model.__module__}.{self.model.__name__}\n"
            f"Original Exception: {original_exception_type.__module__}.{original_exception_type.__name__}\n"
            f"Decoding Data: {self.data}"
        )


class APIError(MaxError):
    """Base class for API-related errors."""

    def __init__(self, status_code: int, message: str, method: type):
        self.status_code = status_code
        self.message = message
        self.method = method

    def __str__(self) -> str:
        self_type = type(self)
        return (
            f"{self_type.__module__}.{self_type.__name__}: {self.status_code} - {self.message}\n"
            f"Method: {self.method.__module__}.{self.method.__name__}"
        )


class BadRequestError(APIError):
    """Raised when the request is malformed or invalid."""

    def __init__(self, method: type, message: str = "Bad Request"):
        super().__init__(400, message, method)


class UnauthorizedError(APIError):
    """Raised when authentication fails."""

    def __init__(self, method: type, message: str = "Unauthorized"):
        super().__init__(401, message, method)


class NotFoundError(APIError):
    """Raised when the requested resource is not found."""

    def __init__(self, method: type, message: str = "Not Found"):
        super().__init__(404, message, method)


class MethodNotAllowedError(APIError):
    """Raised when the method is not allowed for the requested resource."""

    def __init__(self, method: type, message: str = "Method Not Allowed"):
        super().__init__(405, message, method)


class TooManyRequestsError(APIError):
    """Raised when the rate limit is exceeded."""

    def __init__(self, method: type, message: str = "Too Many Requests"):
        super().__init__(429, message, method)


class ServiceUnavailableError(APIError):
    """Raised when the service is unavailable."""

    def __init__(self, method: type, message: str = "Service Unavailable"):
        super().__init__(503, message, method)
