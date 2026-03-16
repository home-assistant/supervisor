"""Testing handling with CoreState."""

# pylint: disable=W0212
import asyncio
import datetime
import errno
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

import pytest

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.exceptions import WhoamiSSLError
from supervisor.host.control import SystemControl
from supervisor.host.info import InfoCenter
from supervisor.resolution.const import IssueType, SuggestionType
from supervisor.supervisor import Supervisor
from supervisor.utils.whoami import WhoamiData

from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.systemd import Systemd as SystemdService


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
        patch.object(Supervisor, "check_connectivity") as mock_check_connectivity,
    ):
        await coresys.core._adjust_system_datetime()
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


async def test_shutdown_reentrant_waits(coresys: CoreSys):
    """Test that concurrent shutdown calls wait for the first to complete."""
    call_count = 0
    shutdown_started = asyncio.Event()
    proceed = asyncio.Event()

    original_shutdown = coresys.addons.shutdown

    async def slow_addon_shutdown(startup):
        nonlocal call_count
        call_count += 1
        shutdown_started.set()
        await proceed.wait()
        return await original_shutdown(startup)

    await coresys.core.set_state(CoreState.RUNNING)

    with patch.object(coresys.addons, "shutdown", side_effect=slow_addon_shutdown):
        # Start first shutdown
        task1 = asyncio.create_task(coresys.core.shutdown())
        await shutdown_started.wait()

        # Second call should wait, not start a new shutdown
        task2 = asyncio.create_task(coresys.core.shutdown())
        await asyncio.sleep(0.05)

        # Let the shutdown proceed
        proceed.set()

        await asyncio.gather(task1, task2)

    # Addon shutdown was only called by the first shutdown (4 startup levels)
    assert call_count == 4
    assert coresys.core._shutdown_event.is_set()


async def test_shutdown_event_reset_between_cycles(coresys: CoreSys):
    """Test that shutdown event is reset for repeated shutdown cycles (e.g. backup restore)."""
    await coresys.core.set_state(CoreState.FREEZE)

    # First shutdown cycle
    await coresys.core.shutdown()
    assert coresys.core._shutdown_event.is_set()

    # Simulate backup restore returning to RUNNING
    await coresys.core.set_state(CoreState.RUNNING)

    # Second shutdown cycle should work (event was cleared)
    second_entered = False

    original_shutdown = coresys.addons.shutdown

    async def track_addon_shutdown(startup):
        nonlocal second_entered
        second_entered = True
        return await original_shutdown(startup)

    with patch.object(coresys.addons, "shutdown", side_effect=track_addon_shutdown):
        await coresys.core.shutdown()

    assert second_entered
    assert coresys.core._shutdown_event.is_set()


@pytest.mark.parametrize(
    "state", [CoreState.STOPPING, CoreState.CLOSE], ids=["stopping", "close"]
)
async def test_shutdown_ignored_during_stop(
    coresys: CoreSys, caplog: pytest.LogCaptureFixture, state: CoreState
):
    """Test that shutdown is ignored when Supervisor is already stopping."""
    await coresys.core.set_state(state)

    with patch.object(coresys.addons, "shutdown") as mock_addon_shutdown:
        await coresys.core.shutdown()

    mock_addon_shutdown.assert_not_called()
    assert "Ignoring shutdown request, Supervisor is already stopping" in caplog.text
