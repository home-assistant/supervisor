"""Test Datadisk/Agent dbus interface."""
import asyncio
from pathlib import Path

import pytest

from supervisor.coresys import CoreSys
from supervisor.exceptions import DBusNotConnectedError

from tests.common import fire_property_change_signal


async def test_dbus_osagent_datadisk(coresys: CoreSys):
    """Test coresys dbus connection."""
    assert coresys.dbus.agent.datadisk.current_device is None

    await coresys.dbus.agent.connect(coresys.dbus.bus)
    await coresys.dbus.agent.update()

    assert coresys.dbus.agent.datadisk.current_device.as_posix() == "/dev/sda"

    fire_property_change_signal(
        coresys.dbus.agent.datadisk, {"CurrentDevice": "/dev/sda1"}
    )
    await asyncio.sleep(0)
    assert coresys.dbus.agent.datadisk.current_device.as_posix() == "/dev/sda1"

    fire_property_change_signal(coresys.dbus.agent.datadisk, {}, ["CurrentDevice"])
    await asyncio.sleep(0)
    assert coresys.dbus.agent.datadisk.current_device.as_posix() == "/dev/sda"


async def test_dbus_osagent_datadisk_change_device(coresys: CoreSys, dbus: list[str]):
    """Change datadisk on device."""
    with pytest.raises(DBusNotConnectedError):
        await coresys.dbus.agent.datadisk.change_device(Path("/dev/sdb"))

    await coresys.dbus.agent.connect(coresys.dbus.bus)

    dbus.clear()
    assert await coresys.dbus.agent.datadisk.change_device(Path("/dev/sdb")) is None
    assert dbus == ["/io/hass/os/DataDisk-io.hass.os.DataDisk.ChangeDevice"]


async def test_dbus_osagent_datadisk_reload_device(coresys: CoreSys, dbus: list[str]):
    """Change datadisk on device."""
    with pytest.raises(DBusNotConnectedError):
        await coresys.dbus.agent.datadisk.reload_device()

    await coresys.dbus.agent.connect(coresys.dbus.bus)

    dbus.clear()
    assert await coresys.dbus.agent.datadisk.reload_device() is None
    assert dbus == ["/io/hass/os/DataDisk-io.hass.os.DataDisk.ReloadDevice"]
