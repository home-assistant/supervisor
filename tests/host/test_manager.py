"""Test host manager."""
from unittest.mock import PropertyMock, patch

from supervisor.coresys import CoreSys
from supervisor.dbus.agent import OSAgent
from supervisor.dbus.const import MulticastProtocolEnabled
from supervisor.dbus.hostname import Hostname
from supervisor.dbus.resolved import Resolved
from supervisor.dbus.systemd import Systemd
from supervisor.dbus.timedate import TimeDate


async def test_load(
    coresys: CoreSys,
    hostname: Hostname,
    systemd: Systemd,
    timedate: TimeDate,
    os_agent: OSAgent,
    resolved: Resolved,
    dbus: list[str],
):
    """Test manager load."""
    type(coresys.dbus).hostname = PropertyMock(return_value=hostname)
    type(coresys.dbus).systemd = PropertyMock(return_value=systemd)
    type(coresys.dbus).timedate = PropertyMock(return_value=timedate)
    type(coresys.dbus).agent = PropertyMock(return_value=os_agent)
    type(coresys.dbus).resolved = PropertyMock(return_value=resolved)
    dbus.clear()

    with patch.object(coresys.host.sound, "update") as sound_update:
        await coresys.host.load()

        assert coresys.dbus.hostname.hostname == "homeassistant-n2"
        assert coresys.dbus.systemd.boot_timestamp == 1646197962613554
        assert coresys.dbus.timedate.timezone == "Etc/UTC"
        assert coresys.dbus.agent.diagnostics is True
        assert coresys.dbus.network.connectivity_enabled is True
        assert coresys.dbus.resolved.multicast_dns == MulticastProtocolEnabled.RESOLVE
        assert coresys.dbus.agent.apparmor.version == "2.13.2"

        sound_update.assert_called_once()

    assert (
        "/org/freedesktop/systemd1-org.freedesktop.systemd1.Manager.ListUnits" in dbus
    )


async def test_reload(coresys: CoreSys, dbus: list[str]):
    """Test manager reload and ensure it does not unnecessarily recreate dbus objects."""
    await coresys.dbus.load()
    await coresys.host.load()

    with patch("supervisor.utils.dbus.DBus.connect") as connect, patch.object(
        coresys.host.sound, "update"
    ) as sound_update:
        await coresys.host.reload()

        connect.assert_not_called()
        sound_update.assert_called_once()

    assert (
        "/org/freedesktop/systemd1-org.freedesktop.systemd1.Manager.ListUnits" in dbus
    )
