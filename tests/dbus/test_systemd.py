"""Test hostname dbus interface."""

from unittest.mock import patch

import pytest

from supervisor.coresys import CoreSys
from supervisor.dbus.const import DBUS_NAME_SYSTEMD
from supervisor.exceptions import DBusNotConnectedError

from tests.common import load_json_fixture


async def test_dbus_systemd_info(coresys: CoreSys):
    """Test coresys dbus connection."""
    assert coresys.dbus.systemd.boot_timestamp is None
    assert coresys.dbus.systemd.startup_time is None

    await coresys.dbus.systemd.connect(coresys.dbus.bus)

    async def mock_get_properties(dbus_obj, interface):
        return load_json_fixture(
            f"{DBUS_NAME_SYSTEMD.replace('.', '_')}_properties.json"
        )

    with patch("supervisor.utils.dbus.DBus.get_properties", new=mock_get_properties):
        await coresys.dbus.systemd.update()

    assert coresys.dbus.systemd.boot_timestamp == 1632236713344227
    assert coresys.dbus.systemd.startup_time == 45.304696


async def test_reboot(coresys: CoreSys, dbus: list[str]):
    """Test reboot."""
    with pytest.raises(DBusNotConnectedError):
        await coresys.dbus.systemd.reboot()

    await coresys.dbus.systemd.connect(coresys.dbus.bus)

    dbus.clear()
    assert await coresys.dbus.systemd.reboot() is None
    assert dbus == ["/org/freedesktop/systemd1-org.freedesktop.systemd1.Manager.Reboot"]


async def test_power_off(coresys: CoreSys, dbus: list[str]):
    """Test power off."""
    with pytest.raises(DBusNotConnectedError):
        await coresys.dbus.systemd.power_off()

    await coresys.dbus.systemd.connect(coresys.dbus.bus)

    dbus.clear()
    assert await coresys.dbus.systemd.power_off() is None
    assert dbus == [
        "/org/freedesktop/systemd1-org.freedesktop.systemd1.Manager.PowerOff"
    ]


async def test_start_unit(coresys: CoreSys, dbus: list[str]):
    """Test start unit."""
    with pytest.raises(DBusNotConnectedError):
        await coresys.dbus.systemd.start_unit("test_unit", "replace")

    await coresys.dbus.systemd.connect(coresys.dbus.bus)

    dbus.clear()
    assert (
        await coresys.dbus.systemd.start_unit("test_unit", "replace")
        == "/org/freedesktop/systemd1/job/7623"
    )
    assert dbus == [
        "/org/freedesktop/systemd1-org.freedesktop.systemd1.Manager.StartUnit"
    ]


async def test_stop_unit(coresys: CoreSys, dbus: list[str]):
    """Test stop unit."""
    with pytest.raises(DBusNotConnectedError):
        await coresys.dbus.systemd.stop_unit("test_unit", "replace")

    await coresys.dbus.systemd.connect(coresys.dbus.bus)

    dbus.clear()
    assert (
        await coresys.dbus.systemd.stop_unit("test_unit", "replace")
        == "/org/freedesktop/systemd1/job/7623"
    )
    assert dbus == [
        "/org/freedesktop/systemd1-org.freedesktop.systemd1.Manager.StopUnit"
    ]


async def test_restart_unit(coresys: CoreSys, dbus: list[str]):
    """Test restart unit."""
    with pytest.raises(DBusNotConnectedError):
        await coresys.dbus.systemd.restart_unit("test_unit", "replace")

    await coresys.dbus.systemd.connect(coresys.dbus.bus)

    dbus.clear()
    assert (
        await coresys.dbus.systemd.restart_unit("test_unit", "replace")
        == "/org/freedesktop/systemd1/job/7623"
    )
    assert dbus == [
        "/org/freedesktop/systemd1-org.freedesktop.systemd1.Manager.RestartUnit"
    ]


async def test_reload_unit(coresys: CoreSys, dbus: list[str]):
    """Test reload unit."""
    with pytest.raises(DBusNotConnectedError):
        await coresys.dbus.systemd.reload_unit("test_unit", "replace")

    await coresys.dbus.systemd.connect(coresys.dbus.bus)

    dbus.clear()
    assert (
        await coresys.dbus.systemd.reload_unit("test_unit", "replace")
        == "/org/freedesktop/systemd1/job/7623"
    )
    assert dbus == [
        "/org/freedesktop/systemd1-org.freedesktop.systemd1.Manager.ReloadOrRestartUnit"
    ]


async def test_list_units(coresys: CoreSys, dbus: list[str]):
    """Test list units."""
    with pytest.raises(DBusNotConnectedError):
        await coresys.dbus.systemd.list_units()

    await coresys.dbus.systemd.connect(coresys.dbus.bus)

    dbus.clear()
    units = await coresys.dbus.systemd.list_units()
    assert len(units) == 4
    assert units[1][0] == "firewalld.service"
    assert units[1][2] == "not-found"
    assert units[3][0] == "zram-swap.service"
    assert units[3][2] == "loaded"
    assert dbus == [
        "/org/freedesktop/systemd1-org.freedesktop.systemd1.Manager.ListUnits"
    ]
