"""Test host control."""

from supervisor.coresys import CoreSys

from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.hostname import Hostname as HostnameService


async def test_set_hostname(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
):
    """Test set hostname."""
    hostname_service: HostnameService = all_dbus_services["hostname"]
    hostname_service.SetStaticHostname.calls.clear()

    assert coresys.dbus.hostname.hostname == "homeassistant-n2"

    await coresys.host.control.set_hostname("test")
    assert hostname_service.SetStaticHostname.calls == [("test", False)]
    await hostname_service.ping()
    assert coresys.dbus.hostname.hostname == "test"
