"""Test hostname dbus interface."""

from supervisor.coresys import CoreSys


async def test_dbus_systemd_info(coresys: CoreSys):
    """Test coresys dbus connection."""
    assert coresys.dbus.systemd.boot_timestamp is None
    assert coresys.dbus.systemd.startup_time is None

    await coresys.dbus.systemd.connect()
    await coresys.dbus.systemd.update()

    assert coresys.dbus.systemd.boot_timestamp == 1632236713344227
    assert coresys.dbus.systemd.startup_time == 45.304696
