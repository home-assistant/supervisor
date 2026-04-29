"""Testing handling with CoreState."""

# pylint: disable=W0212
import asyncio
import datetime
import errno
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

import pytest

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.exceptions import AppFileReadError, HassioError, WhoamiSSLError
from supervisor.host.control import SystemControl
from supervisor.host.info import InfoCenter
from supervisor.resolution.const import IssueType, SuggestionType, UnhealthyReason
from supervisor.supervisor import Supervisor
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
        await asyncio.sleep(0.1)
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
