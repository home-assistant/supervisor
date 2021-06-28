"""Test System/Agent dbus interface."""

import pytest

from supervisor.coresys import CoreSys
from supervisor.exceptions import DBusNotConnectedError


async def test_dbus_osagent_system_wipe(coresys: CoreSys):
    """Test wipe data partition on host."""

    with pytest.raises(DBusNotConnectedError):
        await coresys.dbus.agent.system.schedule_wipe_device()

    await coresys.dbus.agent.connect()

    assert await coresys.dbus.agent.system.schedule_wipe_device()
