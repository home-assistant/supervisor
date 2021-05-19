"""Test TimeDate dbus interface."""
from datetime import datetime, timezone

from supervisor.coresys import CoreSys


async def test_dbus_timezone(coresys: CoreSys):
    """Test coresys dbus connection."""
    await coresys.dbus.timedate.connect()
    await coresys.dbus.timedate.update()

    assert coresys.dbus.timedate.dt_utc == datetime(
        2021, 5, 19, 8, 36, 54, 405718, tzinfo=timezone.utc
    )

    assert (
        coresys.dbus.timedate.dt_utc.isoformat() == "2021-05-19T08:36:54.405718+00:00"
    )


async def test_dbus_settime(coresys: CoreSys):
    """Set timestamp on backend."""
    await coresys.dbus.timedate.connect()

    dt = datetime(2021, 5, 19, 8, 36, 54, 405718, tzinfo=timezone.utc)
    await coresys.dbus.timedate.set_time(dt)


async def test_dbus_setntp(coresys: CoreSys):
    """Disable NTP on backend."""
    await coresys.dbus.timedate.connect()

    await coresys.dbus.timedate.set_ntp(False)
