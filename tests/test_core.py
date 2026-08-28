"""Testing handling with CoreState."""

# pylint: disable=W0212
import asyncio
from contextlib import suppress
import datetime
import errno
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

from awesomeversion import AwesomeVersion
from dbus_fast import DBusError, ErrorType, Variant
import pytest

from supervisor.const import AppStartup, CoreState
from supervisor.core import (
    _PORT_RESERVE_SERVICE,
    _PORT_RESERVE_UNIT,
    _format_bind_address,
)
from supervisor.coresys import CoreSys
from supervisor.dbus.const import DBUS_ERR_SYSTEMD_NO_SUCH_UNIT
from supervisor.exceptions import (
    AppFileReadError,
    DBusNotConnectedError,
    HassioError,
    WhoamiSSLError,
)
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
def core_start_base_mocks(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
):
    """Set up boilerplate mocks for Core.start() that are not under test."""
    # Default config.last_boot is epoch (1970); HwHelper.last_boot returns now →
    # the two differ, so the supervisor-restart early-return is not triggered.

    # By default simulate a fresh boot with no leftover port reservation
    # units: the socket and paired service unit are each checked once during
    # stale-unit cleanup (both raise NoSuchUnit), then the socket unit is
    # checked again while waiting for it to come up, then both units are
    # checked again during the real release before Core starts. Sized
    # generously since a single reservation cycle makes several GetUnit
    # calls across both units.
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_unit_service: SystemdUnitService = all_dbus_services["systemd_unit"]
    systemd_service.response_get_unit = [
        DBusError(DBUS_ERR_SYSTEMD_NO_SUCH_UNIT, "no such unit"),
        DBusError(DBUS_ERR_SYSTEMD_NO_SUCH_UNIT, "no such unit"),
    ] + [SystemdService.response_get_unit] * 20
    # Link the unit mock so Start/StopUnit calls flip its ActiveState the
    # same way real systemd would, letting wait_for_active_state resolve
    # immediately instead of waiting on a signal that never comes.
    systemd_service.mock_systemd_unit = systemd_unit_service

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


@pytest.mark.parametrize(
    ("host", "expected"),
    [
        ("0.0.0.0", "0.0.0.0:8123"),
        ("192.0.2.1", "192.0.2.1:8123"),
        ("::", "[::]:8123"),
        ("2001:db8::1", "[2001:db8::1]:8123"),
    ],
)
def test_format_bind_address(host: str, expected: str) -> None:
    """IPv6 addresses must be bracketed for systemd's Listen directive."""
    assert _format_bind_address(host, 8123) == expected


@pytest.mark.usefixtures("core_start_base_mocks")
@pytest.mark.parametrize(
    ("http_server_host", "expected_listen"),
    [
        (None, ["0.0.0.0:80", "[::]:80"]),
        (["192.0.2.1", "0.0.0.0"], ["192.0.2.1:80", "0.0.0.0:80"]),
        (["::"], ["[::]:80"]),
    ],
    ids=["no_server_host", "with_server_host", "ipv6_only"],
)
async def test_start_reserves_core_port(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
    http_server_host: list[str] | None,
    expected_listen: list[str],
):
    """On fresh boot, Core's port is reserved on every configured bind address.

    When http_server_host is None the reservation falls back to protecting
    both 0.0.0.0 and :: (both address families); when it is set, every listed
    host is reserved, not just the first one.
    """
    coresys.homeassistant.http_server_host = http_server_host
    assert coresys.homeassistant.api_port == 80

    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.StartTransientUnit.calls.clear()
    systemd_service.StopUnit.calls.clear()

    await coresys.core.start()

    # A transient socket unit must be created listening on every address
    assert len(systemd_service.StartTransientUnit.calls) == 1
    unit_name, mode, properties, aux = systemd_service.StartTransientUnit.calls[0]
    assert unit_name == _PORT_RESERVE_UNIT
    assert mode == "replace"
    listen_property = next(value for key, value in properties if key == "Listen")
    assert listen_property == Variant(
        "a(ss)", [("Stream", entry) for entry in expected_listen]
    )
    ipv6_only_property = next(
        value for key, value in properties if key == "BindIPv6Only"
    )
    assert ipv6_only_property == Variant("s", "ipv6-only")

    # The socket must be paired atomically with a holder service, or the
    # first incoming connection during boot would tear the reservation down
    assert len(aux) == 1
    service_name, service_properties = aux[0]
    assert service_name == _PORT_RESERVE_SERVICE
    service_properties_dict = dict(service_properties)
    assert service_properties_dict["Type"] == Variant("s", "oneshot")
    assert service_properties_dict["RemainAfterExit"] == Variant("b", True)

    # Reservation must be released before Core starts
    assert (_PORT_RESERVE_UNIT, "replace") in systemd_service.StopUnit.calls
    assert (_PORT_RESERVE_SERVICE, "replace") in systemd_service.StopUnit.calls

    # Core must have started
    coresys.homeassistant.core.start.assert_awaited_once()


