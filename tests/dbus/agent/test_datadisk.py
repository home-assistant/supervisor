"""Test Datadisk/Agent dbus interface."""
from pathlib import Path

import pytest

from supervisor.coresys import CoreSys
from supervisor.exceptions import DBusNotConnectedError


async def test_dbus_osagent_datadisk(coresys: CoreSys):
    """Test coresys dbus connection."""
    assert coresys.dbus.agent.datadisk.current_device is None

    await coresys.dbus.agent.connect()
    await coresys.dbus.agent.update()

    assert coresys.dbus.agent.datadisk.current_device.as_posix() == "/dev/sda"


async def test_dbus_osagent_datadisk_change_device(coresys: CoreSys):
    """Change datadisk on device."""

    with pytest.raises(DBusNotConnectedError):
        await coresys.dbus.agent.datadisk.change_device(Path("/dev/sdb"))

    await coresys.dbus.agent.connect()

    assert await coresys.dbus.agent.datadisk.change_device(Path("/dev/sdb")) is None
