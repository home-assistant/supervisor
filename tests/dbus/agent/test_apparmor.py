"""Test AppArmor/Agent dbus interface."""
import asyncio
from pathlib import Path

import pytest

from supervisor.coresys import CoreSys
from supervisor.exceptions import DBusNotConnectedError

from tests.common import fire_property_change_signal


async def test_dbus_osagent_apparmor(coresys: CoreSys):
    """Test coresys dbus connection."""
    assert coresys.dbus.agent.apparmor.version is None

    await coresys.dbus.agent.connect(coresys.dbus.bus)
    await coresys.dbus.agent.update()

    assert coresys.dbus.agent.apparmor.version == "2.13.2"

    fire_property_change_signal(coresys.dbus.agent.apparmor, {"ParserVersion": "1.0.0"})
    await asyncio.sleep(0)
    assert coresys.dbus.agent.apparmor.version == "1.0.0"

    fire_property_change_signal(coresys.dbus.agent, {}, ["ParserVersion"])
    await asyncio.sleep(0)
    assert coresys.dbus.agent.apparmor.version == "2.13.2"


async def test_dbus_osagent_apparmor_load(coresys: CoreSys, dbus: list[str]):
    """Load AppArmor Profile on host."""
    with pytest.raises(DBusNotConnectedError):
        await coresys.dbus.agent.apparmor.load_profile(
            Path("/data/apparmor/profile"), Path("/data/apparmor/cache")
        )

    await coresys.dbus.agent.connect(coresys.dbus.bus)

    dbus.clear()
    assert (
        await coresys.dbus.agent.apparmor.load_profile(
            Path("/data/apparmor/profile"), Path("/data/apparmor/cache")
        )
        is None
    )
    assert dbus == ["/io/hass/os/AppArmor-io.hass.os.AppArmor.LoadProfile"]


async def test_dbus_osagent_apparmor_unload(coresys: CoreSys, dbus: list[str]):
    """Unload AppArmor Profile on host."""
    with pytest.raises(DBusNotConnectedError):
        await coresys.dbus.agent.apparmor.unload_profile(
            Path("/data/apparmor/profile"), Path("/data/apparmor/cache")
        )

    await coresys.dbus.agent.connect(coresys.dbus.bus)

    dbus.clear()
    assert (
        await coresys.dbus.agent.apparmor.unload_profile(
            Path("/data/apparmor/profile"), Path("/data/apparmor/cache")
        )
        is None
    )
    assert dbus == ["/io/hass/os/AppArmor-io.hass.os.AppArmor.UnloadProfile"]
