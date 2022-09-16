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
):
    """Test manager load."""
    type(coresys.dbus).hostname = PropertyMock(return_value=hostname)
    type(coresys.dbus).systemd = PropertyMock(return_value=systemd)
    type(coresys.dbus).timedate = PropertyMock(return_value=timedate)
    type(coresys.dbus).agent = PropertyMock(return_value=os_agent)
    type(coresys.dbus).resolved = PropertyMock(return_value=resolved)

    with patch.object(coresys.host.sound, "update") as sound_update, patch.object(
        coresys.host.apparmor, "load"
    ) as apparmor_load:
        await coresys.host.load()

        assert coresys.dbus.hostname.hostname == "homeassistant-n2"
        assert coresys.dbus.systemd.boot_timestamp == 1646197962613554
        assert coresys.dbus.timedate.timezone == "Etc/UTC"
        assert coresys.dbus.agent.diagnostics is True
        assert coresys.dbus.network.connectivity_enabled is True
        assert coresys.dbus.resolved.multicast_dns == MulticastProtocolEnabled.RESOLVE

        sound_update.assert_called_once()
        apparmor_load.assert_called_once()
