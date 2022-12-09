"""Test OSAgent dbus interface."""

import asyncio

from supervisor.coresys import CoreSys

from tests.common import fire_property_change_signal


async def test_dbus_osagent(coresys: CoreSys):
    """Test coresys dbus connection."""
    assert coresys.dbus.agent.version is None
    assert coresys.dbus.agent.diagnostics is None

    await coresys.dbus.agent.connect(coresys.dbus.bus)
    await coresys.dbus.agent.update()

    assert coresys.dbus.agent.version == "1.1.0"
    assert coresys.dbus.agent.diagnostics

    fire_property_change_signal(coresys.dbus.agent, {"Diagnostics": False})
    await asyncio.sleep(0)
    assert coresys.dbus.agent.diagnostics is False

    fire_property_change_signal(coresys.dbus.agent, {}, ["Diagnostics"])
    await asyncio.sleep(0)
    assert coresys.dbus.agent.diagnostics is True
