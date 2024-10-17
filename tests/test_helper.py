from unittest.mock import patch

import pytest

from request_id_helper import RequestIdCtx, request_id_ctx, set_request_id


def test_request_id_ctx():
    assert request_id_ctx.set("TEST") is None
    assert request_id_ctx.get() == "TEST"


def test_custom_id_generator():
    request_id_ctx = RequestIdCtx(lambda: "REQUEST_ID")
    assert request_id_ctx.create() == "REQUEST_ID"


def test_set_request_id_sync():
    @set_request_id()
    def sample_sync_function():
        return "sync_result"

    with patch.object(request_id_ctx, "create") as mock_create:
        result = sample_sync_function()

    assert result == "sync_result"
    mock_create.assert_called_once()


@pytest.mark.asyncio
async def test_set_request_id_async():
    @set_request_id()
    async def sample_async_function():
        return "async_result"

    with patch.object(request_id_ctx, "create") as mock_create:
        result = await sample_async_function()

    assert result == "async_result"
    mock_create.assert_called_once()


def test_set_request_id_sync_with_args():
    @set_request_id()
    def sample_sync_function_with_args(arg1, arg2):
        return f"sync_result: {arg1}, {arg2}"

    with patch.object(request_id_ctx, "create") as mock_create:
        result = sample_sync_function_with_args("hello", "world")

    assert result == "sync_result: hello, world"
    mock_create.assert_called_once()


@pytest.mark.asyncio
async def test_set_request_id_async_with_args():
    @set_request_id()
    async def sample_async_function_with_args(arg1, arg2):
        return f"async_result: {arg1}, {arg2}"

    with patch.object(request_id_ctx, "create") as mock_create:
        result = await sample_async_function_with_args("hello", "world")

    assert result == "async_result: hello, world"
    mock_create.assert_called_once()


def test_set_request_id_sync_with_kwargs():
    @set_request_id()
    def sample_sync_function_with_kwargs(**kwargs):
        return f"sync_result: {kwargs}"

    with patch.object(request_id_ctx, "create") as mock_create:
        result = sample_sync_function_with_kwargs(key1="value1", key2="value2")

    assert result == "sync_result: {'key1': 'value1', 'key2': 'value2'}"
    mock_create.assert_called_once()


@pytest.mark.asyncio
async def test_set_request_id_async_with_kwargs():
    @set_request_id()
    async def sample_async_function_with_kwargs(**kwargs):
        return f"async_result: {kwargs}"

    with patch.object(request_id_ctx, "create") as mock_create:
        result = await sample_async_function_with_kwargs(key1="value1", key2="value2")

    assert result == "async_result: {'key1': 'value1', 'key2': 'value2'}"
    mock_create.assert_called_once()


def test_set_request_id_preserves_function_metadata():
    def sample_function():
        """Sample docstring"""
        pass

    decorated_function = set_request_id()(sample_function)

    assert decorated_function.__name__ == "sample_function"
    assert decorated_function.__doc__ == "Sample docstring"


@pytest.mark.asyncio
async def test_set_request_id_preserves_async_function_metadata():
    async def sample_async_function():
        """Sample async docstring"""
        pass

    decorated_function = set_request_id()(sample_async_function)

    assert decorated_function.__name__ == "sample_async_function"
    assert decorated_function.__doc__ == "Sample async docstring"
