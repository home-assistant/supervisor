"""Test sentry data filter."""

import os
from unittest.mock import patch

from awesomeversion import AwesomeVersion
import pytest

from supervisor.const import SUPERVISOR_VERSION, CoreState
from supervisor.exceptions import AddonConfigurationError
from supervisor.misc.filter import filter_data
from supervisor.resolution.const import (
    ContextType,
    IssueType,
    SuggestionType,
    UnhealthyReason,
    UnsupportedReason,
)

SAMPLE_EVENT = {"sample": "event", "extra": {"Test": "123"}}
SAMPLE_EVENT_AIOHTTP_INTERNAL = {
    "level": "error",
    "request": {
        "url": "http://172.30.32.2/supervisor/options",
        "query_string": "",
        "method": "POST",
        "env": {"REMOTE_ADDR": "172.30.32.1"},
        "headers": {
            "Host": "172.30.32.2",
            "User-Agent": "HomeAssistant/2025.3.0.dev202501310226 aiohttp/3.11.11 Python/3.13",
            "Authorization": "[Filtered]",
            "X-Hass-Source": "core.handler",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Length": "20",
            "Content-Type": "application/json",
        },
        "data": '{"diagnostics":true}',
    },
    "platform": "python",
}
SAMPLE_EVENT_AIOHTTP_EXTERNAL = {
    "level": "error",
    "request": {
        "url": "http://debian-supervised-dev.lan:8123/ingress/SRtKwGqE15nF6jbzGCjkM7Nn3_uQlZ08RrJLzLJJQKc/ws",
        "query_string": "",
        "method": "GET",
        "env": {"REMOTE_ADDR": "172.30.32.1"},
        "headers": {
            "Host": "debian-supervised-dev.lan:8123",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:135.0) Gecko/20100101 Firefox/135.0",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Origin": "http://debian-supervised-dev.lan:8123",
            "Connection": "keep-alive, Upgrade",
            "Cookie": "[Filtered]",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "Upgrade": "websocket",
            "X-Hass-Source": "core.ingress",
            "X-Ingress-Path": "/api/hassio_ingress/SRtKwGqE15nF6jbzGCjkM7Nn3_uQlZ08RrJLzLJJQKc",
            "X-Forwarded-For": "",
            "X-Forwarded-Host": "debian-supervised-dev.lan:8123",
            "X-Forwarded-Proto": "http",
            "Sec-WebSocket-Version": "13",
            "Sec-WebSocket-Key": "BD239eBT8pDIxStE6QO+Qw==",
            "Sec-WebSocket-Protocol": "tty",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "http://debian-supervised-dev.lan:8123/somehwere",
        },
        "data": None,
    },
    "platform": "python",
}


@pytest.fixture
def sys_env(autouse=True):
    """Fixture to inject hassio env."""
    with patch.dict(os.environ, {"Test": "123"}):
        yield


def test_ignored_exception(coresys):
    """Test ignored exceptions."""
    hint = {"exc_info": (None, AddonConfigurationError(), None)}
    assert filter_data(coresys, SAMPLE_EVENT, hint) is None


def test_diagnostics_disabled(coresys):
    """Test if diagnostics is disabled."""
    coresys.config.diagnostics = False
    assert filter_data(coresys, SAMPLE_EVENT, {}) is None


def test_not_supported(coresys):
    """Test if not supported."""
    coresys.config.diagnostics = True
    coresys.resolution.add_unsupported_reason(UnsupportedReason.DOCKER_VERSION)
    assert filter_data(coresys, SAMPLE_EVENT, {}) is None


def test_is_dev(coresys):
    """Test if dev."""
    coresys.config.diagnostics = True
    with patch.dict(os.environ, {"SUPERVISOR_DEV": "1"}):
        assert filter_data(coresys, SAMPLE_EVENT, {}) is None


async def test_not_started(coresys):
    """Test if supervisor not fully started."""
    coresys.config.diagnostics = True

    await coresys.core.set_state(CoreState.INITIALIZE)
    assert filter_data(coresys, SAMPLE_EVENT, {}) == SAMPLE_EVENT

    await coresys.core.set_state(CoreState.SETUP)
    assert filter_data(coresys, SAMPLE_EVENT, {}) == SAMPLE_EVENT


