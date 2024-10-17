import asyncio
import uuid
from functools import wraps
from typing import Callable

from . import context


class RequestIdCtx(context.ContextStorage):
    def __init__(self, id_generator: Callable[..., str] = lambda: str(uuid.uuid4())):
        super().__init__()
        self.id_generator = id_generator

    def create(self) -> str:
        value = self.id_generator()
        self.set(value)
        return value


request_id_ctx = RequestIdCtx()


def set_request_id():
    def decorator(fn):
        if asyncio.iscoroutinefunction(fn):

            @wraps(fn)
            async def wrapper(*args, **kwargs):
                request_id_ctx.create()
                return await fn(*args, **kwargs)

        else:

            @wraps(fn)
            def wrapper(*args, **kwargs):
                request_id_ctx.create()
                return fn(*args, **kwargs)

        return wrapper

    return decorator
