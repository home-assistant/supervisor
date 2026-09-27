"""Test API utils."""

import asyncio
from unittest.mock import MagicMock, patch

import pytest

from supervisor.api.utils import stop_on_disconnect


@pytest.fixture(autouse=True)
def fast_disconnect_check():
    """Check for client disconnects without delay."""
    with patch("supervisor.api.utils.DISCONNECT_CHECK_INTERVAL", 0):
        yield


async def test_stop_on_disconnect_stops_block():
    """Test the wrapped block is stopped once the client disconnects."""
    request = MagicMock()
    request.transport.is_closing.return_value = False
    reached_end = False

    async def handler() -> str:
        nonlocal reached_end
        async with stop_on_disconnect(request):
            await asyncio.sleep(3600)
            reached_end = True
        return "done"

    task = asyncio.create_task(handler())
    await asyncio.sleep(0.01)
    assert not task.done()

    request.transport = None
    assert await asyncio.wait_for(task, 1) == "done"
    assert not reached_end
    assert task.cancelling() == 0


async def test_stop_on_disconnect_connected():
    """Test the wrapped block runs normally while the client is connected."""
    request = MagicMock()
    request.transport.is_closing.return_value = False

    async with stop_on_disconnect(request):
        await asyncio.sleep(0.01)

    assert asyncio.current_task().cancelling() == 0


async def test_stop_on_disconnect_external_cancel():
    """Test cancellation not caused by a disconnect is propagated."""
    request = MagicMock()
    request.transport.is_closing.return_value = False

    async def handler() -> None:
        async with stop_on_disconnect(request):
            await asyncio.sleep(3600)

    task = asyncio.create_task(handler())
    await asyncio.sleep(0.01)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
