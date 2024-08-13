"""Test supervisor logging util methods."""

import asyncio
import logging
import queue
from unittest.mock import patch

import pytest

import supervisor.utils.logging as logging_util


async def test_logging_with_queue_handler() -> None:
    """Test logging with SupervisorQueueHandler."""

    simple_queue = queue.SimpleQueue()  # type: ignore
    handler = logging_util.SupervisorQueueHandler(simple_queue)

    log_record = logging.makeLogRecord({"msg": "Test Log Record"})

    handler.emit(log_record)

    with (
        pytest.raises(asyncio.CancelledError),
        patch.object(handler, "enqueue", side_effect=asyncio.CancelledError),
    ):
        handler.emit(log_record)

    with patch.object(handler, "emit") as emit_mock:
        handler.handle(log_record)
        emit_mock.assert_called_once()

    with (
        patch.object(handler, "filter") as filter_mock,
        patch.object(handler, "emit") as emit_mock,
    ):
        filter_mock.return_value = False
        handler.handle(log_record)
        emit_mock.assert_not_called()

    with (
        patch.object(handler, "enqueue", side_effect=OSError),
        patch.object(handler, "handleError") as mock_handle_error,
    ):
        handler.emit(log_record)
        mock_handle_error.assert_called_once()

    handler.close()

    assert simple_queue.get_nowait().msg == "Test Log Record"
    assert simple_queue.empty()


async def test_migrate_log_handler() -> None:
    """Test migrating log handlers."""

    logging_util.activate_log_queue_handler()

    assert len(logging.root.handlers) == 1
    assert isinstance(logging.root.handlers[0], logging_util.SupervisorQueueHandler)

    # Test that the close hook shuts down the queue handler's thread
    listener_thread = logging.root.handlers[0].listener._thread
    assert listener_thread.is_alive()
    logging.root.handlers[0].close()
    assert not listener_thread.is_alive()
