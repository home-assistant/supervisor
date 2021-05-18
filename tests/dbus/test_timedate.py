"""Test TimeDate dbus interface."""

from supervisor.coresys import CoreSys


async def test_dbus_timezone(coresys: CoreSys):
    """Test coresys dbus connection."""
    await coresys.dbus.timedate.connect()
