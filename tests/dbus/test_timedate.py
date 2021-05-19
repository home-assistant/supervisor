"""Test TimeDate dbus interface."""
from datetime import datetime, timezone

import pytest

from supervisor.coresys import CoreSys
from supervisor.exceptions import DBusNotConnectedError


async def test_dbus_timezone(coresys: CoreSys):
    """Test coresys dbus connection."""
    assert coresys.dbus.timedate.dt_utc is None

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
    test_dt = datetime(2021, 5, 19, 8, 36, 54, 405718, tzinfo=timezone.utc)

    with pytest.raises(DBusNotConnectedError):
        await coresys.dbus.timedate.set_time(test_dt)

    await coresys.dbus.timedate.connect()

    await coresys.dbus.timedate.set_time(test_dt)


async def test_dbus_setntp(coresys: CoreSys):
    """Disable NTP on backend."""
    with pytest.raises(DBusNotConnectedError):
        await coresys.dbus.timedate.set_ntp(False)

    await coresys.dbus.timedate.connect()

    await coresys.dbus.timedate.set_ntp(False)
