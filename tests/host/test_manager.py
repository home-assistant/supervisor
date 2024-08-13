"""Test host manager."""

from unittest.mock import patch

from awesomeversion import AwesomeVersion
import pytest

from supervisor.coresys import CoreSys
from supervisor.dbus.const import MulticastProtocolEnabled

from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.rauc import Rauc as RaucService
from tests.dbus_service_mocks.systemd import Systemd as SystemdService


@pytest.fixture(name="systemd_service")
async def fixture_systemd_service(
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
) -> SystemdService:
    """Return systemd service mock."""
    yield all_dbus_services["systemd"]


async def test_load(coresys: CoreSys, systemd_service: SystemdService):
    """Test manager load."""
    systemd_service.ListUnits.calls.clear()

    with patch.object(coresys.host.sound, "update") as sound_update:
        await coresys.host.load()

        assert coresys.dbus.hostname.hostname == "homeassistant-n2"
        assert coresys.dbus.systemd.boot_timestamp == 1632236713344227
        assert coresys.dbus.timedate.timezone == "Etc/UTC"
        assert coresys.dbus.agent.diagnostics is True
        assert coresys.dbus.network.connectivity_enabled is True
        assert coresys.dbus.resolved.multicast_dns == MulticastProtocolEnabled.RESOLVE
        assert coresys.dbus.agent.apparmor.version == "2.13.2"
        assert len(coresys.host.logs.default_identifiers) > 0
        assert coresys.dbus.udisks2.version == AwesomeVersion("2.9.2")

        sound_update.assert_called_once()

    assert systemd_service.ListUnits.calls == [()]


async def test_reload(coresys: CoreSys, systemd_service: SystemdService):
    """Test manager reload and ensure it does not unnecessarily recreate dbus objects."""
    await coresys.host.load()
    systemd_service.ListUnits.calls.clear()

    with (
        patch("supervisor.utils.dbus.DBus.connect") as connect,
        patch.object(coresys.host.sound, "update") as sound_update,
    ):
        await coresys.host.reload()

        connect.assert_not_called()
        sound_update.assert_called_once()

    assert systemd_service.ListUnits.calls == [()]


async def test_reload_os(
    coresys: CoreSys, all_dbus_services: dict[str, DBusServiceMock], os_available
):
    """Test manager reload while on OS also reloads OS info cache."""
    rauc_service: RaucService = all_dbus_services["rauc"]
    rauc_service.GetSlotStatus.calls.clear()

    await coresys.host.load()
    await coresys.host.reload()

    assert rauc_service.GetSlotStatus.calls == [()]