@pytest.mark.usefixtures("core_start_base_mocks")
async def test_start_port_held_during_app_boot_released_before_core_start(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
):
    """Port reservation unit exists during SYSTEM/SERVICES boot and is stopped before Core starts.

    This verifies that an app attempting to bind Core's port during SYSTEM or
    SERVICES boot would be blocked by the reservation unit, and that the unit
    is stopped in time for Core to bind its own port.
    """
    coresys.homeassistant.http_server_host = None

    call_sequence: list[str] = []

    orig_reserve = coresys.core._reserve_core_port
    orig_release = coresys.core._release_core_port

    async def tracking_reserve(hosts: list[str], port: int) -> bool:
        result = await orig_reserve(hosts, port)
        call_sequence.append("port_reserved")
        return result

    async def tracking_release() -> bool:
        result = await orig_release()
        call_sequence.append("port_released")
        return result

    async def tracking_boot(stage: AppStartup) -> None:
        call_sequence.append(f"boot:{stage}")

    async def tracking_core_start() -> None:
        call_sequence.append("core_start")

    with (
        patch.object(coresys.core, "_reserve_core_port", side_effect=tracking_reserve),
        patch.object(coresys.core, "_release_core_port", side_effect=tracking_release),
        patch.object(coresys.apps, "boot", side_effect=tracking_boot),
        patch.object(
            coresys.homeassistant.core, "start", side_effect=tracking_core_start
        ),
    ):
        await coresys.core.start()

    assert "port_reserved" in call_sequence
    assert f"boot:{AppStartup.SYSTEM}" in call_sequence
    assert f"boot:{AppStartup.SERVICES}" in call_sequence
    assert "port_released" in call_sequence
    assert "core_start" in call_sequence

    reserved_idx = call_sequence.index("port_reserved")
    system_boot_idx = call_sequence.index(f"boot:{AppStartup.SYSTEM}")
    services_boot_idx = call_sequence.index(f"boot:{AppStartup.SERVICES}")
    released_idx = call_sequence.index("port_released")
    core_start_idx = call_sequence.index("core_start")

    # Reservation unit must be active before any pre-Core app stage boots
    assert reserved_idx < system_boot_idx
    assert reserved_idx < services_boot_idx
    # Unit must be stopped before Core starts
    assert released_idx < core_start_idx


