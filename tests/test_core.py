"""Testing handling with CoreState."""

# pylint: disable=W0212
import asyncio
from contextlib import suppress
import datetime
import errno
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

import aiodocker
from awesomeversion import AwesomeVersion
import pytest

from supervisor.const import AppStartup, CoreState
from supervisor.coresys import CoreSys
from supervisor.exceptions import AppFileReadError, HassioError, WhoamiSSLError
from supervisor.hardware.helper import HwHelper
from supervisor.homeassistant.core import HomeAssistantCore
from supervisor.host.control import SystemControl
from supervisor.host.info import InfoCenter
from supervisor.resolution.const import IssueType, SuggestionType, UnhealthyReason
from supervisor.supervisor import Supervisor
from supervisor.utils.dt import utcnow
from supervisor.utils.whoami import WhoamiData

from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.systemd import Systemd as SystemdService
from tests.dbus_service_mocks.systemd_unit import SystemdUnit as SystemdUnitService


@pytest.mark.parametrize("run_supervisor_state", ["test_file"], indirect=True)
async def test_write_state(run_supervisor_state: MagicMock, coresys: CoreSys):
    """Test write corestate to /run/supervisor."""
    run_supervisor_state.reset_mock()

    await coresys.core.set_state(CoreState.RUNNING)

    run_supervisor_state.write_text.assert_called_with(
        str(CoreState.RUNNING), encoding="utf-8"
    )

    await coresys.core.set_state(CoreState.SHUTDOWN)

    run_supervisor_state.write_text.assert_called_with(
        str(CoreState.SHUTDOWN), encoding="utf-8"
    )


async def test_adjust_system_datetime(coresys: CoreSys, websession: MagicMock):
    """Test _adjust_system_datetime method with successful retrieve_whoami."""
    utc_ts = datetime.datetime.now().replace(tzinfo=datetime.UTC)
    with patch(
        "supervisor.core.retrieve_whoami",
        new_callable=AsyncMock,
        side_effect=[WhoamiData("Europe/Zurich", utc_ts)],
    ) as mock_retrieve_whoami:
        await coresys.core._adjust_system_datetime()
        mock_retrieve_whoami.assert_called_once()
        assert coresys.core.sys_config.timezone == "Europe/Zurich"

        # Validate we don't retrieve whoami once timezone has been set
        mock_retrieve_whoami.reset_mock()
        await coresys.core._adjust_system_datetime()
        mock_retrieve_whoami.assert_not_called()


async def test_adjust_system_datetime_without_ssl(
    coresys: CoreSys, websession: MagicMock
):
    """Test _adjust_system_datetime method when retrieve_whoami raises WhoamiSSLError."""
    utc_ts = datetime.datetime.now().replace(tzinfo=datetime.UTC)
    with patch(
        "supervisor.core.retrieve_whoami",
        new_callable=AsyncMock,
        side_effect=[WhoamiSSLError("SSL error"), WhoamiData("Europe/Zurich", utc_ts)],
    ) as mock_retrieve_whoami:
        await coresys.core._adjust_system_datetime()
        assert mock_retrieve_whoami.call_count == 2
        assert mock_retrieve_whoami.call_args_list[0].args[1]
        assert not mock_retrieve_whoami.call_args_list[1].args[1]
        assert coresys.core.sys_config.timezone == "Europe/Zurich"


