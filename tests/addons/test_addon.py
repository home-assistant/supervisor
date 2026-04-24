"""Test Home Assistant Apps."""

import asyncio
from datetime import timedelta
import errno
from http import HTTPStatus
from pathlib import Path, PurePath
from typing import Any
from unittest.mock import MagicMock, PropertyMock, call, patch

import aiodocker
from aiodocker.containers import DockerContainer
from awesomeversion import AwesomeVersion
import pytest
from securetar import SecureTarArchive, SecureTarFile

from supervisor.addons.addon import App
from supervisor.addons.const import AppBackupMode
from supervisor.addons.model import AppModel
from supervisor.config import CoreConfig
from supervisor.const import ATTR_ADVANCED, AppBoot, AppState, BusEvent
from supervisor.coresys import CoreSys
from supervisor.docker.addon import DockerApp
from supervisor.docker.const import ContainerState
from supervisor.docker.manager import CommandReturn, DockerAPI
from supervisor.docker.monitor import DockerContainerStateEvent
from supervisor.exceptions import (
    AppPortConflict,
    AppPrePostBackupCommandReturnedError,
    AppsJobError,
    AppUnknownError,
    AudioUpdateError,
    DockerRegistryAuthError,
    HassioError,
)
from supervisor.hardware.helper import HwHelper
from supervisor.ingress import Ingress
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue
from supervisor.utils.dt import utcnow

from .test_manager import BOOT_FAIL_ISSUE, BOOT_FAIL_SUGGESTIONS

from tests.common import get_fixture_path, is_in_list
from tests.const import TEST_ADDON_SLUG


def _fire_test_event(coresys: CoreSys, name: str, state: ContainerState):
    """Fire a test event."""
    coresys.bus.fire_event(
        BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
        DockerContainerStateEvent(
            name=name,
            state=state,
            id="abc123",
            time=1,
        ),
    )


def test_options_merge(coresys: CoreSys, install_app_ssh: App) -> None:
    """Test options merge."""
    app = coresys.apps.get(TEST_ADDON_SLUG)

    assert app.options == {
        "apks": [],
        "authorized_keys": [],
        "password": "",
        "server": {"tcp_forwarding": False},
    }

    app.options = {"password": "test"}
    assert app.persist["options"] == {"password": "test"}
    assert app.options == {
        "apks": [],
        "authorized_keys": [],
        "password": "test",
        "server": {"tcp_forwarding": False},
    }

    app.options = {"password": "test", "apks": ["gcc"]}
    assert app.persist["options"] == {"password": "test", "apks": ["gcc"]}
    assert app.options == {
        "apks": ["gcc"],
        "authorized_keys": [],
        "password": "test",
        "server": {"tcp_forwarding": False},
    }

    app.options = {"password": "test", "server": {"tcp_forwarding": True}}
    assert app.persist["options"] == {
        "password": "test",
        "server": {"tcp_forwarding": True},
    }
    assert app.options == {
        "apks": [],
        "authorized_keys": [],
        "password": "test",
        "server": {"tcp_forwarding": True},
    }

    # Test overwrite
    test = app.options
    test["server"]["test"] = 1
    assert app.options == {
        "apks": [],
        "authorized_keys": [],
        "password": "test",
        "server": {"tcp_forwarding": True},
    }
    app.options = {"password": "test", "server": {"tcp_forwarding": True}}


async def test_app_state_listener(coresys: CoreSys, install_app_ssh: App) -> None:
    """Test app is setting state from docker events."""
    with patch.object(DockerApp, "attach"):
        await install_app_ssh.load()

    assert install_app_ssh.state == AppState.UNKNOWN

    with patch.object(App, "watchdog_container"):
        _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", ContainerState.RUNNING)
        await asyncio.sleep(0)
        assert install_app_ssh.state == AppState.STARTED

        _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", ContainerState.STOPPED)
        await asyncio.sleep(0)
        assert install_app_ssh.state == AppState.STOPPED

        _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", ContainerState.HEALTHY)
        await asyncio.sleep(0)
        assert install_app_ssh.state == AppState.STARTED

        _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", ContainerState.FAILED)
        await asyncio.sleep(0)
        assert install_app_ssh.state == AppState.ERROR

        # Test other apps are ignored
        _fire_test_event(coresys, "addon_local_non_installed", ContainerState.RUNNING)
        await asyncio.sleep(0)
        assert install_app_ssh.state == AppState.ERROR


