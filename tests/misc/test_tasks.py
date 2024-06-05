"""Test scheduled tasks."""

from unittest.mock import MagicMock, Mock, patch

from awesomeversion import AwesomeVersion
import pytest

from supervisor.coresys import CoreSys
from supervisor.exceptions import HomeAssistantError
from supervisor.homeassistant.api import HomeAssistantAPI
from supervisor.homeassistant.const import LANDINGPAGE
from supervisor.homeassistant.core import HomeAssistantCore
from supervisor.misc.tasks import Tasks

# pylint: disable=protected-access


@pytest.fixture(name="tasks")
async def fixture_tasks(coresys: CoreSys, container: MagicMock) -> Tasks:
    """Return task manager."""
    coresys.homeassistant.watchdog = True
    coresys.homeassistant.version = AwesomeVersion("2023.12.0")
    container.status = "running"
    yield Tasks(coresys)


async def test_watchdog_homeassistant_api(
    tasks: Tasks, caplog: pytest.LogCaptureFixture
):
    """Test watchdog of homeassistant api."""
    with patch.object(
        HomeAssistantAPI, "check_api_state", return_value=False
    ), patch.object(HomeAssistantCore, "restart") as restart:
        await tasks._watchdog_homeassistant_api()

        restart.assert_not_called()
        assert "Watchdog missed an Home Assistant Core API response." in caplog.text
        assert (
            "Watchdog missed 2 Home Assistant Core API responses in a row. Restarting Home Assistant Core API!"
            not in caplog.text
        )

        caplog.clear()
        await tasks._watchdog_homeassistant_api()

        restart.assert_called_once()
        assert "Watchdog missed an Home Assistant Core API response." not in caplog.text
        assert (
            "Watchdog missed 2 Home Assistant Core API responses in a row. Restarting Home Assistant Core API!"
            in caplog.text
        )


async def test_watchdog_homeassistant_api_off(tasks: Tasks, coresys: CoreSys):
    """Test watchdog of homeassistant api does not run when disabled."""
    coresys.homeassistant.watchdog = False

    with patch.object(
        HomeAssistantAPI, "check_api_state", return_value=False
    ), patch.object(HomeAssistantCore, "restart") as restart:
        await tasks._watchdog_homeassistant_api()
        await tasks._watchdog_homeassistant_api()
        restart.assert_not_called()


async def test_watchdog_homeassistant_api_error_state(tasks: Tasks, coresys: CoreSys):
    """Test watchdog of homeassistant api does not restart when in error state."""
    coresys.homeassistant.core._error_state = True

    with patch.object(
        HomeAssistantAPI, "check_api_state", return_value=False
    ), patch.object(HomeAssistantCore, "restart") as restart:
        await tasks._watchdog_homeassistant_api()
        await tasks._watchdog_homeassistant_api()
        restart.assert_not_called()


async def test_watchdog_homeassistant_api_landing_page(tasks: Tasks, coresys: CoreSys):
    """Test watchdog of homeassistant api does not monitor landing page."""
    coresys.homeassistant.version = LANDINGPAGE

    with patch.object(
        HomeAssistantAPI, "check_api_state", return_value=False
    ), patch.object(HomeAssistantCore, "restart") as restart:
        await tasks._watchdog_homeassistant_api()
        await tasks._watchdog_homeassistant_api()
        restart.assert_not_called()


async def test_watchdog_homeassistant_api_not_running(
    tasks: Tasks, container: MagicMock
):
    """Test watchdog of homeassistant api does not monitor when home assistant not running."""
    container.status = "stopped"

    with patch.object(
        HomeAssistantAPI, "check_api_state", return_value=False
    ), patch.object(HomeAssistantCore, "restart") as restart:
        await tasks._watchdog_homeassistant_api()
        await tasks._watchdog_homeassistant_api()
        restart.assert_not_called()


async def test_watchdog_homeassistant_api_reanimation_limit(
    tasks: Tasks, caplog: pytest.LogCaptureFixture, capture_exception: Mock
):
    """Test watchdog of homeassistant api stops after max reanimation failures."""
    with patch.object(
        HomeAssistantAPI, "check_api_state", return_value=False
    ), patch.object(
        HomeAssistantCore, "restart", side_effect=(err := HomeAssistantError())
    ) as restart:
        for _ in range(5):
            await tasks._watchdog_homeassistant_api()
            restart.assert_not_called()

            await tasks._watchdog_homeassistant_api()
            restart.assert_called_once_with(safe_mode=False)
            assert "Home Assistant watchdog reanimation failed!" in caplog.text

            restart.reset_mock()

        capture_exception.assert_called_once_with(err)

        # Next time it should try safe mode
        caplog.clear()
        await tasks._watchdog_homeassistant_api()
        restart.assert_not_called()

        await tasks._watchdog_homeassistant_api()
        restart.assert_called_once_with(safe_mode=True)

        restart.assert_called_once_with(safe_mode=True)
        assert (
            "Watchdog cannot reanimate Home Assistant Core, failed all 5 attempts. Restarting into safe mode"
            in caplog.text
        )
        assert (
            "Safe mode restart failed. Watchdog cannot bring Home Assistant online."
            in caplog.text
        )

        # After safe mode has failed too, no more restart attempts
        restart.reset_mock()
        caplog.clear()
        await tasks._watchdog_homeassistant_api()
        restart.assert_not_called()
        assert not caplog.text
