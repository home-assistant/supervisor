"""Test host control."""

import asyncio

from supervisor.coresys import CoreSys

from tests.common import fire_property_change_signal


async def test_set_hostname(coresys: CoreSys, dbus: list[str]):
    """Test set hostname."""
    await coresys.dbus.hostname.connect(coresys.dbus.bus)

    assert coresys.dbus.hostname.hostname == "homeassistant-n2"

    dbus.clear()
    await coresys.host.control.set_hostname("test")
    assert dbus == [
        "/org/freedesktop/hostname1-org.freedesktop.hostname1.SetStaticHostname"
    ]

    await fire_property_change_signal(coresys.dbus.hostname, {"StaticHostname": "test"})
    await asyncio.sleep(0)
    assert coresys.dbus.hostname.hostname == "test"