async def test_app_watchdog(coresys: CoreSys, install_app_ssh: App) -> None:
    """Test app watchdog works correctly."""
    with patch.object(DockerApp, "attach"):
        await install_app_ssh.load()

    install_app_ssh.watchdog = True
    install_app_ssh._manual_stop = False  # pylint: disable=protected-access

    with (
        patch.object(App, "restart") as restart,
        patch.object(App, "start") as start,
        patch.object(DockerApp, "current_state") as current_state,
    ):
        # Restart if it becomes unhealthy
        current_state.return_value = ContainerState.UNHEALTHY
        _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", ContainerState.UNHEALTHY)
        await asyncio.sleep(0)
        restart.assert_called_once()
        start.assert_not_called()

        restart.reset_mock()

        # Rebuild if it failed
        current_state.return_value = ContainerState.FAILED
        with patch.object(DockerApp, "stop") as stop:
            _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", ContainerState.FAILED)
            await asyncio.sleep(0)
            stop.assert_called_once_with(remove_container=True)
            restart.assert_not_called()
            start.assert_called_once()

        start.reset_mock()

        # Do not process event if container state has changed since fired
        current_state.return_value = ContainerState.HEALTHY
        _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", ContainerState.FAILED)
        await asyncio.sleep(0)
        restart.assert_not_called()
        start.assert_not_called()

        # Other apps ignored
        current_state.return_value = ContainerState.UNHEALTHY
        _fire_test_event(coresys, "addon_local_non_installed", ContainerState.UNHEALTHY)
        await asyncio.sleep(0)
        restart.assert_not_called()
        start.assert_not_called()


async def test_watchdog_port_conflict_does_not_retry(
    coresys: CoreSys,
    install_app_ssh: App,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Watchdog must not retry or capture when start fails with a port conflict."""
    with patch.object(DockerApp, "attach"):
        await install_app_ssh.load()

    install_app_ssh.watchdog = True
    install_app_ssh._manual_stop = False  # pylint: disable=protected-access

    with (
        patch.object(
            App, "start", side_effect=AppPortConflict(name=TEST_ADDON_SLUG, port=2222)
        ) as start,
        patch.object(DockerApp, "current_state", return_value=ContainerState.FAILED),
        patch.object(DockerApp, "stop"),
        patch("supervisor.addons.addon.async_capture_exception") as capture_exception,
    ):
        caplog.clear()
        _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", ContainerState.FAILED)
        await asyncio.sleep(0)

        start.assert_called_once()
        capture_exception.assert_not_called()
        assert f"Watchdog cannot restart app {install_app_ssh.name}" in caplog.text


async def test_watchdog_on_stop(coresys: CoreSys, install_app_ssh: App) -> None:
    """Test app watchdog restarts app on stop if not manual."""
    with patch.object(DockerApp, "attach"):
        await install_app_ssh.load()

    install_app_ssh.watchdog = True

    with (
        patch.object(App, "restart") as restart,
        patch.object(
            DockerApp,
            "current_state",
            return_value=ContainerState.STOPPED,
        ),
        patch.object(DockerApp, "stop"),
    ):
        # Do not restart when app stopped by user
        _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", ContainerState.RUNNING)
        await asyncio.sleep(0)
        await install_app_ssh.stop()
        _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", ContainerState.STOPPED)
        await asyncio.sleep(0)
        restart.assert_not_called()

        # Do restart app if it stops and user didn't do it
        _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", ContainerState.RUNNING)
        await asyncio.sleep(0)
        _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", ContainerState.STOPPED)
        await asyncio.sleep(0)
        restart.assert_called_once()


@pytest.mark.usefixtures("mock_amd64_arch_supported", "test_repository")
async def test_listener_attached_on_install(coresys: CoreSys):
    """Test events listener attached on app install."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    coresys.docker.containers.get.side_effect = aiodocker.DockerError(
        500, {"message": "fail"}
    )
    with (
        patch("pathlib.Path.is_dir", return_value=True),
        patch(
            "supervisor.addons.addon.App.need_build",
            new=PropertyMock(return_value=False),
        ),
        patch(
            "supervisor.addons.model.AppModel.with_ingress",
            new=PropertyMock(return_value=False),
        ),
    ):
        await coresys.apps.install(TEST_ADDON_SLUG)

    # Normally this would be defaulted to False on start of the app but test skips that
    coresys.apps.get_local_only(TEST_ADDON_SLUG).watchdog = False

    _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", ContainerState.RUNNING)
    await asyncio.sleep(0)
    assert coresys.apps.get(TEST_ADDON_SLUG).state == AppState.STARTED


@pytest.mark.parametrize(
    "boot_timedelta,restart_count", [(timedelta(), 1), (timedelta(days=1), 0)]
)
@pytest.mark.usefixtures("test_repository")
async def test_watchdog_during_attach(
    coresys: CoreSys,
    boot_timedelta: timedelta,
    restart_count: int,
):
    """Test host reboot treated as manual stop but not supervisor restart."""
    store = coresys.apps.store[TEST_ADDON_SLUG]
    await coresys.apps.data.install(store)

    with (
        patch.object(App, "restart") as restart,
        patch.object(HwHelper, "last_boot", return_value=utcnow()),
        patch.object(DockerApp, "attach"),
        patch.object(
            DockerApp,
            "current_state",
            return_value=ContainerState.STOPPED,
        ),
    ):
        coresys.config.last_boot = (
            await coresys.hardware.helper.last_boot() + boot_timedelta
        )
        app = App(coresys, store.slug)
        coresys.apps.local[app.slug] = app
        app.watchdog = True

        await app.load()
        _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", ContainerState.STOPPED)
        await asyncio.sleep(0)

        assert restart.call_count == restart_count


