"""Test login dbus interface."""
import pytest

from supervisor.coresys import CoreSys
from supervisor.exceptions import DBusNotConnectedError


async def test_reboot(coresys: CoreSys, dbus: list[str]):
    """Test reboot."""
    with pytest.raises(DBusNotConnectedError):
        await coresys.dbus.logind.reboot()

    await coresys.dbus.logind.connect()

    dbus.clear()
    assert await coresys.dbus.logind.reboot() is None
    assert dbus == ["/org/freedesktop/login1-org.freedesktop.login1.Manager.Reboot"]


async def test_power_off(coresys: CoreSys, dbus: list[str]):
    """Test power off."""
    with pytest.raises(DBusNotConnectedError):
        await coresys.dbus.logind.power_off()

    await coresys.dbus.logind.connect()

    dbus.clear()
    assert await coresys.dbus.logind.power_off() is None
    assert dbus == ["/org/freedesktop/login1-org.freedesktop.login1.Manager.PowerOff"]
