"""Test host manager."""

import asyncio
import os
from unittest.mock import AsyncMock, PropertyMock, patch

from awesomeversion import AwesomeVersion
import pytest

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.dbus.const import MulticastProtocolEnabled
from supervisor.exceptions import DBusError

from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.logind import Logind as LogindService
from tests.dbus_service_mocks.rauc import Rauc as RaucService
from tests.dbus_service_mocks.systemd import Systemd as SystemdService


@pytest.fixture(name="logind_service")
async def fixture_logind_service(
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
) -> LogindService:
    """Return logind service mock."""
    yield all_dbus_services["logind"]


@pytest.fixture(name="systemd_service")
async def fixture_systemd_service(
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
) -> SystemdService:
    """Return systemd service mock."""
    yield all_dbus_services["systemd"]


async def test_load(coresys: CoreSys, systemd_service: SystemdService):
    """Test manager load."""
    systemd_service.ListUnits.calls.clear()

    with patch.object(coresys.host.sound, "update") as sound_update:
        await coresys.host.load()

        assert coresys.dbus.hostname.hostname == "homeassistant-n2"
        assert coresys.dbus.systemd.boot_timestamp == 1632236713344227
        assert coresys.dbus.timedate.timezone == "Etc/UTC"
        assert coresys.dbus.agent.diagnostics is True
        assert coresys.dbus.network.connectivity_enabled is True
        assert coresys.dbus.resolved.multicast_dns == MulticastProtocolEnabled.RESOLVE
        assert coresys.dbus.agent.apparmor.version == "2.13.2"
        assert len(coresys.host.logs.default_identifiers) > 0
        assert coresys.dbus.udisks2.version == AwesomeVersion("2.9.2")

        sound_update.assert_called_once()

    assert systemd_service.ListUnits.calls == [()]


async def test_reload(coresys: CoreSys, systemd_service: SystemdService):
    """Test manager reload and ensure it does not unnecessarily recreate dbus objects."""
    await coresys.host.load()
    systemd_service.ListUnits.calls.clear()

    with (
        patch("supervisor.utils.dbus.DBus.connect") as connect,
        patch.object(coresys.host.sound, "update") as sound_update,
    ):
        await coresys.host.reload()

        connect.assert_not_called()
        sound_update.assert_called_once()

    assert systemd_service.ListUnits.calls == [()]


async def test_reload_os(
    coresys: CoreSys, all_dbus_services: dict[str, DBusServiceMock], os_available
):
    """Test manager reload while on OS also reloads OS info cache."""
    rauc_service: RaucService = all_dbus_services["rauc"]
    rauc_service.GetSlotStatus.calls.clear()

    await coresys.host.load()
    await coresys.host.reload()

    assert rauc_service.GetSlotStatus.calls == [()]


async def test_host_shutdown_on_prepare_for_shutdown_signal(
    coresys: CoreSys, logind_service: LogindService
):
    """Test graceful shutdown when PrepareForShutdown signal is received."""
    shutdown_called = asyncio.Event()

    async def mock_shutdown(**kwargs):
        shutdown_called.set()

    await coresys.host.load()
    await coresys.core.set_state(CoreState.RUNNING)

    # Give the monitor task time to start and register the signal listener
    # (needs multiple yields for inhibit D-Bus call + AddMatch call)
    await asyncio.sleep(0.1)

    with patch.object(coresys.core, "shutdown", side_effect=mock_shutdown):
        # Emit PrepareForShutdown(true) signal as if host is shutting down
        logind_service.PrepareForShutdown()
        await logind_service.ping()

        async with asyncio.timeout(2):
            await shutdown_called.wait()


async def test_host_shutdown_signal_reentrant(
    coresys: CoreSys, logind_service: LogindService
):
    """Test PrepareForShutdown during in-progress shutdown awaits same shutdown."""
    shutdown_called = asyncio.Event()

    async def mock_shutdown(**kwargs):
        shutdown_called.set()

    await coresys.host.load()
    await coresys.core.set_state(CoreState.SHUTDOWN)

    # Give the monitor task time to start and register the signal listener
    await asyncio.sleep(0.1)

    with patch.object(coresys.core, "shutdown", side_effect=mock_shutdown):
        logind_service.PrepareForShutdown()
        await logind_service.ping()

        # shutdown() is called reentrantly - it awaits the in-progress shutdown
        async with asyncio.timeout(2):
            await shutdown_called.wait()


async def test_host_unload_cancels_monitor_task(
    coresys: CoreSys, logind_service: LogindService
):
    """Test unload cancels the shutdown monitor task."""
    await coresys.host.load()
    await asyncio.sleep(0.1)

    assert coresys.host._shutdown_monitor_task is not None
    assert not coresys.host._shutdown_monitor_task.done()

    await coresys.host.unload()

    assert coresys.host._shutdown_monitor_task is None


async def test_host_unload_no_monitor_task(coresys: CoreSys):
    """Test unload when no monitor task was started."""
    # Don't call load(), so no monitor task exists
    assert coresys.host._shutdown_monitor_task is None
    await coresys.host.unload()
    assert coresys.host._shutdown_monitor_task is None


async def test_monitor_inhibit_lock_failure(
    coresys: CoreSys,
    logind_service: LogindService,
    caplog: pytest.LogCaptureFixture,
):
    """Test monitor task logs warning when inhibit lock fails."""
    with patch.object(
        coresys.dbus.logind, "inhibit", side_effect=DBusError("test error")
    ):
        await coresys.host.load()
        await asyncio.sleep(0.1)

    assert "Could not take shutdown inhibitor lock from logind" in caplog.text


async def test_monitor_dbus_error_during_signal_wait(
    coresys: CoreSys,
    logind_service: LogindService,
    caplog: pytest.LogCaptureFixture,
):
    """Test monitor task handles D-Bus errors during signal monitoring."""
    with patch.object(
        coresys.dbus.logind,
        "prepare_for_shutdown",
        side_effect=DBusError("connection lost"),
    ):
        await coresys.host.load()
        await asyncio.sleep(0.1)

    assert "Error monitoring host shutdown signal" in caplog.text


async def test_inhibitor_lock_released_after_shutdown(
    coresys: CoreSys,
    logind_service: LogindService,
    caplog: pytest.LogCaptureFixture,
):
    """Test that the inhibitor lock FD is closed after shutdown completes."""
    # Mock inhibit to return a real FD (session bus doesn't negotiate unix FDs)
    r_fd, w_fd = os.pipe()
    os.close(w_fd)

    with patch.object(
        coresys.dbus.logind, "inhibit", new_callable=AsyncMock, return_value=r_fd
    ):
        await coresys.host.load()
        await asyncio.sleep(0.1)

    await coresys.core.set_state(CoreState.RUNNING)

    with patch.object(coresys.core, "shutdown", new_callable=AsyncMock):
        logind_service.PrepareForShutdown()
        await logind_service.ping()
        await asyncio.sleep(0.2)

    assert "Shutdown inhibitor lock released" in caplog.text


async def test_no_monitor_task_without_logind(coresys: CoreSys):
    """Test no monitor task is started when logind is not connected."""
    with patch.object(
        type(coresys.dbus.logind),
        "is_connected",
        new_callable=PropertyMock,
        return_value=False,
    ):
        await coresys.host.load()

    assert coresys.host._shutdown_monitor_task is None