@pytest.mark.usefixtures("install_app_ssh")
async def test_install_update_fails_if_out_of_date(coresys: CoreSys):
    """Test install or update of app fails when supervisor or plugin is out of date."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    with patch.object(
        type(coresys.supervisor), "need_update", new=PropertyMock(return_value=True)
    ):
        with pytest.raises(AppsJobError):
            await coresys.apps.install(TEST_ADDON_SLUG)
        with pytest.raises(AppsJobError):
            await coresys.apps.update(TEST_ADDON_SLUG)

    with (
        patch.object(
            type(coresys.plugins.audio),
            "need_update",
            new=PropertyMock(return_value=True),
        ),
        patch.object(
            type(coresys.plugins.audio), "update", side_effect=AudioUpdateError
        ),
    ):
        with pytest.raises(AppsJobError):
            await coresys.apps.install(TEST_ADDON_SLUG)
        with pytest.raises(AppsJobError):
            await coresys.apps.update(TEST_ADDON_SLUG)


async def test_listeners_removed_on_uninstall(
    coresys: CoreSys, install_app_ssh: App
) -> None:
    """Test app listeners are removed on uninstall."""
    with patch.object(DockerApp, "attach"):
        await install_app_ssh.load()

    assert install_app_ssh.loaded is True
    # pylint: disable=protected-access
    listeners = install_app_ssh._listeners
    for listener in listeners:
        assert (
            listener in coresys.bus._listeners[BusEvent.DOCKER_CONTAINER_STATE_CHANGE]
        )

    with patch.object(App, "persist", new=PropertyMock(return_value=MagicMock())):
        await coresys.apps.uninstall(TEST_ADDON_SLUG)

    for listener in listeners:
        assert (
            listener
            not in coresys.bus._listeners[BusEvent.DOCKER_CONTAINER_STATE_CHANGE]
        )


@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
async def test_start(coresys: CoreSys, install_app_ssh: App) -> None:
    """Test starting an app without healthcheck."""
    install_app_ssh.path_data.mkdir()
    await install_app_ssh.load()
    await asyncio.sleep(0)
    assert install_app_ssh.state == AppState.STOPPED

    start_task = await install_app_ssh.start()
    assert start_task

    _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", ContainerState.RUNNING)
    await start_task
    assert install_app_ssh.state == AppState.STARTED


@pytest.mark.parametrize("state", [ContainerState.HEALTHY, ContainerState.UNHEALTHY])
@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
async def test_start_wait_healthcheck(
    coresys: CoreSys,
    install_app_ssh: App,
    container: DockerContainer,
    state: ContainerState,
) -> None:
    """Test starting an app with a healthcheck waits for health status."""
    install_app_ssh.path_data.mkdir()
    container.show.return_value["Config"] = {"Healthcheck": "exists"}
    await install_app_ssh.load()
    await asyncio.sleep(0)
    assert install_app_ssh.state == AppState.STOPPED

    start_task = await install_app_ssh.start()
    assert start_task

    _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", ContainerState.RUNNING)
    await asyncio.sleep(0.01)

    assert not start_task.done()
    assert install_app_ssh.state == AppState.STARTUP

    _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", state)
    await asyncio.sleep(0.01)

    assert start_task.done()
    assert install_app_ssh.state == AppState.STARTED


@pytest.mark.usefixtures("coresys", "tmp_supervisor_data", "path_extern")
async def test_start_timeout(
    install_app_ssh: App, caplog: pytest.LogCaptureFixture
) -> None:
    """Test starting an app times out while waiting."""
    install_app_ssh.path_data.mkdir()
    await install_app_ssh.load()
    await asyncio.sleep(0)
    assert install_app_ssh.state == AppState.STOPPED

    start_task = await install_app_ssh.start()
    assert start_task

    caplog.clear()
    with patch(
        "supervisor.addons.addon.asyncio.wait_for", side_effect=asyncio.TimeoutError
    ):
        await start_task

    assert "Timeout while waiting for app Terminal & SSH to start" in caplog.text


@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
async def test_restart(coresys: CoreSys, install_app_ssh: App) -> None:
    """Test restarting an app."""
    install_app_ssh.path_data.mkdir()
    await install_app_ssh.load()
    await asyncio.sleep(0)
    assert install_app_ssh.state == AppState.STOPPED

    start_task = await install_app_ssh.restart()
    assert start_task

    _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", ContainerState.RUNNING)
    await start_task
    assert install_app_ssh.state == AppState.STARTED


@pytest.mark.parametrize("status", ["running", "stopped"])
@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
async def test_backup(
    coresys: CoreSys,
    install_app_ssh: App,
    container: DockerContainer,
    status: str,
) -> None:
    """Test backing up an app."""
    container.show.return_value["State"]["Status"] = status
    container.show.return_value["State"]["Running"] = status == "running"
    install_app_ssh.path_data.mkdir()
    await install_app_ssh.load()

    archive = SecureTarArchive(coresys.config.path_tmp / "test.tar", "w")
    archive.open()
    tar_file = archive.create_tar("./test.tar.gz")
    assert await install_app_ssh.backup(tar_file) is None
    archive.close()


@pytest.mark.parametrize("status", ["running", "stopped"])
@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
async def test_backup_no_config(
    coresys: CoreSys,
    install_app_ssh: App,
    container: DockerContainer,
    status: str,
) -> None:
    """Test backing up an app with deleted config directory."""
    container.show.return_value["State"]["Status"] = status
    container.show.return_value["State"]["Running"] = status == "running"

    install_app_ssh.data["map"].append({"type": "addon_config", "read_only": False})
    assert not install_app_ssh.path_config.exists()
    install_app_ssh.path_data.mkdir()
    await install_app_ssh.load()

    archive = SecureTarArchive(coresys.config.path_tmp / "test.tar", "w")
    archive.open()
    tar_file = archive.create_tar("./test.tar.gz")
    assert await install_app_ssh.backup(tar_file) is None
    archive.close()


@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
async def test_backup_with_pre_post_command(
    coresys: CoreSys,
    install_app_ssh: App,
    container: DockerContainer,
) -> None:
    """Test backing up an app with pre and post command."""
    container.show.return_value["State"]["Status"] = "running"
    container.show.return_value["State"]["Running"] = True
    install_app_ssh.path_data.mkdir()
    await install_app_ssh.load()

    archive = SecureTarArchive(coresys.config.path_tmp / "test.tar", "w")
    archive.open()
    tar_file = archive.create_tar("./test.tar.gz")
    with (
        patch.object(App, "backup_pre", new=PropertyMock(return_value="backup_pre")),
        patch.object(App, "backup_post", new=PropertyMock(return_value="backup_post")),
    ):
        assert await install_app_ssh.backup(tar_file) is None
    archive.close()

    assert container.exec.call_count == 2
    assert container.exec.call_args_list[0].args[0] == "backup_pre"
    assert container.exec.call_args_list[1].args[0] == "backup_post"


@pytest.mark.parametrize(
    (
        "container_get_side_effect",
        "exec_start_side_effect",
        "exec_inspect_side_effect",
        "exc_type_raised",
    ),
    [
        (
            aiodocker.DockerError(HTTPStatus.NOT_FOUND, {"message": "missing"}),
            None,
            [{"ExitCode": 1}],
            AppUnknownError,
        ),
        (
            aiodocker.DockerError(HTTPStatus.INTERNAL_SERVER_ERROR, {"message": "bad"}),
            None,
            [{"ExitCode": 1}],
            AppUnknownError,
        ),
        (
            None,
            aiodocker.DockerError(HTTPStatus.INTERNAL_SERVER_ERROR, {"message": "bad"}),
            [{"ExitCode": 1}],
            AppUnknownError,
        ),
        (
            None,
            None,
            aiodocker.DockerError(HTTPStatus.INTERNAL_SERVER_ERROR, {"message": "bad"}),
            AppUnknownError,
        ),
        (None, None, [{"ExitCode": 1}], AppPrePostBackupCommandReturnedError),
    ],
)
@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
async def test_backup_with_pre_command_error(
    coresys: CoreSys,
    install_app_ssh: App,
    container_get_side_effect: aiodocker.DockerError | None,
    exec_start_side_effect: aiodocker.DockerError | None,
    exec_inspect_side_effect: aiodocker.DockerError | list[dict[str, Any]] | None,
    exc_type_raised: type[HassioError],
) -> None:
    """Test backing up an app with error running pre command."""
    coresys.docker.containers.get.side_effect = container_get_side_effect
    coresys.docker.containers.get.return_value.exec.return_value.start.side_effect = (
        exec_start_side_effect
    )
    coresys.docker.containers.get.return_value.exec.return_value.inspect.side_effect = (
        exec_inspect_side_effect
    )

    install_app_ssh.path_data.mkdir()
    await install_app_ssh.load()

    archive = SecureTarArchive(coresys.config.path_tmp / "test.tar", "w")
    archive.open()
    tar_file = archive.create_tar("./test.tar.gz")
    with (
        patch.object(DockerApp, "is_running", return_value=True),
        patch.object(App, "backup_pre", new=PropertyMock(return_value="backup_pre")),
        pytest.raises(exc_type_raised),
    ):
        assert await install_app_ssh.backup(tar_file) is None

    assert not tar_file.path.exists()
    archive.close()


@pytest.mark.parametrize("status", ["running", "stopped"])
@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
async def test_backup_cold_mode(
    coresys: CoreSys,
    install_app_ssh: App,
    container: DockerContainer,
    status: str,
) -> None:
    """Test backing up an app in cold mode."""
    container.show.return_value["State"]["Status"] = status
    container.show.return_value["State"]["Running"] = status == "running"
    install_app_ssh.path_data.mkdir()
    await install_app_ssh.load()

    archive = SecureTarArchive(coresys.config.path_tmp / "test.tar", "w")
    archive.open()
    tar_file = archive.create_tar("./test.tar.gz")
    with (
        patch.object(
            AppModel,
            "backup_mode",
            new=PropertyMock(return_value=AppBackupMode.COLD),
        ),
        patch.object(
            DockerApp, "is_running", side_effect=[status == "running", False, False]
        ),
    ):
        start_task = await install_app_ssh.backup(tar_file)
    archive.close()

    assert bool(start_task) is (status == "running")


@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
async def test_backup_cold_mode_with_watchdog(
    coresys: CoreSys,
    install_app_ssh: App,
    container: DockerContainer,
):
    """Test backing up an app in cold mode with watchdog active."""
    container.show.return_value["State"]["Status"] = "running"
    container.show.return_value["State"]["Running"] = True
    install_app_ssh.watchdog = True
    install_app_ssh.path_data.mkdir()
    await install_app_ssh.load()
    # Clear task queue, including the event fired for running container
    await asyncio.sleep(0)

    # Simulate stop firing the docker event for stopped container like it normally would
    async def mock_stop(*args, **kwargs):
        container.show.return_value["State"]["Status"] = "stopped"
        container.show.return_value["State"]["Running"] = False
        _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", ContainerState.STOPPED)

    # Patching out the normal end of backup process leaves the container in a stopped state
    # Watchdog should still not try to restart it though, it should remain this way
    archive = SecureTarArchive(coresys.config.path_tmp / "test.tar", "w")
    archive.open()
    tar_file = archive.create_tar("./test.tar.gz")
    with (
        patch.object(App, "start") as start,
        patch.object(App, "restart") as restart,
        patch.object(App, "end_backup"),
        patch.object(DockerApp, "stop", new=mock_stop),
        patch.object(
            AppModel,
            "backup_mode",
            new=PropertyMock(return_value=AppBackupMode.COLD),
        ),
    ):
        await install_app_ssh.backup(tar_file)
        await asyncio.sleep(0)
        start.assert_not_called()
        restart.assert_not_called()
    archive.close()


@pytest.mark.parametrize("status", ["running", "stopped"])
@pytest.mark.usefixtures(
    "tmp_supervisor_data", "path_extern", "mock_aarch64_arch_supported"
)
async def test_restore(coresys: CoreSys, install_app_ssh: App, status: str) -> None:
    """Test restoring an app."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    install_app_ssh.path_data.mkdir()
    await install_app_ssh.load()

    tarfile = SecureTarFile(get_fixture_path(f"backup_local_ssh_{status}.tar.gz"))
    with patch.object(DockerApp, "is_running", return_value=False):
        start_task = await coresys.apps.restore(TEST_ADDON_SLUG, tarfile)

    assert bool(start_task) is (status == "running")


