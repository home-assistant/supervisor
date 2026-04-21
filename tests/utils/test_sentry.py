"""Unit tests for Sentry."""

import threading
from unittest.mock import patch

import pytest
from sentry_sdk.worker import BackgroundWorker

from supervisor.bootstrap import initialize_coresys, warning_handler


@pytest.mark.usefixtures("supervisor_name", "docker")
async def test_sentry_disabled_by_default():
    """Test diagnostics off by default."""
    with (
        patch("supervisor.bootstrap.initialize_system"),
        patch("sentry_sdk.init") as sentry_init,
    ):
        await initialize_coresys()
        sentry_init.assert_not_called()


def test_sentry_sdk_background_worker_thread_name():
    """Test that the Sentry SDK background worker thread name starts with 'sentry-sdk.'.

    The warning_handler in bootstrap.py skips capture_exception for warnings
    originating from threads named 'sentry-sdk.*' to prevent a feedback loop.
    This test ensures the SDK still uses the expected naming convention.
    """
    worker = BackgroundWorker()
    worker.submit(lambda: None)
    try:
        assert worker._thread is not None
        assert worker._thread.name.startswith("sentry-sdk.")
    finally:
        worker.kill()


def test_warning_handler_suppresses_on_sentry_thread():
    """Test that warning_handler does not call capture_exception on Sentry threads."""
    with patch("supervisor.bootstrap.capture_exception") as mock_capture:
        # Simulate being called from a Sentry SDK background thread
        original_name = threading.current_thread().name
        try:
            threading.current_thread().name = "sentry-sdk.BackgroundWorker"
            warning_handler(UserWarning("test"), UserWarning, "test.py", 1, None, None)
            mock_capture.assert_not_called()
        finally:
            threading.current_thread().name = original_name


def test_warning_handler_captures_on_main_thread():
    """Test that warning_handler calls capture_exception on non-Sentry threads."""
    with patch("supervisor.bootstrap.capture_exception") as mock_capture:
        warning = UserWarning("test")
        warning_handler(warning, UserWarning, "test.py", 1, None, None)
        mock_capture.assert_called_once_with(warning)
