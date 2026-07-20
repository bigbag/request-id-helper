import asyncio

import pytest

from request_id_helper.context import ContextStorage


def test_context_storage_returns_default_and_resets_last_value() -> None:
    storage = ContextStorage()

    assert storage.get() == ""
    assert storage.set("first") is None
    assert storage.get() == "first"
    storage.reset()
    assert storage.get() == ""


def test_context_storage_reset_without_a_token_is_a_noop() -> None:
    storage = ContextStorage()

    storage.reset()

    assert storage.get() == ""


@pytest.mark.asyncio
async def test_context_storage_keeps_reset_tokens_isolated_per_task() -> None:
    storage = ContextStorage()
    ready = asyncio.Event()
    release = asyncio.Event()

    async def worker(value: str) -> tuple[str, str]:
        storage.set(value)
        ready.set()
        await release.wait()
        before_reset = storage.get()
        storage.reset()
        return before_reset, storage.get()

    first = asyncio.create_task(worker("first"))
    await ready.wait()
    ready.clear()
    second = asyncio.create_task(worker("second"))
    await ready.wait()
    release.set()

    assert sorted(await asyncio.gather(first, second)) == [("first", ""), ("second", "")]


def test_context_storage_can_be_bound_again_after_reset() -> None:
    storage = ContextStorage()

    storage.set("first")
    storage.reset()
    storage.set("second")

    assert storage.get() == "second"
    storage.reset()
    assert storage.get() == ""