@pytest.mark.usefixtures(
    "tmp_supervisor_data", "path_extern", "mock_aarch64_arch_supported"
)
async def test_restore_while_running(
    coresys: CoreSys, install_app_ssh: App, container: DockerContainer
):
    """Test restore of a running app."""
    container.show.return_value["State"]["Status"] = "running"
    container.show.return_value["State"]["Running"] = True
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    install_app_ssh.path_data.mkdir()
    await install_app_ssh.load()

    tarfile = SecureTarFile(get_fixture_path("backup_local_ssh_stopped.tar.gz"))
    with (
        patch.object(DockerApp, "is_running", return_value=True),
        patch.object(Ingress, "update_hass_panel"),
    ):
        start_task = await coresys.apps.restore(TEST_ADDON_SLUG, tarfile)

    assert bool(start_task) is False
    container.stop.assert_called_once()


@pytest.mark.usefixtures(
    "tmp_supervisor_data", "path_extern", "mock_aarch64_arch_supported"
)
async def test_restore_while_running_with_watchdog(
    coresys: CoreSys, install_app_ssh: App, container: DockerContainer
):
    """Test restore of a running app with watchdog interference."""
    container.show.return_value["State"]["Status"] = "running"
    container.show.return_value["State"]["Running"] = True
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    install_app_ssh.path_data.mkdir()
    install_app_ssh.watchdog = True
    await install_app_ssh.load()

    # Simulate stop firing the docker event for stopped container like it normally would
    async def mock_stop(*args, **kwargs):
        container.show.return_value["State"]["Status"] = "stopped"
        container.show.return_value["State"]["Running"] = False
        _fire_test_event(coresys, f"addon_{TEST_ADDON_SLUG}", ContainerState.STOPPED)

    # We restore a stopped backup so restore will not restart it
    # Watchdog will see it stop and should not attempt reanimation either
    tarfile = SecureTarFile(get_fixture_path("backup_local_ssh_stopped.tar.gz"))
    with (
        patch.object(App, "start") as start,
        patch.object(App, "restart") as restart,
        patch.object(DockerApp, "stop", new=mock_stop),
        patch.object(Ingress, "update_hass_panel"),
    ):
        await coresys.apps.restore(TEST_ADDON_SLUG, tarfile)
        await asyncio.sleep(0)
        start.assert_not_called()
        restart.assert_not_called()


