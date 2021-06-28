"""Test AppArmor/Agent dbus interface."""
from pathlib import Path

import pytest

from supervisor.coresys import CoreSys
from supervisor.exceptions import DBusNotConnectedError


async def test_dbus_osagent_apparmor(coresys: CoreSys):
    """Test coresys dbus connection."""
    assert coresys.dbus.agent.apparmor.version is None

    await coresys.dbus.agent.connect()
    await coresys.dbus.agent.update()

    assert coresys.dbus.agent.apparmor.version == "2.13.2"


async def test_dbus_osagent_apparmor_load(coresys: CoreSys):
    """Load AppArmor Profile on host."""

    with pytest.raises(DBusNotConnectedError):
        await coresys.dbus.agent.apparmor.load_profile(
            Path("/data/apparmor/profile"), Path("/data/apparmor/cache")
        )

    await coresys.dbus.agent.connect()

    assert await coresys.dbus.agent.apparmor.load_profile(
        Path("/data/apparmor/profile"), Path("/data/apparmor/cache")
    )


async def test_dbus_osagent_apparmor_unload(coresys: CoreSys):
    """Unload AppArmor Profile on host."""

    with pytest.raises(DBusNotConnectedError):
        await coresys.dbus.agent.apparmor.unload_profile(
            Path("/data/apparmor/profile"), Path("/data/apparmor/cache")
        )

    await coresys.dbus.agent.connect()

    assert await coresys.dbus.agent.apparmor.unload_profile(
        Path("/data/apparmor/profile"), Path("/data/apparmor/cache")
    )