async def test_defaults(coresys):
    """Test event defaults."""
    coresys.config.diagnostics = True

    await coresys.core.set_state(CoreState.RUNNING)
    with patch("shutil.disk_usage", return_value=(42, 42, 2 * (1024.0**3))):
        filtered = filter_data(coresys, SAMPLE_EVENT, {})

    assert filtered["tags"]["installation_type"] == "supervised"
    assert filtered["contexts"]["host"]["arch"] == "amd64"
    assert filtered["contexts"]["host"]["machine"] == "qemux86-64"
    assert filtered["contexts"]["versions"]["supervisor"] == AwesomeVersion(
        SUPERVISOR_VERSION
    )
    assert filtered["user"]["id"] == coresys.machine_id


async def test_sanitize_user_hostname(coresys):
    """Test user hostname event sanitation."""
    event = SAMPLE_EVENT_AIOHTTP_EXTERNAL
    coresys.config.diagnostics = True

    await coresys.core.set_state(CoreState.RUNNING)
    with patch("shutil.disk_usage", return_value=(42, 42, 2 * (1024.0**3))):
        filtered = filter_data(coresys, event, {})

    assert "debian-supervised-dev.lan" not in filtered["request"]["url"]

    assert "debian-supervised-dev.lan" not in filtered["request"]["headers"]["Host"]
    assert "debian-supervised-dev.lan" not in filtered["request"]["headers"]["Referer"]
    assert (
        "debian-supervised-dev.lan"
        not in filtered["request"]["headers"]["X-Forwarded-Host"]
    )


async def test_sanitize_internal(coresys):
    """Test internal event sanitation."""
    event = SAMPLE_EVENT_AIOHTTP_INTERNAL
    coresys.config.diagnostics = True

    await coresys.core.set_state(CoreState.RUNNING)
    with patch("shutil.disk_usage", return_value=(42, 42, 2 * (1024.0**3))):
        filtered = filter_data(coresys, event, {})

    assert filtered == event


async def test_issues_on_report(coresys):
    """Attach issue to report."""

    coresys.resolution.create_issue(IssueType.FATAL_ERROR, ContextType.SYSTEM)

    coresys.config.diagnostics = True
    await coresys.core.set_state(CoreState.RUNNING)

    with patch("shutil.disk_usage", return_value=(42, 42, 2 * (1024.0**3))):
        event = filter_data(coresys, SAMPLE_EVENT, {})

    assert "issues" in event["contexts"]["resolution"]
    assert event["contexts"]["resolution"]["issues"][0]["type"] == IssueType.FATAL_ERROR
    assert event["contexts"]["resolution"]["issues"][0]["context"] == ContextType.SYSTEM


async def test_suggestions_on_report(coresys):
    """Attach suggestion to report."""

    coresys.resolution.create_issue(
        IssueType.FATAL_ERROR,
        ContextType.SYSTEM,
        suggestions=[SuggestionType.EXECUTE_RELOAD],
    )

    coresys.config.diagnostics = True
    await coresys.core.set_state(CoreState.RUNNING)

    with patch("shutil.disk_usage", return_value=(42, 42, 2 * (1024.0**3))):
        event = filter_data(coresys, SAMPLE_EVENT, {})

    assert "issues" in event["contexts"]["resolution"]
    assert event["contexts"]["resolution"]["issues"][0]["type"] == IssueType.FATAL_ERROR
    assert event["contexts"]["resolution"]["issues"][0]["context"] == ContextType.SYSTEM
    assert (
        event["contexts"]["resolution"]["suggestions"][0]["type"]
        == SuggestionType.EXECUTE_RELOAD
    )
    assert (
        event["contexts"]["resolution"]["suggestions"][0]["context"]
        == ContextType.SYSTEM
    )


async def test_unhealthy_on_report(coresys):
    """Attach unhealthy to report."""

    coresys.config.diagnostics = True
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.resolution.add_unhealthy_reason(UnhealthyReason.DOCKER)

    with patch("shutil.disk_usage", return_value=(42, 42, 2 * (1024.0**3))):
        event = filter_data(coresys, SAMPLE_EVENT, {})

    assert "issues" in event["contexts"]["resolution"]
    assert event["contexts"]["resolution"]["unhealthy"][-1] == UnhealthyReason.DOCKER


async def test_images_report(coresys):
    """Attach image to report."""

    coresys.config.diagnostics = True
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.resolution.evaluate.cached_images.add("my/test:image")

    with patch("shutil.disk_usage", return_value=(42, 42, 2 * (1024.0**3))):
        event = filter_data(coresys, SAMPLE_EVENT, {})

    assert "issues" in event["contexts"]["resolution"]
    assert event["contexts"]["host"]["images"] == ["my/test:image"]