@pytest.mark.usefixtures("coresys")
async def test_start_when_running(
    install_app_ssh: App,
    container: DockerContainer,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test starting an app without healthcheck."""
    container.show.return_value["State"]["Status"] = "running"
    container.show.return_value["State"]["Running"] = True
    await install_app_ssh.load()
    await asyncio.sleep(0)
    assert install_app_ssh.state == AppState.STARTED

    caplog.clear()
    start_task = await install_app_ssh.start()
    assert start_task
    await start_task

    assert "local_ssh is already running" in caplog.text


@pytest.mark.usefixtures("test_repository", "mock_aarch64_arch_supported")
async def test_local_example_install(coresys: CoreSys, tmp_supervisor_data: Path):
    """Test install of an app."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    assert not (
        data_dir := tmp_supervisor_data / "addons" / "data" / "local_example"
    ).exists()

    with patch.object(DockerApp, "install") as install:
        await coresys.apps.install("local_example")
        install.assert_called_once()

    assert data_dir.is_dir()


@pytest.mark.usefixtures("test_repository", "tmp_supervisor_data")
async def test_app_install_auth_failure(coresys: CoreSys):
    """Test app install raises DockerRegistryAuthError on 401 with credentials."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    # Configure bad registry credentials
    coresys.docker.config._data["registries"] = {  # pylint: disable=protected-access
        "docker.io": {"username": "baduser", "password": "badpass"}
    }

    with (
        patch.object(
            DockerApp,
            "install",
            side_effect=DockerRegistryAuthError(registry="docker.io"),
        ),
        pytest.raises(DockerRegistryAuthError),
    ):
        await coresys.apps.install("local_example")

    # Verify app data was cleaned up
    assert "local_example" not in coresys.apps.local


@pytest.mark.usefixtures("tmp_supervisor_data")
async def test_app_update_auth_failure(coresys: CoreSys, install_app_example: App):
    """Test app update raises DockerRegistryAuthError on 401 with credentials."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    with (
        patch.object(
            DockerApp,
            "update",
            side_effect=DockerRegistryAuthError(registry="docker.io"),
        ),
        pytest.raises(DockerRegistryAuthError),
    ):
        await install_app_example.update()


