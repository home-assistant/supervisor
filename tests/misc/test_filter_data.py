"""Test sentry data filter."""
import os
from unittest.mock import patch

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
    coresys.resolution.unsupported = UnsupportedReason.DOCKER_VERSION
    assert filter_data(coresys, SAMPLE_EVENT, {}) is None


def test_is_dev(coresys):
    """Test if dev."""
    coresys.config.diagnostics = True
    with patch("os.environ", return_value=[("ENV_SUPERVISOR_DEV", "1")]):
        assert filter_data(coresys, SAMPLE_EVENT, {}) is None


def test_not_started(coresys):
    """Test if supervisor not fully started."""
    coresys.config.diagnostics = True

    coresys.core.state = CoreState.INITIALIZE
    assert filter_data(coresys, SAMPLE_EVENT, {}) == SAMPLE_EVENT

    coresys.core.state = CoreState.SETUP
    assert filter_data(coresys, SAMPLE_EVENT, {}) == SAMPLE_EVENT


def test_defaults(coresys):
    """Test event defaults."""
    coresys.config.diagnostics = True

    coresys.core.state = CoreState.RUNNING
    with patch("shutil.disk_usage", return_value=(42, 42, 2 * (1024.0 ** 3))):
        filtered = filter_data(coresys, SAMPLE_EVENT, {})

    assert ["installation_type", "supervised"] in filtered["tags"]
    assert filtered["contexts"]["host"]["arch"] == "amd64"
    assert filtered["contexts"]["host"]["machine"] == "qemux86-64"
    assert filtered["contexts"]["versions"]["supervisor"] == SUPERVISOR_VERSION
    assert filtered["user"]["id"] == coresys.machine_id


def test_sanitize(coresys):
    """Test event sanitation."""
    event = {
        "tags": [["url", "https://mydomain.com"]],
        "request": {
            "url": "https://mydomain.com",
            "headers": [
                ["Host", "mydomain.com"],
                ["Referer", "https://mydomain.com/api/hassio_ingress/xxx-xxx/"],
                ["X-Forwarded-Host", "mydomain.com"],
                ["X-Hassio-Key", "xxx"],
            ],
        },
    }
    coresys.config.diagnostics = True

    coresys.core.state = CoreState.RUNNING
    with patch("shutil.disk_usage", return_value=(42, 42, 2 * (1024.0 ** 3))):
        filtered = filter_data(coresys, event, {})

    assert ["url", "https://example.com"] in filtered["tags"]

    assert filtered["request"]["url"] == "https://example.com"

    assert ["Host", "example.com"] in filtered["request"]["headers"]
    assert ["Referer", "https://example.com/api/hassio_ingress/xxx-xxx/"] in filtered[
        "request"
    ]["headers"]
    assert ["X-Forwarded-Host", "example.com"] in filtered["request"]["headers"]
    assert ["X-Hassio-Key", "XXXXXXXXXXXXXXXXXXX"] in filtered["request"]["headers"]


def test_issues_on_report(coresys):
    """Attach issue to report."""

    coresys.resolution.create_issue(IssueType.FATAL_ERROR, ContextType.SYSTEM)

    coresys.config.diagnostics = True
    coresys.core.state = CoreState.RUNNING

    with patch("shutil.disk_usage", return_value=(42, 42, 2 * (1024.0 ** 3))):
        event = filter_data(coresys, SAMPLE_EVENT, {})

    assert "issues" in event["contexts"]["resolution"]
    assert event["contexts"]["resolution"]["issues"][0]["type"] == IssueType.FATAL_ERROR
    assert event["contexts"]["resolution"]["issues"][0]["context"] == ContextType.SYSTEM


def test_suggestions_on_report(coresys):
    """Attach suggestion to report."""

    coresys.resolution.create_issue(
        IssueType.FATAL_ERROR,
        ContextType.SYSTEM,
        suggestions=[SuggestionType.EXECUTE_RELOAD],
    )

    coresys.config.diagnostics = True
    coresys.core.state = CoreState.RUNNING

    with patch("shutil.disk_usage", return_value=(42, 42, 2 * (1024.0 ** 3))):
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


def test_unhealthy_on_report(coresys):
    """Attach unhealthy to report."""

    coresys.config.diagnostics = True
    coresys.core.state = CoreState.RUNNING
    coresys.resolution.unhealthy = UnhealthyReason.DOCKER

    with patch("shutil.disk_usage", return_value=(42, 42, 2 * (1024.0 ** 3))):
        event = filter_data(coresys, SAMPLE_EVENT, {})

    assert "issues" in event["contexts"]["resolution"]
    assert event["contexts"]["resolution"]["unhealthy"][-1] == UnhealthyReason.DOCKER


def test_images_report(coresys):
    """Attach image to report."""

    coresys.config.diagnostics = True
    coresys.core.state = CoreState.RUNNING
    coresys.resolution.evaluate.cached_images.add("my/test:image")

    with patch("shutil.disk_usage", return_value=(42, 42, 2 * (1024.0 ** 3))):
        event = filter_data(coresys, SAMPLE_EVENT, {})

    assert "issues" in event["contexts"]["resolution"]
    assert event["contexts"]["host"]["images"] == ["my/test:image"]
