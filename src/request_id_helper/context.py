from contextvars import ContextVar, Token
from typing import Any


class ContextStorage:
    DEFAULT_VALUE: Any = ""
    CONTEXT_KEY_NAME = "default"

    def __init__(self) -> None:
        self._values: ContextVar[Any] = ContextVar(
            self.CONTEXT_KEY_NAME, default=self.DEFAULT_VALUE
        )
        self._tokens: ContextVar[Token[Any] | None] = ContextVar(
            f"{self.CONTEXT_KEY_NAME}_reset_token", default=None
        )

    def get(self) -> Any:
        return self._values.get()

    def set(self, value: Any) -> None:
        token = self._values.set(value)
        self._tokens.set(token)

    def reset(self) -> None:
        token = self._tokens.get()
        if token is not None:
            self._values.reset(token)
            self._tokens.set(None)
