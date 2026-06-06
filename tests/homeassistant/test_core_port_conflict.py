"""Tests for Home Assistant core port conflict handling."""

# pylint: disable=protected-access

from unittest.mock import AsyncMock, Mock, patch

import pytest

from supervisor.const import AppState
from supervisor.exceptions import AppsError
from supervisor.homeassistant.core import ComponentType, PortConflict

from tests.common import force_app_state


@pytest.mark.parametrize("app_state", [AppState.STOPPED, AppState.ERROR])
async def test_set_port_conflict_app_not_running_creates_issue_only(
    coresys, install_app_ssh, app_state: AppState
):
    """Test app conflicts create issue but do not stop or abort if app is not running."""
    app = install_app_ssh
    force_app_state(app, app_state)
    app.create_port_conflict_issue = Mock()
    app.stop = AsyncMock()

    core = coresys.homeassistant.core
    core._startup_abort = AsyncMock()

    conflict = PortConflict(
        port=coresys.homeassistant.api_port,
        component_type=ComponentType.APP,
        component=app,
    )

    await core.set_port_conflict(conflict)

    app.create_port_conflict_issue.assert_called_once_with(conflict.port, source="core")
    app.stop.assert_not_called()
    core._startup_abort.set.assert_not_called()


@pytest.mark.parametrize("app_state", [AppState.STARTUP, AppState.STARTED])
async def test_set_port_conflict_app_running_stops_without_abort_on_success(
    coresys, install_app_ssh, app_state: AppState
):
    """Test running app conflicts are resolved by stopping app when possible."""
    app = install_app_ssh
    force_app_state(app, app_state)
    app.create_port_conflict_issue = Mock()
    app.stop = AsyncMock()

    core = coresys.homeassistant.core
    core._startup_abort = AsyncMock()

    conflict = PortConflict(
        port=coresys.homeassistant.api_port,
        component_type=ComponentType.APP,
        component=app,
    )

    await core.set_port_conflict(conflict)

    app.create_port_conflict_issue.assert_called_once_with(conflict.port, source="core")
    app.stop.assert_awaited_once()
    core._startup_abort.set.assert_not_called()


@pytest.mark.parametrize("app_state", [AppState.STARTUP, AppState.STARTED])
async def test_set_port_conflict_app_running_aborts_on_stop_failure(
    coresys, install_app_ssh, app_state: AppState
):
    """Test running app conflicts abort startup if stop fails while waiting."""
    app = install_app_ssh
    force_app_state(app, app_state)
    app.create_port_conflict_issue = Mock()
    app.stop = AsyncMock(side_effect=AppsError())

    core = coresys.homeassistant.core
    core._startup_abort = AsyncMock()

    conflict = PortConflict(
        port=coresys.homeassistant.api_port,
        component_type=ComponentType.APP,
        component=app,
    )

    await core.set_port_conflict(conflict)

    app.create_port_conflict_issue.assert_called_once_with(conflict.port, source="core")
    app.stop.assert_awaited_once()
    core._startup_abort.set.assert_called_once()


async def test_set_port_conflict_non_app_aborts_startup(coresys):
    """Test non-app conflicts abort startup if Supervisor is waiting."""
    core = coresys.homeassistant.core
    core._startup_abort = AsyncMock()

    conflict = PortConflict(
        port=coresys.homeassistant.api_port,
        component_type=ComponentType.UNKNOWN,
        component="other-container",
    )

    await core.set_port_conflict(conflict)

    core._startup_abort.set.assert_called_once()


async def test_set_port_conflict_non_app_no_abort_event(coresys):
    """Test non-app conflicts do not fail when no startup wait is active."""
    core = coresys.homeassistant.core
    core._startup_abort = None

    conflict = PortConflict(
        port=coresys.homeassistant.api_port,
        component_type=ComponentType.UNKNOWN,
        component="other-container",
    )

    with patch("supervisor.homeassistant.core._LOGGER.error") as logger_error:
        await core.set_port_conflict(conflict)

    logger_error.assert_called()
