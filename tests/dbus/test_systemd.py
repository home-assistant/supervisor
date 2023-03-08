"""Test hostname dbus interface."""
# pylint: disable=import-error
from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.systemd import Systemd
from supervisor.exceptions import DBusNotConnectedError

from tests.common import mock_dbus_services
from tests.dbus_service_mocks.systemd import Systemd as SystemdService


@pytest.fixture(name="systemd_service", autouse=True)
async def fixture_systemd_service(dbus_session_bus: MessageBus) -> SystemdService:
    """Mock systemd dbus service."""
    yield (await mock_dbus_services({"systemd": None}, dbus_session_bus))["systemd"]


async def test_dbus_systemd_info(dbus_session_bus: MessageBus):
    """Test systemd properties."""
    systemd = Systemd()

    assert systemd.boot_timestamp is None
    assert systemd.startup_time is None

    await systemd.connect(dbus_session_bus)

    assert systemd.boot_timestamp == 1632236713344227
    assert systemd.startup_time == 45.304696


async def test_reboot(systemd_service: SystemdService, dbus_session_bus: MessageBus):
    """Test reboot."""
    systemd = Systemd()

    with pytest.raises(DBusNotConnectedError):
        await systemd.reboot()

    await systemd.connect(dbus_session_bus)

    assert await systemd.reboot() is None
    assert systemd_service.Reboot.calls == [tuple()]


async def test_power_off(systemd_service: SystemdService, dbus_session_bus: MessageBus):
    """Test power off."""
    systemd = Systemd()

    with pytest.raises(DBusNotConnectedError):
        await systemd.power_off()

    await systemd.connect(dbus_session_bus)

    assert await systemd.power_off() is None
    assert systemd_service.PowerOff.calls == [tuple()]


async def test_start_unit(
    systemd_service: SystemdService, dbus_session_bus: MessageBus
):
    """Test start unit."""
    systemd = Systemd()

    with pytest.raises(DBusNotConnectedError):
        await systemd.start_unit("test_unit", "replace")

    await systemd.connect(dbus_session_bus)

    assert (
        await systemd.start_unit("test_unit", "replace")
        == "/org/freedesktop/systemd1/job/7623"
    )
    assert systemd_service.StartUnit.calls == [("test_unit", "replace")]


async def test_stop_unit(systemd_service: SystemdService, dbus_session_bus: MessageBus):
    """Test stop unit."""
    systemd = Systemd()

    with pytest.raises(DBusNotConnectedError):
        await systemd.stop_unit("test_unit", "replace")

    await systemd.connect(dbus_session_bus)

    assert (
        await systemd.stop_unit("test_unit", "replace")
        == "/org/freedesktop/systemd1/job/7623"
    )
    assert systemd_service.StopUnit.calls == [("test_unit", "replace")]


async def test_restart_unit(
    systemd_service: SystemdService, dbus_session_bus: MessageBus
):
    """Test restart unit."""
    systemd = Systemd()

    with pytest.raises(DBusNotConnectedError):
        await systemd.restart_unit("test_unit", "replace")

    await systemd.connect(dbus_session_bus)

    assert (
        await systemd.restart_unit("test_unit", "replace")
        == "/org/freedesktop/systemd1/job/7623"
    )
    assert systemd_service.RestartUnit.calls == [("test_unit", "replace")]


async def test_reload_unit(
    systemd_service: SystemdService, dbus_session_bus: MessageBus
):
    """Test reload unit."""
    systemd = Systemd()

    with pytest.raises(DBusNotConnectedError):
        await systemd.reload_unit("test_unit", "replace")

    await systemd.connect(dbus_session_bus)

    assert (
        await systemd.reload_unit("test_unit", "replace")
        == "/org/freedesktop/systemd1/job/7623"
    )
    assert systemd_service.ReloadOrRestartUnit.calls == [("test_unit", "replace")]


async def test_list_units(dbus_session_bus: MessageBus):
    """Test list units."""
    systemd = Systemd()

    with pytest.raises(DBusNotConnectedError):
        await systemd.list_units()

    await systemd.connect(dbus_session_bus)

    units = await systemd.list_units()
    assert len(units) == 4
    assert units[1][0] == "firewalld.service"
    assert units[1][2] == "not-found"
    assert units[3][0] == "zram-swap.service"
    assert units[3][2] == "loaded"