@pytest.mark.usefixtures("core_start_base_mocks")
async def test_start_skips_port_reservation_when_core_already_running(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
):
    """When Core is already running (Supervisor restart), no reservation unit is created."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.StartTransientUnit.calls.clear()

    with patch.object(
        coresys.homeassistant.core,
        "is_running",
        new=AsyncMock(return_value=True),
    ):
        await coresys.core.start()

    assert systemd_service.StartTransientUnit.calls == []


@pytest.mark.usefixtures("core_start_base_mocks")
async def test_start_continues_when_port_reservation_fails(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
):
    """Core boot continues even if the port reservation could not be made."""
    coresys.homeassistant.http_server_host = None

    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.response_start_transient_unit = DBusError(
        ErrorType.FAILED, "unit already exists"
    )

    await coresys.core.start()

    coresys.homeassistant.core.start.assert_awaited_once()


@pytest.mark.usefixtures("core_start_base_mocks")
async def test_start_still_starts_core_when_release_not_confirmed(
    coresys: CoreSys,
):
    """Core is still started even if the reservation release can't be confirmed.

    Core's port is only used for its own API/frontend bind, so failing to
    confirm the release must never stop Core from starting -- worst case
    Core just logs and retries the bind itself, which beats leaving users
    without a running Core at all.
    """
    coresys.homeassistant.http_server_host = None

    orig_release = coresys.core._release_core_port
    release_calls = 0

    async def flaky_release() -> bool:
        nonlocal release_calls
        release_calls += 1
        if release_calls == 1:
            # Pre-cleanup release inside _reserve_core_port succeeds normally
            return await orig_release()
        # The real release before Core starts can't be confirmed
        return False

    with patch.object(coresys.core, "_release_core_port", side_effect=flaky_release):
        await coresys.core.start()

    coresys.homeassistant.core.start.assert_awaited_once()


@pytest.mark.usefixtures("core_start_base_mocks")
async def test_start_cleans_up_stale_active_unit_before_reserving(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
):
    """A reservation unit left active by a previous crashed boot is stopped first.

    Systemd refuses to redefine a transient unit that is still loaded (in any
    state), even with mode=replace, so a unit left active by a Supervisor
    crash must be stopped -- and that stop waited out -- before a new
    reservation can be started under the same name.
    """
    coresys.homeassistant.http_server_host = None

    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_unit_service: SystemdUnitService = all_dbus_services["systemd_unit"]

    # Simulate a leftover unit from a previous crashed boot: GetUnit finds it
    # and it is still active (mock_systemd_unit is already linked by the base
    # fixture so StopUnit/StartTransientUnit flip its ActiveState like real
    # systemd would).
    systemd_service.response_get_unit = SystemdService.response_get_unit
    systemd_unit_service.active_state = "active"
    systemd_service.StopUnit.calls.clear()
    systemd_service.StartTransientUnit.calls.clear()
    systemd_service.ResetFailedUnit.calls.clear()

    await coresys.core.start()

    # The stale unit must have been stopped before the new one was started
    assert (_PORT_RESERVE_UNIT, "replace") in systemd_service.StopUnit.calls
    assert len(systemd_service.StartTransientUnit.calls) == 1
    # It cleanly reached INACTIVE, so there was nothing to reset
    assert systemd_service.ResetFailedUnit.calls == []
    coresys.homeassistant.core.start.assert_awaited_once()


async def test_release_core_port_resets_failed_unit(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
):
    """Releasing a unit that ended up FAILED (not cleanly INACTIVE) resets it.

    Systemd keeps a FAILED unit around until it is explicitly reset, unlike a
    unit that cleanly stops to INACTIVE and is garbage collected on its own.
    """
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_unit_service: SystemdUnitService = all_dbus_services["systemd_unit"]

    # Simulate a unit that is FAILED and stays that way: StopUnit's mock
    # unconditionally flips a *linked* unit to INACTIVE, so leave it unlinked
    # and set the state directly instead, matching a real FAILED unit that
    # ignores a stop request. ResetFailedUnit is also a no-op when unlinked,
    # so the unit never actually clears -- release can't be confirmed.
    systemd_service.response_get_unit = SystemdService.response_get_unit
    systemd_unit_service.active_state = "failed"

    result = await coresys.core._release_core_port()

    assert result is False
    assert (_PORT_RESERVE_UNIT, "replace") in systemd_service.StopUnit.calls
    assert (_PORT_RESERVE_UNIT,) in systemd_service.ResetFailedUnit.calls


async def test_release_core_port_confirms_success_when_unit_goes_inactive(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
):
    """Releasing returns True once both units are confirmed INACTIVE."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_unit_service: SystemdUnitService = all_dbus_services["systemd_unit"]

    systemd_service.response_get_unit = SystemdService.response_get_unit
    systemd_service.mock_systemd_unit = systemd_unit_service
    systemd_unit_service.active_state = "active"

    result = await coresys.core._release_core_port()

    assert result is True