@pytest.mark.usefixtures("tmp_supervisor_data")
async def test_app_rebuild_auth_failure(coresys: CoreSys, install_app_example: App):
    """Test app rebuild raises DockerRegistryAuthError on 401 with credentials."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    with (
        patch.object(DockerApp, "remove"),
        patch.object(
            DockerApp,
            "install",
            side_effect=DockerRegistryAuthError(registry="docker.io"),
        ),
        pytest.raises(DockerRegistryAuthError),
    ):
        await install_app_example.rebuild()


@pytest.mark.usefixtures("coresys", "path_extern")
async def test_local_example_start(tmp_supervisor_data: Path, install_app_example: App):
    """Test start of an app."""
    install_app_example.path_data.mkdir()
    await install_app_example.load()
    await asyncio.sleep(0)
    assert install_app_example.state == AppState.STOPPED

    assert not (
        app_config_dir := tmp_supervisor_data / "addon_configs" / "local_example"
    ).exists()

    await install_app_example.start()

    assert app_config_dir.is_dir()


@pytest.mark.usefixtures("coresys", "tmp_supervisor_data")
async def test_local_example_ingress_port_set(install_app_example: App):
    """Test start of an app."""
    install_app_example.path_data.mkdir()
    await install_app_example.load()

    assert install_app_example.ingress_port != 0


@pytest.mark.usefixtures("tmp_supervisor_data")
async def test_app_pulse_error(
    coresys: CoreSys, install_app_example: App, caplog: pytest.LogCaptureFixture
):
    """Test error writing pulse config for app."""
    with patch(
        "supervisor.addons.addon.Path.write_text", side_effect=(err := OSError())
    ):
        err.errno = errno.EBUSY
        await install_app_example.write_pulse()

        assert "can't write pulse/client.config" in caplog.text
        assert coresys.core.healthy is True

        caplog.clear()
        err.errno = errno.EBADMSG
        await install_app_example.write_pulse()

        assert "can't write pulse/client.config" in caplog.text
        assert coresys.core.healthy is False


@pytest.mark.usefixtures("coresys")
def test_auto_update_available(install_app_example: App):
    """Test auto update availability based on versions."""
    assert install_app_example.auto_update is False
    assert install_app_example.need_update is False
    assert install_app_example.auto_update_available is False

    with patch.object(
        App, "version", new=PropertyMock(return_value=AwesomeVersion("1.0"))
    ):
        assert install_app_example.need_update is True
        assert install_app_example.auto_update_available is False

        install_app_example.auto_update = True
        assert install_app_example.auto_update_available is True

    with patch.object(
        App, "version", new=PropertyMock(return_value=AwesomeVersion("0.9"))
    ):
        assert install_app_example.auto_update_available is False

    with patch.object(
        App, "version", new=PropertyMock(return_value=AwesomeVersion("test"))
    ):
        assert install_app_example.auto_update_available is False


@pytest.mark.usefixtures("coresys")
def test_advanced_flag_ignored(install_app_example: App):
    """Ensure advanced flag in config is ignored."""
    install_app_example.data[ATTR_ADVANCED] = True

    assert install_app_example.advanced is False


async def test_paths_cache(coresys: CoreSys, install_app_ssh: App):
    """Test cache for key paths that may or may not exist."""
    assert not install_app_ssh.with_logo
    assert not install_app_ssh.with_icon
    assert not install_app_ssh.with_changelog
    assert not install_app_ssh.with_documentation

    with (
        patch("supervisor.addons.addon.Path.exists", return_value=True),
        patch("supervisor.store.repository.RepositoryLocal.update", return_value=True),
    ):
        await coresys.store.reload(coresys.store.get("local"))

        assert install_app_ssh.with_logo
        assert install_app_ssh.with_icon
        assert install_app_ssh.with_changelog
        assert install_app_ssh.with_documentation


@pytest.mark.usefixtures("mock_amd64_arch_supported")
async def test_app_loads_wrong_image(
    coresys: CoreSys, install_app_ssh: App, container: DockerContainer
):
    """Test app is loaded with incorrect image for architecture."""
    coresys.apps.data.save_data.reset_mock()
    install_app_ssh.persist["image"] = "local/aarch64-addon-ssh"
    assert install_app_ssh.image == "local/aarch64-addon-ssh"

    with (
        patch("pathlib.Path.is_file", return_value=True),
        patch.object(
            coresys.docker,
            "run_command",
            return_value=CommandReturn(0, ["Build successful"]),
        ) as mock_run_command,
        patch.object(
            type(coresys.config),
            "local_to_extern_path",
            return_value=PurePath("/addon/path/on/host"),
        ),
    ):
        await install_app_ssh.load()

    container.delete.assert_called_with(force=True, v=True)
    # one for removing the app, one for removing the app builder
    assert coresys.docker.images.delete.call_count == 2

    assert coresys.docker.images.delete.call_args_list[0] == call(
        "local/aarch64-addon-ssh:latest", force=True
    )
    assert coresys.docker.images.delete.call_args_list[1] == call(
        "local/aarch64-addon-ssh:9.2.1", force=True
    )
    mock_run_command.assert_called_once()
    assert mock_run_command.call_args.args[0] == "docker"
    assert mock_run_command.call_args.kwargs["tag"] == "1.0.0-cli"
    command = mock_run_command.call_args.kwargs["command"]
    assert is_in_list(
        ["--platform", "linux/amd64"],
        command,
    )
    assert is_in_list(
        ["--tag", "local/amd64-addon-ssh:9.2.1"],
        command,
    )
    assert install_app_ssh.image == "local/amd64-addon-ssh"
    coresys.apps.data.save_data.assert_called_once()


@pytest.mark.usefixtures("mock_amd64_arch_supported")
async def test_app_loads_missing_image(coresys: CoreSys, install_app_ssh: App):
    """Test app corrects a missing image on load."""
    coresys.docker.images.inspect.side_effect = aiodocker.DockerError(
        HTTPStatus.NOT_FOUND, {"message": "missing"}
    )

    with (
        patch("pathlib.Path.is_file", return_value=True),
        patch.object(
            coresys.docker,
            "run_command",
            return_value=CommandReturn(0, ["Build successful"]),
        ) as mock_run_command,
        patch.object(
            type(coresys.config),
            "local_to_extern_path",
            return_value=PurePath("/addon/path/on/host"),
        ),
    ):
        await install_app_ssh.load()

    mock_run_command.assert_called_once()
    assert mock_run_command.call_args.args[0] == "docker"
    assert mock_run_command.call_args.kwargs["tag"] == "1.0.0-cli"
    command = mock_run_command.call_args.kwargs["command"]
    assert is_in_list(
        ["--platform", "linux/amd64"],
        command,
    )
    assert is_in_list(
        ["--tag", "local/amd64-addon-ssh:9.2.1"],
        command,
    )
    assert install_app_ssh.image == "local/amd64-addon-ssh"


@pytest.mark.usefixtures("container", "mock_amd64_arch_supported")
async def test_app_load_succeeds_with_docker_errors(
    coresys: CoreSys, install_app_ssh: App, caplog: pytest.LogCaptureFixture
):
    """Docker errors while building/pulling an image during load should not raise and fail setup."""
    # Build env invalid failure
    coresys.docker.images.inspect.side_effect = aiodocker.DockerError(
        HTTPStatus.NOT_FOUND, {"message": "missing"}
    )
    caplog.clear()
    await install_app_ssh.load()
    assert "Cannot build app 'local_ssh' because dockerfile is missing" in caplog.text

    # Image build failure
    caplog.clear()
    with (
        patch("pathlib.Path.is_file", return_value=True),
        patch.object(
            CoreConfig,
            "local_to_extern_path",
            return_value=PurePath("/addon/path/on/host"),
        ),
        patch.object(
            DockerAPI, "run_command", return_value=CommandReturn(1, ["error"])
        ),
    ):
        await install_app_ssh.load()
    assert (
        "Docker build failed for local/amd64-addon-ssh:9.2.1 (exit code 1). Build output:\nerror"
        in caplog.text
    )

    # Image pull failure
    install_app_ssh.data["image"] = "test/amd64-addon-ssh"
    caplog.clear()
    with patch.object(
        DockerAPI,
        "pull_image",
        side_effect=aiodocker.DockerError(400, {"message": "error"}),
    ):
        await install_app_ssh.load()
    assert "Can't install test/amd64-addon-ssh:9.2.1:" in caplog.text


@pytest.mark.usefixtures("coresys")
async def test_app_manual_only_boot(install_app_example: App):
    """Test an app with manual only boot mode."""
    assert install_app_example.boot_config == "manual_only"
    assert install_app_example.boot == "manual"

    # Users cannot change boot mode of an app with manual forced so changing boot isn't realistic
    # However boot mode can change on update and user may have set auto before, ensure it is ignored
    install_app_example.boot = "auto"
    assert install_app_example.boot == "manual"


@pytest.mark.parametrize(
    ("initial_state", "target_state", "issue", "suggestions"),
    [
        (
            AppState.ERROR,
            AppState.STARTED,
            BOOT_FAIL_ISSUE,
            [suggestion.type for suggestion in BOOT_FAIL_SUGGESTIONS],
        ),
        (
            AppState.STARTED,
            AppState.STOPPED,
            Issue(
                IssueType.DEVICE_ACCESS_MISSING,
                ContextType.ADDON,
                reference=TEST_ADDON_SLUG,
            ),
            [SuggestionType.EXECUTE_RESTART],
        ),
    ],
)
async def test_app_state_dismisses_issue(
    coresys: CoreSys,
    install_app_ssh: App,
    initial_state: AppState,
    target_state: AppState,
    issue: Issue,
    suggestions: list[SuggestionType],
):
    """Test an app state change dismisses the issues."""
    install_app_ssh.state = initial_state
    coresys.resolution.add_issue(issue, suggestions)

    install_app_ssh.state = target_state
    assert coresys.resolution.issues == []
    assert coresys.resolution.suggestions == []


async def test_app_disable_boot_dismisses_boot_fail(
    coresys: CoreSys, install_app_ssh: App
):
    """Test a disabling boot dismisses the boot fail issue."""
    install_app_ssh.boot = AppBoot.AUTO
    install_app_ssh.state = AppState.ERROR
    coresys.resolution.add_issue(
        BOOT_FAIL_ISSUE, [suggestion.type for suggestion in BOOT_FAIL_SUGGESTIONS]
    )

    install_app_ssh.boot = AppBoot.MANUAL
    assert coresys.resolution.issues == []
    assert coresys.resolution.suggestions == []


@pytest.mark.parametrize(
    ("docker_message", "port"),
    [
        (
            "failed to set up container networking: driver failed programming external connectivity on endpoint addon_local_ssh (ea4d0fdaa72cf86f2c9199a04208e3eaf0c5a0d6fd34b3c7f4fab2daadb1f3a9): failed to bind host port for 0.0.0.0:2222:172.30.33.4:22/tcp: address already in use",
            2222,
        ),
        (
            "failed to set up container networking: driver failed programming external connectivity on endpoint addon_local_ssh (ea4d0fdaa72cf86f2c9199a04208e3eaf0c5a0d6fd34b3c7f4fab2daadb1f3a9): Bind for 0.0.0.0:2222 failed: port is already allocated",
            2222,
        ),
        (
            "failed to set up container networking: driver failed programming external connectivity on endpoint addon_local_ssh (ea4d0fdaa72cf86f2c9199a04208e3eaf0c5a0d6fd34b3c7f4fab2daadb1f3a9): failed to bind host port 0.0.0.0:2222/tcp: address already in use",
            2222,
        ),
    ],
)
@pytest.mark.usefixtures(
    "container", "mock_amd64_arch_supported", "path_extern", "tmp_supervisor_data"
)
async def test_app_start_port_conflict_error(
    coresys: CoreSys,
    install_app_ssh: App,
    caplog: pytest.LogCaptureFixture,
    docker_message: str,
    port: int,
):
    """Test port conflict error when trying to start app."""
    install_app_ssh.data["image"] = "test/amd64-addon-ssh"
    coresys.docker.containers.create.return_value.start.side_effect = (
        aiodocker.DockerError(HTTPStatus.INTERNAL_SERVER_ERROR, docker_message)
    )
    await install_app_ssh.load()

    caplog.clear()
    with (
        patch.object(App, "write_options"),
        pytest.raises(
            AppPortConflict,
            check=lambda exc: exc.extra_fields == {"name": "local_ssh", "port": port},
        ),
    ):
        await install_app_ssh.start()

    assert (
        f"Cannot start container addon_local_ssh because port {port} is already in use"
        in caplog.text
    )
