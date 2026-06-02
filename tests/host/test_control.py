"""Test host control."""

from unittest.mock import patch

from dbus_fast import DBusError, ErrorType
import pytest

from supervisor.coresys import CoreSys
from supervisor.exceptions import HostInvalidHostnameError

from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.hostname import Hostname as HostnameService
from tests.dbus_service_mocks.logind import Logind as LogindService
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


async def test_set_hostname_rejected_by_host(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
):
    """A hostname rejected by hostnamed surfaces as HostInvalidHostnameError."""
    hostname_service: HostnameService = all_dbus_services["hostname"]
    hostname_service.response_set_static_hostname = DBusError(
        ErrorType.INVALID_ARGS, "Invalid static hostname 'bad name'"
    )

    with pytest.raises(HostInvalidHostnameError) as exc_info:
        await coresys.host.control.set_hostname("bad name")

    assert exc_info.value.error_key == "host_invalid_hostname"
    assert exc_info.value.extra_fields == {"hostname": "bad name"}
    assert str(exc_info.value) == "Invalid hostname 'bad name'"


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


@pytest.mark.parametrize(
    ("os_available", "in_process_shutdown"),
    [("18.0", False), ("17.3", True)],
    indirect=["os_available"],
    ids=["new-os", "old-os"],
)
async def test_reboot_graceful_shutdown_gating(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
    os_available: str,
    in_process_shutdown: bool,
):
    """reboot() stops Core in-process only on OS too old for coordinated shutdown."""
    logind_service: LogindService = all_dbus_services["logind"]
    logind_service.Reboot.calls.clear()

    with patch.object(coresys.core, "shutdown") as core_shutdown:
        await coresys.host.control.reboot()

    assert core_shutdown.called is in_process_shutdown
    assert len(logind_service.Reboot.calls) == 1


@pytest.mark.parametrize(
    ("os_available", "in_process_shutdown"),
    [("18.0", False), ("17.3", True)],
    indirect=["os_available"],
    ids=["new-os", "old-os"],
)
async def test_shutdown_graceful_shutdown_gating(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
    os_available: str,
    in_process_shutdown: bool,
):
    """shutdown() stops Core in-process only on OS too old for coordinated shutdown."""
    logind_service: LogindService = all_dbus_services["logind"]
    logind_service.PowerOff.calls.clear()

    with patch.object(coresys.core, "shutdown") as core_shutdown:
        await coresys.host.control.shutdown()

    assert core_shutdown.called is in_process_shutdown
    assert len(logind_service.PowerOff.calls) == 1
