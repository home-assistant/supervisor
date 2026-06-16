"""Test scheduled tasks."""

import asyncio
from collections.abc import AsyncGenerator
from shutil import copy
from unittest.mock import AsyncMock, Mock, PropertyMock, patch

from aiodocker.containers import DockerContainer
from awesomeversion import AwesomeVersion
import pytest

from supervisor.apps.app import App
from supervisor.const import ATTR_VERSION_TIMESTAMP, CoreState
from supervisor.coresys import CoreSys
from supervisor.exceptions import HomeAssistantError
from supervisor.homeassistant.api import HomeAssistantAPI
from supervisor.homeassistant.const import LANDINGPAGE
from supervisor.homeassistant.core import HomeAssistantCore
from supervisor.misc.tasks import Tasks
from supervisor.plugins.dns import PluginDns
from supervisor.supervisor import Supervisor

from tests.common import MockResponse, get_fixture_path

# pylint: disable=protected-access


@pytest.fixture(name="tasks")
async def fixture_tasks(
    coresys: CoreSys, container: DockerContainer
) -> AsyncGenerator[Tasks]:
    """Return task manager."""
    coresys.homeassistant.watchdog = True
    coresys.homeassistant.version = AwesomeVersion("2023.12.0")
    container.show.return_value["State"]["Status"] = "running"
    container.show.return_value["State"]["Running"] = True
    return Tasks(coresys)


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
    tasks: Tasks, container: DockerContainer
):
    """Test watchdog of homeassistant api does not monitor when home assistant not running."""
    container.show.return_value["State"]["Status"] = "stopped"
    container.show.return_value["State"]["Running"] = False

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


@pytest.mark.usefixtures("no_job_throttle", "supervisor_internet")
async def test_reload_updater_triggers_supervisor_update(
    tasks: Tasks, coresys: CoreSys, mock_update_data: MockResponse
):
    """Test an updater reload triggers a supervisor update if there is one."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    await coresys.core.set_state(CoreState.RUNNING)

    with (
        patch.object(
            Supervisor,
            "version",
            new=PropertyMock(return_value=AwesomeVersion("2024.10.0")),
        ),
        patch.object(Supervisor, "update") as update,
    ):
        # Set supervisor's version initially
        await coresys.updater.reload()
        assert coresys.supervisor.latest_version == AwesomeVersion("2024.10.0")

        # No change in version means no update
        await tasks._reload_updater()
        update.assert_not_called()

        # Version change causes an update
        version_data = await mock_update_data.text()
        mock_update_data.update_text(version_data.replace("2024.10.0", "2024.10.1"))
        await tasks._reload_updater()
        update.assert_called_once()


@pytest.mark.usefixtures("path_extern", "tmp_supervisor_data")
async def test_core_backup_cleanup(tasks: Tasks, coresys: CoreSys):
    """Test core backup task cleans up old backup files."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    # Put an old and new backup in folder
    copy(get_fixture_path("backup_example.tar"), coresys.config.path_core_backup)
    await coresys.backups.reload()
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


@pytest.mark.usefixtures("no_job_throttle")
async def test_update_dns_skipped_when_auto_update_disabled(
    tasks: Tasks, coresys: CoreSys
):
    """Test plugin auto-update task is skipped when auto update is disabled."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    coresys.updater.auto_update = False

    with patch.object(PluginDns, "update") as update:
        await tasks._update_dns()
        update.assert_not_called()


@pytest.mark.usefixtures("no_job_throttle", "supervisor_internet")
async def test_scheduled_reload_updater_triggers_one_supervisor_update(
    tasks: Tasks, coresys: CoreSys, mock_update_data: MockResponse
):
    """Test scheduled reload updater triggers exactly one supervisor update.

    Regression test: previously _update_supervisor ran on a separate schedule
    in addition to being called from _reload_updater, causing duplicate updates.
    Now only _reload_updater triggers the supervisor auto-update.
    """
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    await coresys.core.set_state(CoreState.RUNNING)

    # Make version data show a newer supervisor version
    version_data = await mock_update_data.text()
    mock_update_data.update_text(version_data.replace("2024.10.0", "2024.10.1"))

    with (
        patch.object(
            Supervisor,
            "version",
            new=PropertyMock(return_value=AwesomeVersion("2024.10.0")),
        ),
        patch.object(Supervisor, "update") as update,
    ):
        await tasks.load()
        update.assert_not_called()

        # Advance the event loop clock by 24h+ so scheduled tasks fire.
        # Patching loop.time makes all call_later callbacks appear due;
        # a tiny real sleep lets _run_once re-evaluate and execute them.
        loop = asyncio.get_event_loop()
        original_time = loop.time
        loop.time = lambda: original_time() + 86401

        try:
            # Busy-wait until call_later callbacks fire and create jobs
            while not any(t.job and not t.job.done() for t in coresys.scheduler._tasks):
                await asyncio.sleep(0)

            # Wait for all scheduler-created tasks to finish
            pending = [
                t.job for t in coresys.scheduler._tasks if t.job and not t.job.done()
            ]
            await asyncio.gather(*pending)

            # Verify update was triggered exactly once
            update.assert_called_once()
        finally:
            loop.time = original_time

    await coresys.scheduler.shutdown()


@pytest.mark.usefixtures("tmp_supervisor_data")
async def test_update_apps_auto_update_success(
    tasks: Tasks,
    coresys: CoreSys,
    ha_ws_client: AsyncMock,
    install_app_example: App,
):
    """Test that an eligible app is auto-updated via websocket command."""
    await coresys.core.set_state(CoreState.RUNNING)

    # Set up the app as eligible for auto-update
    install_app_example.auto_update = True
    install_app_example.data_store[ATTR_VERSION_TIMESTAMP] = 0
    with patch.object(
        App, "version", new=PropertyMock(return_value=AwesomeVersion("1.0"))
    ):
        assert install_app_example.need_update is True
        assert install_app_example.auto_update_available is True

        # Make sure all job events from installing the app are cleared
        ha_ws_client.async_send_command.reset_mock()

        # pylint: disable-next=protected-access
        await tasks._update_apps()

        ha_ws_client.async_send_command.assert_any_call(
            {
                "type": "hassio/update/addon",
                "addon": install_app_example.slug,
                "backup": True,
            }
        )
