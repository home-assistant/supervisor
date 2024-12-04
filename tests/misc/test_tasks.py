"""Test scheduled tasks."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from shutil import copy
from unittest.mock import AsyncMock, MagicMock, Mock, PropertyMock, patch

from awesomeversion import AwesomeVersion
import pytest

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.exceptions import HomeAssistantError
from supervisor.homeassistant.api import HomeAssistantAPI
from supervisor.homeassistant.const import LANDINGPAGE
from supervisor.homeassistant.core import HomeAssistantCore
from supervisor.misc.tasks import Tasks
from supervisor.supervisor import Supervisor

from tests.common import get_fixture_path, load_fixture

# pylint: disable=protected-access


@pytest.fixture(name="tasks")
async def fixture_tasks(
    coresys: CoreSys, container: MagicMock
) -> AsyncGenerator[Tasks]:
    """Return task manager."""
    coresys.homeassistant.watchdog = True
    coresys.homeassistant.version = AwesomeVersion("2023.12.0")
    container.status = "running"
    yield Tasks(coresys)


async def test_watchdog_homeassistant_api(
    tasks: Tasks, caplog: pytest.LogCaptureFixture
):
    """Test watchdog of homeassistant api."""
    with (
        patch.object(HomeAssistantAPI, "check_api_state", return_value=False),
        patch.object(HomeAssistantCore, "restart") as restart,
    ):
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
            "Watchdog missed 2 Home Assistant Core API responses in a row. Restarting Home Assistant Core!"
            in caplog.text
        )


async def test_watchdog_homeassistant_api_off(tasks: Tasks, coresys: CoreSys):
    """Test watchdog of homeassistant api does not run when disabled."""
    coresys.homeassistant.watchdog = False

    with (
        patch.object(HomeAssistantAPI, "check_api_state", return_value=False),
        patch.object(HomeAssistantCore, "restart") as restart,
    ):
        await tasks._watchdog_homeassistant_api()
        await tasks._watchdog_homeassistant_api()
        restart.assert_not_called()


async def test_watchdog_homeassistant_api_error_state(tasks: Tasks, coresys: CoreSys):
    """Test watchdog of homeassistant api does not restart when in error state."""
    coresys.homeassistant.core._error_state = True

    with (
        patch.object(HomeAssistantAPI, "check_api_state", return_value=False),
        patch.object(HomeAssistantCore, "restart") as restart,
    ):
        await tasks._watchdog_homeassistant_api()
        await tasks._watchdog_homeassistant_api()
        restart.assert_not_called()


async def test_watchdog_homeassistant_api_landing_page(tasks: Tasks, coresys: CoreSys):
    """Test watchdog of homeassistant api does not monitor landing page."""
    coresys.homeassistant.version = LANDINGPAGE

    with (
        patch.object(HomeAssistantAPI, "check_api_state", return_value=False),
        patch.object(HomeAssistantCore, "restart") as restart,
    ):
        await tasks._watchdog_homeassistant_api()
        await tasks._watchdog_homeassistant_api()
        restart.assert_not_called()


async def test_watchdog_homeassistant_api_not_running(
    tasks: Tasks, container: MagicMock
):
    """Test watchdog of homeassistant api does not monitor when home assistant not running."""
    container.status = "stopped"

    with (
        patch.object(HomeAssistantAPI, "check_api_state", return_value=False),
        patch.object(HomeAssistantCore, "restart") as restart,
    ):
        await tasks._watchdog_homeassistant_api()
        await tasks._watchdog_homeassistant_api()
        restart.assert_not_called()


async def test_watchdog_homeassistant_api_reanimation_limit(
    tasks: Tasks, caplog: pytest.LogCaptureFixture, capture_exception: Mock
):
    """Test watchdog of homeassistant api stops after max reanimation failures."""
    with (
        patch.object(HomeAssistantAPI, "check_api_state", return_value=False),
        patch.object(
            HomeAssistantCore, "restart", side_effect=(err := HomeAssistantError())
        ) as restart,
        patch.object(HomeAssistantCore, "rebuild", side_effect=err) as rebuild,
    ):
        for _ in range(5):
            await tasks._watchdog_homeassistant_api()
            restart.assert_not_called()

            await tasks._watchdog_homeassistant_api()
            restart.assert_called_once_with()
            assert "Home Assistant watchdog reanimation failed!" in caplog.text

            rebuild.assert_not_called()
            restart.reset_mock()

        capture_exception.assert_called_once_with(err)

        # Next time it should try safe mode
        caplog.clear()
        await tasks._watchdog_homeassistant_api()
        rebuild.assert_not_called()

        await tasks._watchdog_homeassistant_api()

        rebuild.assert_called_once_with(safe_mode=True)
        restart.assert_not_called()
        assert (
            "Watchdog cannot reanimate Home Assistant Core, failed all 5 attempts. Restarting into safe mode"
            in caplog.text
        )
        assert (
            "Safe mode restart failed. Watchdog cannot bring Home Assistant online."
            in caplog.text
        )

        # After safe mode has failed too, no more restart attempts
        rebuild.reset_mock()
        caplog.clear()
        await tasks._watchdog_homeassistant_api()
        assert "Watchdog missed an Home Assistant Core API response." in caplog.text

        caplog.clear()
        await tasks._watchdog_homeassistant_api()
        assert not caplog.text
        restart.assert_not_called()
        rebuild.assert_not_called()


async def test_reload_updater_triggers_supervisor_update(
    tasks: Tasks, coresys: CoreSys
):
    """Test an updater reload triggers a supervisor update if there is one."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    coresys.core.state = CoreState.RUNNING
    coresys.security.content_trust = False

    version_data = load_fixture("version_stable.json")
    version_resp = AsyncMock()
    version_resp.status = 200
    version_resp.read.return_value = version_data

    @asynccontextmanager
    async def mock_get_for_version(*args, **kwargs) -> AsyncGenerator[AsyncMock]:
        """Mock get call for version information."""
        yield version_resp

    with (
        patch("supervisor.coresys.aiohttp.ClientSession.get", new=mock_get_for_version),
        patch.object(
            Supervisor,
            "version",
            new=PropertyMock(return_value=AwesomeVersion("2024.10.0")),
        ),
        patch.object(Supervisor, "update") as update,
    ):
        # Set supervisor's version intially
        await coresys.updater.reload()
        assert coresys.supervisor.latest_version == AwesomeVersion("2024.10.0")

        # No change in version means no update
        await tasks._reload_updater()
        update.assert_not_called()

        # Version change causes an update
        version_resp.read.return_value = version_data.replace("2024.10.0", "2024.10.1")
        await tasks._reload_updater()
        update.assert_called_once()


@pytest.mark.usefixtures("path_extern")
async def test_core_backup_cleanup(
    tasks: Tasks, coresys: CoreSys, tmp_supervisor_data: Path
):
    """Test core backup task cleans up old backup files."""
    coresys.core.state = CoreState.RUNNING
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    # Put an old and new backup in folder
    copy(get_fixture_path("backup_example.tar"), coresys.config.path_core_backup)
    await coresys.backups.reload(
        location=".cloud_backup", filename="backup_example.tar"
    )
    assert (old_backup := coresys.backups.get("7fed74c8"))
    new_backup = await coresys.backups.do_backup_partial(
        name="test", folders=["ssl"], location=".cloud_backup"
    )

    old_tar = old_backup.tarfile
    new_tar = new_backup.tarfile
    # pylint: disable-next=protected-access
    await tasks._core_backup_cleanup()

    assert coresys.backups.get(new_backup.slug)
    assert not coresys.backups.get("7fed74c8")
    assert new_tar.exists()
    assert not old_tar.exists()
