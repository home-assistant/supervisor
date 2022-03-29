"""Test host manager."""
from unittest.mock import AsyncMock, PropertyMock, patch

from supervisor.coresys import CoreSys
from supervisor.dbus.agent import OSAgent
from supervisor.dbus.hostname import Hostname
from supervisor.dbus.systemd import Systemd
from supervisor.dbus.timedate import TimeDate


async def test_reload(coresys: CoreSys):
    """Test manager reload."""
    with patch.object(coresys.host.info, "update") as info_update, patch.object(
        coresys.host.services, "update"
    ) as services_update, patch.object(
        coresys.host.network, "update"
    ) as network_update, patch.object(
        coresys.host.sys_dbus.agent, "update", new=AsyncMock()
    ) as agent_update, patch.object(
        coresys.host.sound, "update"
    ) as sound_update:

        await coresys.host.reload()

        info_update.assert_called_once()
        services_update.assert_called_once()
        network_update.assert_called_once()
        agent_update.assert_called_once()
        sound_update.assert_called_once()

        info_update.reset_mock()
        services_update.reset_mock()
        network_update.reset_mock()
        agent_update.reset_mock()
        sound_update.reset_mock()

        await coresys.host.reload(
            services=False, network=False, agent=False, audio=False
        )
        info_update.assert_called_once()
        services_update.assert_not_called()
        network_update.assert_not_called()
        agent_update.assert_not_called()
        sound_update.assert_not_called()


async def test_load(
    coresys: CoreSys,
    hostname: Hostname,
    systemd: Systemd,
    timedate: TimeDate,
    os_agent: OSAgent,
):
    """Test manager load."""
    type(coresys.dbus).hostname = PropertyMock(return_value=hostname)
    type(coresys.dbus).systemd = PropertyMock(return_value=systemd)
    type(coresys.dbus).timedate = PropertyMock(return_value=timedate)
    type(coresys.dbus).agent = PropertyMock(return_value=os_agent)

    with patch.object(coresys.host.sound, "update") as sound_update, patch.object(
        coresys.host.apparmor, "load"
    ) as apparmor_load:
        # Network is updated on connect for a version check so its not None already
        assert coresys.dbus.hostname.hostname is None
        assert coresys.dbus.systemd.boot_timestamp is None
        assert coresys.dbus.timedate.timezone is None
        assert coresys.dbus.agent.diagnostics is None

        await coresys.host.load()

        assert coresys.dbus.hostname.hostname == "homeassistant-n2"
        assert coresys.dbus.systemd.boot_timestamp == 1646197962613554
        assert coresys.dbus.timedate.timezone == "Etc/UTC"
        assert coresys.dbus.agent.diagnostics is True
        assert coresys.dbus.network.connectivity_enabled is True

        sound_update.assert_called_once()
        apparmor_load.assert_called_once()