async def test_adjust_system_datetime_if_time_behind(
    coresys: CoreSys,
    websession: MagicMock,
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
):
    """Test _adjust_system_datetime method when current time is ahead more than 1 hour."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.StopUnit.calls.clear()
    systemd_unit_service: SystemdUnitService = all_dbus_services["systemd_unit"]
    systemd_unit_service.active_state = "active"
    systemd_unit_service.active_state_read.clear()

    utc_ts = datetime.datetime.now().replace(tzinfo=datetime.UTC) + datetime.timedelta(
        hours=1, minutes=1
    )
    with (
        patch(
            "supervisor.core.retrieve_whoami",
            new_callable=AsyncMock,
            side_effect=[WhoamiData("Europe/Zurich", utc_ts)],
        ) as mock_retrieve_whoami,
        patch.object(SystemControl, "set_datetime") as mock_set_datetime,
        patch.object(SystemControl, "set_timezone") as mock_set_timezone,
        patch.object(
            InfoCenter, "dt_synchronized", new=PropertyMock(return_value=False)
        ),
        patch.object(InfoCenter, "use_ntp", new=PropertyMock(return_value=True)),
        patch.object(
            Supervisor, "check_and_update_connectivity"
        ) as mock_check_connectivity,
    ):
        # Start the time adjustment which will wait for timesyncd to stop
        task = asyncio.create_task(coresys.core._adjust_system_datetime())
        # wait_for_active_state installs the PropertiesChanged subscription and
        # then reads ActiveState. Waiting for that read guarantees the client is
        # subscribed before we emit, so the signal cannot be lost to a race.
        await systemd_unit_service.active_state_read.wait()
        # Simulate timesyncd stopping via D-Bus signal
        systemd_unit_service.emit_properties_changed({"ActiveState": "inactive"})
        await task

        mock_retrieve_whoami.assert_called_once()
        mock_set_datetime.assert_called_once()
        mock_check_connectivity.assert_called_once()
        mock_set_timezone.assert_called_once_with("Europe/Zurich")

        # Verify timesyncd was stopped before setting time
        assert systemd_service.StopUnit.calls == [
            ("systemd-timesyncd.service", "replace")
        ]

        # Verify issue was created
        assert any(
            issue.type == IssueType.NTP_SYNC_FAILED
            for issue in coresys.resolution.issues
        )
        assert any(
            suggestion.type == SuggestionType.ENABLE_NTP
            for suggestion in coresys.resolution.suggestions
        )


async def test_adjust_system_datetime_sync_timezone_to_host(
    coresys: CoreSys, websession: MagicMock
):
    """Test _adjust_system_datetime method syncs timezone to host when different."""
    await coresys.core.sys_config.set_timezone("Europe/Prague")

    with (
        patch.object(SystemControl, "set_timezone") as mock_set_timezone,
        patch.object(InfoCenter, "timezone", new=PropertyMock(return_value="Etc/UTC")),
    ):
        await coresys.core._adjust_system_datetime()
        mock_set_timezone.assert_called_once_with("Europe/Prague")


async def test_write_state_failure(
    run_supervisor_state: MagicMock, coresys: CoreSys, caplog: pytest.LogCaptureFixture
):
    """Test failure to write corestate to /run/supervisor."""
    err = OSError()
    err.errno = errno.EBADMSG
    run_supervisor_state.write_text.side_effect = err
    await coresys.core.set_state(CoreState.RUNNING)

    assert "Can't update the Supervisor state" in caplog.text
    assert coresys.core.state == CoreState.RUNNING


# Components whose load() method is awaited from Core.setup().
_SETUP_LOAD_COMPONENTS = (
    "api",
    "hardware",
    "dbus",
    "host",
    "os",
    "mounts",
    "docker",
    "updater",
    "plugins",
    "homeassistant",
    "arch",
    "store",
    "apps",
    "backups",
    "services",
    "discovery",
    "ingress",
    "resolution",
)


@pytest.fixture
def mocked_setup_loads(coresys: CoreSys):
    """Replace all load() calls in Core.setup() with AsyncMock."""
    with (
        patch.object(coresys, "init_websession", new=AsyncMock()),
        patch.object(Supervisor, "check_and_update_connectivity", new=AsyncMock()),
        patch.object(coresys.core, "_adjust_system_datetime", new=AsyncMock()),
    ):
        patches = [
            patch.object(getattr(coresys, attr), "load", new=AsyncMock())
            for attr in _SETUP_LOAD_COMPONENTS
        ]
        for p in patches:
            p.start()
        try:
            yield
        finally:
            for p in patches:
                p.stop()


@pytest.mark.usefixtures("mocked_setup_loads")
async def test_setup_app_file_read_error_not_captured(
    coresys: CoreSys, caplog: pytest.LogCaptureFixture
):
    """Test setup does not capture AppFileReadError to Sentry but marks unhealthy."""
    coresys.apps.load.side_effect = AppFileReadError(
        app="local_example", error="[Errno 74] Bad message"
    )
    with patch("supervisor.core.async_capture_exception") as capture_mock:
        await coresys.core.setup()

    capture_mock.assert_not_called()
    assert "Fatal error happening on load Task" not in caplog.text
    assert "Error on load Task" in caplog.text
    assert UnhealthyReason.SETUP in coresys.resolution.unhealthy


@pytest.mark.usefixtures("mocked_setup_loads")
async def test_setup_unhandled_exception_captured(
    coresys: CoreSys, caplog: pytest.LogCaptureFixture
):
    """Test setup captures unhandled exceptions to Sentry and marks unhealthy."""
    coresys.apps.load.side_effect = HassioError("boom")
    with patch("supervisor.core.async_capture_exception") as capture_mock:
        await coresys.core.setup()

    capture_mock.assert_called_once()
    assert "Fatal error happening on load Task" in caplog.text
    assert UnhealthyReason.SETUP in coresys.resolution.unhealthy


async def test_shutdown_reentrant_waits(coresys: CoreSys):
    """Concurrent shutdown() calls await the in-flight shutdown rather than re-running."""
    call_count = 0
    shutdown_started = asyncio.Event()
    proceed = asyncio.Event()

    original_shutdown = coresys.apps.shutdown

    async def slow_app_shutdown(startup):
        nonlocal call_count
        call_count += 1
        shutdown_started.set()
        await proceed.wait()
        return await original_shutdown(startup)

    await coresys.core.set_state(CoreState.RUNNING)

    with patch.object(coresys.apps, "shutdown", side_effect=slow_app_shutdown):
        task1 = asyncio.create_task(coresys.core.shutdown())
        await shutdown_started.wait()

        # Second call should wait, not start a new shutdown
        task2 = asyncio.create_task(coresys.core.shutdown())
        await asyncio.sleep(0.05)

        proceed.set()
        await asyncio.gather(task1, task2)

    # AppStartup has 4 levels (APPLICATION/SERVICES/SYSTEM/INITIALIZE); a single
    # shutdown call iterates them. A re-entered shutdown would double the count.
    assert call_count == 4
    assert coresys.core._shutdown_event.is_set()


async def test_shutdown_releases_event_when_set_state_cancelled(coresys: CoreSys):
    """Cancellation mid set_state() must still release waiters.

    set_state() updates Core._state before awaiting the run-state file write.
    If cancellation hits during that await, in-memory state is already
    SHUTDOWN. Without the try/finally around set_state(), _shutdown_event
    would never be set and concurrent callers would deadlock on wait().
    """
    await coresys.core.set_state(CoreState.RUNNING)

    cancel_during_write = asyncio.Event()

    async def cancel_during_set_state(*_args, **_kwargs):
        cancel_during_write.set()
        await asyncio.sleep(3600)  # wait long enough to be cancelled

    with patch.object(
        coresys.core, "_write_run_state", side_effect=cancel_during_set_state
    ):
        task = asyncio.create_task(coresys.core.shutdown())
        await cancel_during_write.wait()
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task

    # In-memory state moved to SHUTDOWN before the cancellation point
    assert coresys.core.state == CoreState.SHUTDOWN
    # finally must have run so any future caller does not deadlock
    assert coresys.core._shutdown_event.is_set()


async def test_shutdown_transitions_state(coresys: CoreSys):
    """Shutdown moves Core into SHUTDOWN state so HA Core/WS observers react."""
    await coresys.core.set_state(CoreState.RUNNING)
    await coresys.core.shutdown()
    assert coresys.core.state == CoreState.SHUTDOWN


async def test_teardown_services_does_not_change_state(coresys: CoreSys):
    """Teardown leaves Core state alone so callers (e.g. backup restore) control it."""
    await coresys.core.set_state(CoreState.FREEZE)
    await coresys.core.teardown_services()
    assert coresys.core.state == CoreState.FREEZE


async def test_teardown_services_does_not_stop_plugins(coresys: CoreSys):
    """Plugins must keep running across teardown so restore can talk to them."""
    await coresys.core.set_state(CoreState.FREEZE)
    with patch.object(coresys.plugins, "shutdown") as mock_plugins_shutdown:
        await coresys.core.teardown_services()
    mock_plugins_shutdown.assert_not_called()


async def test_shutdown_stops_plugins(coresys: CoreSys):
    """Real shutdown stops plugins as the final step."""
    await coresys.core.set_state(CoreState.RUNNING)
    with patch.object(coresys.plugins, "shutdown") as mock_plugins_shutdown:
        await coresys.core.shutdown()
    mock_plugins_shutdown.assert_called_once()


@pytest.mark.parametrize(
    "state", [CoreState.STOPPING, CoreState.CLOSE], ids=["stopping", "close"]
)
async def test_shutdown_ignored_during_stop(
    coresys: CoreSys, caplog: pytest.LogCaptureFixture, state: CoreState
):
    """Shutdown is ignored when Supervisor is already stopping."""
    await coresys.core.set_state(state)

    with patch.object(coresys.apps, "shutdown") as mock_app_shutdown:
        await coresys.core.shutdown()

    mock_app_shutdown.assert_not_called()
    assert "Ignoring shutdown request, Supervisor is already stopping" in caplog.text


@pytest.mark.parametrize(
    "state",
    [CoreState.INITIALIZE, CoreState.STARTUP, CoreState.SETUP],
    ids=["initialize", "startup", "setup"],
)
async def test_shutdown_skipped_during_startup(
    coresys: CoreSys, caplog: pytest.LogCaptureFixture, state: CoreState
):
    """Shutdown returns early when Supervisor has not finished starting yet."""
    await coresys.core.set_state(state)

    with patch.object(coresys.apps, "shutdown") as mock_app_shutdown:
        await coresys.core.shutdown()

    mock_app_shutdown.assert_not_called()
    assert (
        "Ignoring shutdown request, Supervisor has not finished starting" in caplog.text
    )


async def test_stop_signals_stopping_complete(coresys: CoreSys):
    """Test stop() sets stopping_complete before starting the teardown."""
    await coresys.core.set_state(CoreState.RUNNING)

    stopping = asyncio.Event()
    seen_at_api_stop: list[tuple[CoreState, bool]] = []

    async def api_stop():
        seen_at_api_stop.append((coresys.core.state, stopping.is_set()))

    coresys._websession = AsyncMock()
    with (
        patch.object(coresys.api, "stop", new=api_stop),
        patch.object(coresys.scheduler, "shutdown", new=AsyncMock()),
        patch.object(coresys.docker, "unload", new=AsyncMock()),
        patch.object(coresys.homeassistant.api, "close", new=AsyncMock()),
        patch.object(coresys.ingress, "unload", new=AsyncMock()),
        patch.object(coresys.hardware, "unload", new=AsyncMock()),
        patch.object(coresys.dbus, "unload", new=AsyncMock()),
        patch.object(coresys.loop, "stop") as loop_stop,
    ):
        await coresys.core.stop(stopping_complete=stopping)

    assert stopping.is_set()
    assert coresys.core.state == CoreState.CLOSE
    # The event was set while STOPPING, before the API teardown began
    assert seen_at_api_stop == [(CoreState.STOPPING, True)]
    loop_stop.assert_called_once()


@pytest.mark.parametrize(
    "state", [CoreState.STOPPING, CoreState.CLOSE], ids=["stopping", "close"]
)
async def test_stop_reentry_signals_event_without_teardown(
    coresys: CoreSys, state: CoreState
):
    """Test stop() while already stopping sets the event and does nothing else."""
    await coresys.core.set_state(state)

    stopping = asyncio.Event()
    with patch.object(coresys.api, "stop", new=(api_stop := AsyncMock())):
        await coresys.core.stop(stopping_complete=stopping)

    assert stopping.is_set()
    api_stop.assert_not_called()
    assert coresys.core.state == state


@pytest.fixture
def core_start_base_mocks(coresys: CoreSys):
    """Set up boilerplate mocks for Core.start() that are not under test."""
    # Default config.last_boot is epoch (1970); HwHelper.last_boot returns now →
    # the two differ, so the supervisor-restart early-return is not triggered.
    with (
        patch.object(coresys.os, "mark_healthy", new=AsyncMock()),
        patch.object(coresys.updater, "reload", new=AsyncMock()),
        patch.object(Supervisor, "need_update", new=PropertyMock(return_value=False)),
        patch.object(
            Supervisor,
            "image",
            new=PropertyMock(
                return_value="ghcr.io/home-assistant/amd64-hassio-supervisor"
            ),
        ),
        patch.object(HwHelper, "last_boot", return_value=utcnow()),
        patch.object(coresys.services, "reset", new=AsyncMock()),
        patch.object(coresys.tasks, "load", new=AsyncMock()),
        patch.object(coresys.host, "reload", new=AsyncMock()),
        patch.object(coresys.resolution, "healthcheck", new=AsyncMock()),
        patch.object(
            HomeAssistantCore,
            "error_state",
            new=PropertyMock(return_value=False),
        ),
        patch.object(coresys.core, "_update_last_boot", new=AsyncMock()),
        patch.object(coresys.homeassistant.websocket, "supervisor_update_event"),
        patch.object(coresys.apps, "boot", new=AsyncMock()),
        patch.object(
            coresys.homeassistant.core, "is_running", new=AsyncMock(return_value=False)
        ),
        patch.object(coresys.homeassistant.core, "start", new=AsyncMock()),
    ):
        coresys.homeassistant.version = AwesomeVersion("2023.8.1")
        yield


def _make_docker_containers_mock(mock_container: MagicMock) -> MagicMock:
    """Return a mock for sys_docker.docker.containers.

    get() raises DockerError(404) to indicate no stale container;
    create() returns mock_container.
    """
    mock_containers = MagicMock()
    mock_containers.get = AsyncMock(
        side_effect=aiodocker.DockerError(404, {"message": "no such container"})
    )
    mock_containers.create = AsyncMock(return_value=mock_container)
    return mock_containers


def _make_reservation_container() -> MagicMock:
    """Return a mock Docker container used as the port reservation container."""
    mock_container = MagicMock()
    mock_container.start = AsyncMock()
    mock_container.kill = AsyncMock()
    mock_container.delete = AsyncMock()
    return mock_container


@pytest.mark.usefixtures("core_start_base_mocks")
@pytest.mark.parametrize(
    ("http_server_host", "expected_bind_host"),
    [
        (None, "0.0.0.0"),
        (["192.0.2.1", "0.0.0.0"], "192.0.2.1"),
    ],
    ids=["no_server_host", "with_server_host"],
)
async def test_start_reserves_core_port(
    coresys: CoreSys,
    http_server_host: list[str] | None,
    expected_bind_host: str,
):
    """On fresh boot, Core's port is reserved using the correct bind address.

    When http_server_host is None the reservation falls back to 0.0.0.0;
    when it is set the first listed host is used.
    """
    coresys.homeassistant.http_server_host = http_server_host
    assert coresys.homeassistant.api_port == 8123

    mock_container = _make_reservation_container()
    coresys.docker.docker = MagicMock()
    coresys.docker.docker.containers = _make_docker_containers_mock(mock_container)

    await coresys.core.start()

    # Container must be created with host networking and the right bind address
    coresys.docker.docker.containers.create.assert_awaited_once()
    create_config = coresys.docker.docker.containers.create.call_args[0][0]
    assert create_config["HostConfig"]["NetworkMode"] == "host"
    assert expected_bind_host in create_config["Cmd"][-1]
    assert "8123" in create_config["Cmd"][-1]

    # Container must be started then cleaned up before Core starts
    mock_container.start.assert_awaited_once()
    mock_container.kill.assert_awaited_once()
    mock_container.delete.assert_awaited_once()

    # Core must have started
    coresys.homeassistant.core.start.assert_awaited_once()

    mock_container.kill.assert_awaited_once()
    mock_container.delete.assert_awaited_once()
    coresys.homeassistant.core.start.assert_awaited_once()


@pytest.mark.usefixtures("core_start_base_mocks")
async def test_start_port_held_during_app_boot_released_before_core_start(
    coresys: CoreSys,
):
    """Port reservation container exists during SYSTEM/SERVICES boot and is removed before Core starts.

    This verifies that an app attempting to bind Core's port during SYSTEM or
    SERVICES boot would be blocked by the reservation container, and that the
    container is removed in time for Core to bind its own port.
    """
    coresys.homeassistant.http_server_host = None

    call_sequence: list[str] = []

    mock_container = _make_reservation_container()
    mock_container.start.side_effect = lambda: call_sequence.append("container_start")
    mock_container.kill.side_effect = lambda: call_sequence.append("container_kill")

    coresys.docker.docker = MagicMock()
    coresys.docker.docker.containers = _make_docker_containers_mock(mock_container)

    async def tracking_boot(stage: AppStartup) -> None:
        call_sequence.append(f"boot:{stage}")

    async def tracking_core_start() -> None:
        call_sequence.append("core_start")

    with (
        patch.object(coresys.apps, "boot", side_effect=tracking_boot),
        patch.object(
            coresys.homeassistant.core, "start", side_effect=tracking_core_start
        ),
    ):
        await coresys.core.start()

    assert "container_start" in call_sequence
    assert f"boot:{AppStartup.SYSTEM}" in call_sequence
    assert f"boot:{AppStartup.SERVICES}" in call_sequence
    assert "container_kill" in call_sequence
    assert "core_start" in call_sequence

    container_start_idx = call_sequence.index("container_start")
    system_boot_idx = call_sequence.index(f"boot:{AppStartup.SYSTEM}")
    services_boot_idx = call_sequence.index(f"boot:{AppStartup.SERVICES}")
    container_kill_idx = call_sequence.index("container_kill")
    core_start_idx = call_sequence.index("core_start")

    # Reservation container must be running before any pre-Core app stage boots
    assert container_start_idx < system_boot_idx
    assert container_start_idx < services_boot_idx
    # Container must be stopped before Core starts
    assert container_kill_idx < core_start_idx


@pytest.mark.usefixtures("core_start_base_mocks")
async def test_start_skips_port_reservation_when_core_already_running(coresys: CoreSys):
    """When Core is already running (Supervisor restart), no reservation container is created."""
    coresys.docker.docker = MagicMock()
    coresys.docker.docker.containers = MagicMock()

    with patch.object(
        coresys.homeassistant.core,
        "is_running",
        new=AsyncMock(return_value=True),
    ):
        await coresys.core.start()

    coresys.docker.docker.containers.create.assert_not_called()
