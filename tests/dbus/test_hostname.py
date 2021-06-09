"""Test hostname dbus interface."""

import pytest

from supervisor.coresys import CoreSys
from supervisor.exceptions import DBusNotConnectedError


async def test_dbus_hostname_info(coresys: CoreSys):
    """Test coresys dbus connection."""
    assert coresys.dbus.hostname.hostname is None

    await coresys.dbus.hostname.connect()
    await coresys.dbus.hostname.update()

    assert coresys.dbus.hostname.hostname == "homeassistant-n2"
    assert coresys.dbus.hostname.kernel == "5.10.33"
    assert (
        coresys.dbus.hostname.cpe
        == "cpe:2.3:o:home-assistant:haos:6.0.dev20210504:*:development:*:*:*:odroid-n2:*"
    )
    assert coresys.dbus.hostname.operating_system == "Home Assistant OS 6.0.dev20210504"


async def test_dbus_sethostname(coresys: CoreSys):
    """Set hostname on backend."""

    with pytest.raises(DBusNotConnectedError):
        await coresys.dbus.hostname.set_static_hostname("StarWars")

    await coresys.dbus.hostname.connect()

    await coresys.dbus.hostname.set_static_hostname("StarWars")
