import asyncio
from uuid import UUID

import pytest

from request_id_helper import RequestIdCtx, request_id_ctx, set_request_id


def test_request_id_ctx_create_uses_custom_generator() -> None:
    context = RequestIdCtx(lambda: "REQUEST_ID")

    assert context.create() == "REQUEST_ID"
    assert context.get() == "REQUEST_ID"


def test_sync_decorator_exposes_generated_id_only_during_call() -> None:
    request_id_ctx.set("parent")

    @set_request_id()
    def handler() -> str:
        return request_id_ctx.get()

    request_id = handler()

    assert request_id != "parent"
    assert request_id_ctx.get() == "parent"
    request_id_ctx.reset()


def test_sync_decorator_restores_parent_after_exception() -> None:
    request_id_ctx.set("parent")

    @set_request_id()
    def handler() -> None:
        assert request_id_ctx.get() != "parent"
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        handler()

    assert request_id_ctx.get() == "parent"
    request_id_ctx.reset()


@pytest.mark.asyncio
async def test_async_decorator_restores_parent_after_cancellation() -> None:
    request_id_ctx.set("parent")
    started = asyncio.Event()

    @set_request_id()
    async def handler() -> None:
        assert request_id_ctx.get() != "parent"
        started.set()
        await asyncio.Future()

    task = asyncio.create_task(handler())
    await started.wait()
    task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await task

    assert request_id_ctx.get() == "parent"
    request_id_ctx.reset()


@pytest.mark.asyncio
async def test_async_decorator_restores_the_default_after_exception() -> None:
    @set_request_id()
    async def handler() -> None:
        assert request_id_ctx.get()
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        await handler()

    assert request_id_ctx.get() == ""


def test_nested_decorators_restore_the_outer_id() -> None:
    seen: list[str] = []

    @set_request_id()
    def inner() -> None:
        seen.append(request_id_ctx.get())

    @set_request_id()
    def outer() -> None:
        outer_id = request_id_ctx.get()
        inner()
        seen.append(request_id_ctx.get())
        assert seen[0] != outer_id

    outer()

    assert seen[0] != seen[1]
    assert request_id_ctx.get() == ""


@pytest.mark.asyncio
async def test_async_decorator_isolates_concurrent_calls() -> None:
    entered = asyncio.Event()
    release = asyncio.Event()

    @set_request_id()
    async def handler() -> str:
        entered.set()
        await release.wait()
        return request_id_ctx.get()

    first = asyncio.create_task(handler())
    await entered.wait()
    entered.clear()
    second = asyncio.create_task(handler())
    await entered.wait()
    release.set()

    first_id, second_id = await asyncio.gather(first, second)

    assert first_id != second_id
    assert request_id_ctx.get() == ""


def test_decorator_preserves_sync_metadata_and_arguments() -> None:
    @set_request_id()
    def handler(value: str, *, suffix: str) -> str:
        """Return the provided value."""
        return f"{value}{suffix}"

    assert handler("hello", suffix="!") == "hello!"
    assert handler.__name__ == "handler"
    assert handler.__doc__ == "Return the provided value."


@pytest.mark.asyncio
async def test_decorator_preserves_async_metadata_and_arguments() -> None:
    @set_request_id()
    async def handler(value: str, *, suffix: str) -> str:
        """Return the provided value asynchronously."""
        return f"{value}{suffix}"

    assert await handler("hello", suffix="!") == "hello!"
    assert handler.__name__ == "handler"
    assert handler.__doc__ == "Return the provided value asynchronously."


def test_sync_decorator_generates_a_v4_uuid_and_restores_the_default() -> None:
    @set_request_id()
    def handler() -> str:
        return request_id_ctx.get()

    generated_id = handler()

    assert UUID(generated_id).version == 4
    assert request_id_ctx.get() == ""
