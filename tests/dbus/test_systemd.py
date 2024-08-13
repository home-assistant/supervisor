"""Test hostname dbus interface."""

# pylint: disable=import-error
from dbus_fast import DBusError, Variant
from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.const import StartUnitMode, StopUnitMode, UnitActiveState
from supervisor.dbus.systemd import Systemd
from supervisor.exceptions import DBusNotConnectedError, DBusSystemdNoSuchUnit

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
    systemd_service.Reboot.calls.clear()
    systemd = Systemd()

    with pytest.raises(DBusNotConnectedError):
        await systemd.reboot()

    await systemd.connect(dbus_session_bus)

    assert await systemd.reboot() is None
    assert systemd_service.Reboot.calls == [()]


async def test_power_off(systemd_service: SystemdService, dbus_session_bus: MessageBus):
    """Test power off."""
    systemd_service.PowerOff.calls.clear()
    systemd = Systemd()

    with pytest.raises(DBusNotConnectedError):
        await systemd.power_off()

    await systemd.connect(dbus_session_bus)

    assert await systemd.power_off() is None
    assert systemd_service.PowerOff.calls == [()]


async def test_start_unit(
    systemd_service: SystemdService, dbus_session_bus: MessageBus
):
    """Test start unit."""
    systemd_service.StartUnit.calls.clear()
    systemd = Systemd()

    with pytest.raises(DBusNotConnectedError):
        await systemd.start_unit("test_unit", StartUnitMode.REPLACE)

    await systemd.connect(dbus_session_bus)

    assert (
        await systemd.start_unit("test_unit", StartUnitMode.REPLACE)
        == "/org/freedesktop/systemd1/job/7623"
    )
    assert systemd_service.StartUnit.calls == [("test_unit", "replace")]


async def test_stop_unit(systemd_service: SystemdService, dbus_session_bus: MessageBus):
    """Test stop unit."""
    systemd_service.StopUnit.calls.clear()
    systemd = Systemd()

    with pytest.raises(DBusNotConnectedError):
        await systemd.stop_unit("test_unit", StopUnitMode.REPLACE)

    await systemd.connect(dbus_session_bus)

    assert (
        await systemd.stop_unit("test_unit", StopUnitMode.REPLACE)
        == "/org/freedesktop/systemd1/job/7623"
    )
    assert systemd_service.StopUnit.calls == [("test_unit", "replace")]


async def test_restart_unit(
    systemd_service: SystemdService, dbus_session_bus: MessageBus
):
    """Test restart unit."""
    systemd_service.RestartUnit.calls.clear()
    systemd = Systemd()

    with pytest.raises(DBusNotConnectedError):
        await systemd.restart_unit("test_unit", StartUnitMode.REPLACE)

    await systemd.connect(dbus_session_bus)

    assert (
        await systemd.restart_unit("test_unit", StartUnitMode.REPLACE)
        == "/org/freedesktop/systemd1/job/7623"
    )
    assert systemd_service.RestartUnit.calls == [("test_unit", "replace")]


async def test_reload_unit(
    systemd_service: SystemdService, dbus_session_bus: MessageBus
):
    """Test reload unit."""
    systemd_service.ReloadOrRestartUnit.calls.clear()
    systemd = Systemd()

    with pytest.raises(DBusNotConnectedError):
        await systemd.reload_unit("test_unit", StartUnitMode.REPLACE)

    await systemd.connect(dbus_session_bus)

    assert (
        await systemd.reload_unit("test_unit", StartUnitMode.REPLACE)
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


async def test_start_transient_unit(
    systemd_service: SystemdService, dbus_session_bus: MessageBus
):
    """Test start transient unit."""
    systemd_service.StartTransientUnit.calls.clear()
    systemd = Systemd()

    with pytest.raises(DBusNotConnectedError):
        await systemd.start_transient_unit(
            "tmp-test.mount",
            StartUnitMode.FAIL,
            [],
        )

    await systemd.connect(dbus_session_bus)

    assert (
        await systemd.start_transient_unit(
            "tmp-test.mount",
            StartUnitMode.FAIL,
            [
                ("Description", Variant("s", "Test")),
                ("What", Variant("s", "//homeassistant/config")),
                ("Type", Variant("s", "cifs")),
                ("Options", Variant("s", "username=homeassistant,password=password")),
            ],
        )
        == "/org/freedesktop/systemd1/job/7623"
    )
    assert systemd_service.StartTransientUnit.calls == [
        (
            "tmp-test.mount",
            "fail",
            [
                ["Description", Variant("s", "Test")],
                ["What", Variant("s", "//homeassistant/config")],
                ["Type", Variant("s", "cifs")],
                ["Options", Variant("s", "username=homeassistant,password=password")],
            ],
            [],
        )
    ]


async def test_reset_failed_unit(
    systemd_service: SystemdService, dbus_session_bus: MessageBus
):
    """Test resetting a failed unit."""
    systemd_service.ResetFailedUnit.calls.clear()
    systemd = Systemd()

    with pytest.raises(DBusNotConnectedError):
        await systemd.reset_failed_unit("tmp-test.mount")

    await systemd.connect(dbus_session_bus)

    assert await systemd.reset_failed_unit("tmp-test.mount") is None
    assert systemd_service.ResetFailedUnit.calls == [("tmp-test.mount",)]


async def test_get_unit(systemd_service: SystemdService, dbus_session_bus: MessageBus):
    """Test getting job ID for unit."""
    await mock_dbus_services(
        {"systemd_unit": "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount"},
        dbus_session_bus,
    )
    systemd_service.GetUnit.calls.clear()
    systemd = Systemd()

    with pytest.raises(DBusNotConnectedError):
        await systemd.get_unit("tmp-test.mount")

    await systemd.connect(dbus_session_bus)

    unit = await systemd.get_unit("tmp-test.mount")
    assert unit.bus_name == "org.freedesktop.systemd1"
    assert unit.object_path == "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount"
    assert await unit.get_active_state() == UnitActiveState.ACTIVE
    assert systemd_service.GetUnit.calls == [("tmp-test.mount",)]


async def test_get_unit_not_found(
    systemd_service: SystemdService, dbus_session_bus: MessageBus
):
    """Test error for non-existent unit name."""
    systemd_service.response_get_unit = DBusError(
        "org.freedesktop.systemd1.NoSuchUnit", "error"
    )

    systemd = Systemd()
    await systemd.connect(dbus_session_bus)

    with pytest.raises(DBusSystemdNoSuchUnit):
        await systemd.get_unit("error.mount")
