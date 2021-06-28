"""Test OSAgent dbus interface."""

from supervisor.coresys import CoreSys


async def test_dbus_osagent(coresys: CoreSys):
    """Test coresys dbus connection."""
    assert coresys.dbus.agent.version is None
    assert coresys.dbus.agent.diagnostics is None

    await coresys.dbus.agent.connect()
    await coresys.dbus.agent.update()

    assert coresys.dbus.agent.version == "1.1.0"
    assert coresys.dbus.agent.diagnostics
