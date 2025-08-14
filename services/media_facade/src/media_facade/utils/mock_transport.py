from httpx import AsyncBaseTransport, Request, Response


def mock_request(method: str, path: str):
    """Декоратор для пометки мок-методов с указанием HTTP-метода и пути."""

    def decorator(func):
        func.__is_mock__ = True
        func.__mock_method__ = method.upper()
        func.__mock_path__ = path
        return func

    return decorator


class MockTransport(AsyncBaseTransport):
    def __init__(self) -> None:
        self.mock_endpoints = [
            {
                "name": name,
                "method": getattr(func, "__mock_method__", None),
                "path": getattr(func, "__mock_path__", None),
                "func": func,
            }
            for name, func in self.__class__.__dict__.items()
            if callable(func) and getattr(func, "__is_mock__", False)
        ]

    async def handle_async_request(
        self,
        request: Request,
    ) -> Response:
        await request.aread()
        for mock in self.mock_endpoints:
            if (
                request.method.upper() == mock["method"]
                and request.url.path == mock["path"]
            ):
                return await mock["func"](self, request)
        raise NotImplementedError(
            f"No mock handler for {request.method} {request.url.path}"
        )

    @mock_request(method="POST", path="/message")
    async def add_message(self, request: Request) -> Response:
        return Response(status_code=200)
