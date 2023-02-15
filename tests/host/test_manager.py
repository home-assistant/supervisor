"""Test host manager."""
from unittest.mock import PropertyMock, patch

from awesomeversion import AwesomeVersion
import pytest

from supervisor.coresys import CoreSys
from supervisor.dbus.agent import OSAgent
from supervisor.dbus.const import MulticastProtocolEnabled
from supervisor.dbus.hostname import Hostname
from supervisor.dbus.manager import DBusManager
from supervisor.dbus.resolved import Resolved
from supervisor.dbus.systemd import Systemd
from supervisor.dbus.timedate import TimeDate
from supervisor.dbus.udisks2 import UDisks2


@pytest.fixture(name="coresys_dbus")
async def fixture_coresys_dbus(
    coresys: CoreSys,
    hostname: Hostname,
    systemd: Systemd,
    timedate: TimeDate,
    os_agent: OSAgent,
    resolved: Resolved,
    udisks2: UDisks2,
) -> CoreSys:
    """Coresys with all dbus interfaces mock loaded."""
    DBusManager.hostname = PropertyMock(return_value=hostname)
    DBusManager.systemd = PropertyMock(return_value=systemd)
    DBusManager.timedate = PropertyMock(return_value=timedate)
    DBusManager.agent = PropertyMock(return_value=os_agent)
    DBusManager.resolved = PropertyMock(return_value=resolved)
    DBusManager.udisks2 = PropertyMock(return_value=udisks2)

    yield coresys


async def test_load(coresys_dbus: CoreSys, dbus: list[str]):
    """Test manager load."""
    coresys = coresys_dbus
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
        assert len(coresys.host.logs.default_identifiers) > 0
        assert coresys.dbus.udisks2.version == AwesomeVersion("2.9.2")

        sound_update.assert_called_once()

    assert (
        "/org/freedesktop/systemd1-org.freedesktop.systemd1.Manager.ListUnits" in dbus
    )


async def test_reload(coresys_dbus: CoreSys, dbus: list[str]):
    """Test manager reload and ensure it does not unnecessarily recreate dbus objects."""
    coresys = coresys_dbus
    await coresys.host.load()
    dbus.clear()

    with patch("supervisor.utils.dbus.DBus.connect") as connect, patch.object(
        coresys.host.sound, "update"
    ) as sound_update:
        await coresys.host.reload()

        connect.assert_not_called()
        sound_update.assert_called_once()

    assert (
        "/org/freedesktop/systemd1-org.freedesktop.systemd1.Manager.ListUnits" in dbus
    )