async def test_reserve_core_port_skips_when_dbus_not_connected(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
):
    """No reservation is attempted if systemd D-Bus is not connected."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.StartTransientUnit.calls.clear()

    with patch.object(coresys.dbus.systemd, "dbus", None):
        result = await coresys.core._reserve_core_port(["0.0.0.0"], 8123)

    assert result is False
    assert systemd_service.StartTransientUnit.calls == []


async def test_release_core_port_skips_when_dbus_not_connected(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
):
    """Releasing is a cheap no-op (confirmed released) if systemd D-Bus is not connected."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.StopUnit.calls.clear()

    with patch.object(coresys.dbus.systemd, "dbus", None):
        result = await coresys.core._release_core_port()

    assert result is True
    assert systemd_service.StopUnit.calls == []


async def test_reserve_core_port_returns_false_when_unit_ends_up_failed(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
):
    """If the unit is created but ends up FAILED rather than ACTIVE, fail cleanly.

    This can happen if the port turns out to already be bound by something
    else outside Supervisor's knowledge: systemd creates the unit but it
    immediately fails to actually claim the socket.
    """
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_unit_service: SystemdUnitService = all_dbus_services["systemd_unit"]

    # First two GetUnit calls are the pre-cleanup check (one per unit) on a
    # clean/fresh boot -- neither exists yet. The next GetUnit call is the
    # post-creation poll for the newly created socket unit, which ends up
    # FAILED rather than ACTIVE. Leave mock_systemd_unit unlinked so
    # StartTransientUnit's mock doesn't overwrite ActiveState back to
    # "active" after we set it.
    systemd_service.response_get_unit = [
        DBusError(DBUS_ERR_SYSTEMD_NO_SUCH_UNIT, "no such unit"),
        DBusError(DBUS_ERR_SYSTEMD_NO_SUCH_UNIT, "no such unit"),
    ] + [SystemdService.response_get_unit] * 5
    systemd_unit_service.active_state = "failed"
    systemd_service.StartTransientUnit.calls.clear()

    result = await coresys.core._reserve_core_port(["0.0.0.0"], 8123)

    assert result is False
    assert len(systemd_service.StartTransientUnit.calls) == 1


async def test_reserve_core_port_handles_dbus_disconnect_mid_call(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
):
    """A mid-call D-Bus disconnect is treated as a non-fatal reservation failure.

    DBusNotConnectedError is not a DBusError subclass -- it's raised directly
    by the dbus_connected decorator when the bus drops after the initial
    is_connected check passed -- so it must be caught via the broader
    HassioError, or it would propagate and abort Supervisor startup.
    """
    systemd_service: SystemdService = all_dbus_services["systemd"]
    # Pre-cleanup finds nothing on both units (clean/fresh boot); the
    # disconnect happens on the create attempt itself.
    systemd_service.response_get_unit = DBusError(
        DBUS_ERR_SYSTEMD_NO_SUCH_UNIT, "no such unit"
    )

    with patch.object(
        coresys.dbus.systemd,
        "start_transient_unit",
        side_effect=DBusNotConnectedError(),
    ):
        result = await coresys.core._reserve_core_port(["0.0.0.0"], 8123)

    assert result is False


async def test_release_core_port_handles_dbus_disconnect_mid_call(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
):
    """A mid-call D-Bus disconnect while stopping a unit does not propagate."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.response_get_unit = SystemdService.response_get_unit

    # mock_systemd_unit is left unlinked, so the unit's ActiveState never
    # actually moves off the "active" default -- shorten the wait so the
    # test doesn't block for the real _PORT_RESERVE_TIMEOUT (10s).
    with (
        patch("supervisor.core._PORT_RESERVE_TIMEOUT", 0.01),
        patch.object(
            coresys.dbus.systemd,
            "stop_unit",
            side_effect=DBusNotConnectedError(),
        ),
    ):
        result = await coresys.core._release_core_port()

    assert result is False
