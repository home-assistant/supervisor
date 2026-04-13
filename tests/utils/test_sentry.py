"""Unit tests for Sentry."""

import threading
from unittest.mock import patch

import pytest
from sentry_sdk.worker import BackgroundWorker

from supervisor.bootstrap import initialize_coresys, warning_handler
from supervisor.exceptions import (
    APITooManyRequests,
    DockerError,
    DockerHubRateLimitExceeded,
    DockerRegistryRateLimitExceeded,
    GithubContainerRegistryRateLimitExceeded,
    SupervisorUpdateError,
)
from supervisor.utils.sentry import async_capture_exception, capture_exception


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


@pytest.mark.parametrize(
    "exception",
    [
        APITooManyRequests(),
        DockerRegistryRateLimitExceeded(),
        DockerHubRateLimitExceeded(),
        GithubContainerRegistryRateLimitExceeded(),
    ],
)
def test_capture_exception_skips_rate_limits(exception: BaseException):
    """Test rate limit errors are not sent to Sentry.

    Container registry rate limits are expected transient failures, not bugs.
    Previously they generated thousands of issues during throttling incidents.
    """
    with (
        patch("supervisor.utils.sentry.sentry_sdk.is_initialized", return_value=True),
        patch("supervisor.utils.sentry.sentry_sdk.capture_exception") as mock_capture,
    ):
        capture_exception(exception)
        mock_capture.assert_not_called()


def test_capture_exception_skips_wrapped_rate_limit():
    """Test rate limit errors wrapped in another exception are also skipped.

    Callers like supervisor.update() wrap DockerHubRateLimitExceeded in
    SupervisorUpdateError. The filter must walk the __cause__ chain.
    """
    cause = DockerHubRateLimitExceeded()
    wrapped = SupervisorUpdateError("Update failed")
    wrapped.__cause__ = cause

    with (
        patch("supervisor.utils.sentry.sentry_sdk.is_initialized", return_value=True),
        patch("supervisor.utils.sentry.sentry_sdk.capture_exception") as mock_capture,
    ):
        capture_exception(wrapped)
        mock_capture.assert_not_called()


def test_capture_exception_sends_other_errors():
    """Test non-rate-limit errors are still sent to Sentry."""
    err = DockerError("something broke")

    with (
        patch("supervisor.utils.sentry.sentry_sdk.is_initialized", return_value=True),
        patch("supervisor.utils.sentry.sentry_sdk.capture_exception") as mock_capture,
    ):
        capture_exception(err)
        mock_capture.assert_called_once_with(err)


async def test_async_capture_exception_skips_rate_limits():
    """Test async variant also filters rate limits."""
    with (
        patch("supervisor.utils.sentry.sentry_sdk.is_initialized", return_value=True),
        patch("supervisor.utils.sentry.sentry_sdk.capture_exception") as mock_capture,
    ):
        await async_capture_exception(DockerHubRateLimitExceeded())
        mock_capture.assert_not_called()


async def test_async_capture_exception_sends_other_errors():
    """Test async variant still sends non-rate-limit errors."""
    err = DockerError("something broke")

    with (
        patch("supervisor.utils.sentry.sentry_sdk.is_initialized", return_value=True),
        patch("supervisor.utils.sentry.sentry_sdk.capture_exception") as mock_capture,
    ):
        await async_capture_exception(err)
        mock_capture.assert_called_once_with(err)
