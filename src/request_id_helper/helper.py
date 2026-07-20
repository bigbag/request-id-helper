from collections.abc import Callable, Generator
from contextlib import contextmanager
from contextvars import Token
from functools import wraps
from inspect import iscoroutinefunction
from typing import Any, TypeVar, cast
from uuid import uuid4

from . import context

F = TypeVar("F", bound=Callable[..., Any])


class RequestIdCtx(context.ContextStorage):
    def __init__(self, id_generator: Callable[[], str] | None = None) -> None:
        super().__init__()
        self.id_generator = id_generator or (lambda: str(uuid4()))

    def create(self) -> str:
        value = self.id_generator()
        self.set(value)
        return value

    @contextmanager
    def _new_scope(self) -> Generator[str, None, None]:
        value = self.id_generator()
        token: Token[Any] = self._values.set(value)
        try:
            yield value
        finally:
            self._values.reset(token)


request_id_ctx = RequestIdCtx()


def set_request_id() -> Callable[[F], F]:
    def decorator(function: F) -> F:
        if iscoroutinefunction(function):
            async_function = cast(Callable[..., Any], function)

            @wraps(function)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                with request_id_ctx._new_scope():
                    return await async_function(*args, **kwargs)

            return cast(F, async_wrapper)

        @wraps(function)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            with request_id_ctx._new_scope():
                return function(*args, **kwargs)

        return cast(F, sync_wrapper)

    return decorator
