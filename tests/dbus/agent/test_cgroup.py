"""Test CGroup/Agent dbus interface."""

import pytest

from supervisor.coresys import CoreSys
from supervisor.exceptions import DBusNotConnectedError


async def test_dbus_osagent_cgroup_add_devices(coresys: CoreSys, dbus: list[str]):
    """Test wipe data partition on host."""

    with pytest.raises(DBusNotConnectedError):
        await coresys.dbus.agent.cgroup.add_devices_allowed("9324kl23j4kl", "*:* rwm")

    await coresys.dbus.agent.connect()

    dbus.clear()
    assert (
        await coresys.dbus.agent.cgroup.add_devices_allowed("9324kl23j4kl", "*:* rwm")
        is None
    )
    assert dbus == ["/io/hass/os/CGroup-io.hass.os.CGroup.AddDevicesAllowed"]
