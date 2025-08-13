"""Test host control."""

import pytest

from supervisor.coresys import CoreSys

from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.hostname import Hostname as HostnameService
from tests.dbus_service_mocks.timedate import TimeDate as TimeDateService


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


@pytest.mark.parametrize("os_available", ["16.2"], indirect=True)
async def test_set_timezone(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
    os_available: str,
):
    """Test set timezone."""
    timedate_service: TimeDateService = all_dbus_services["timedate"]
    timedate_service.SetTimezone.calls.clear()

    assert coresys.dbus.timedate.timezone == "Etc/UTC"

    await coresys.host.control.set_timezone("Europe/Prague")
    assert timedate_service.SetTimezone.calls == [("Europe/Prague", False)]


@pytest.mark.parametrize("os_available", ["16.1"], indirect=True)
async def test_set_timezone_unsupported(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
    os_available: str,
):
    """Test DBus call is not made when OS doesn't support it."""
    timedate_service: TimeDateService = all_dbus_services["timedate"]
    timedate_service.SetTimezone.calls.clear()

    await coresys.host.control.set_timezone("Europe/Prague")
    assert timedate_service.SetTimezone.calls == []
