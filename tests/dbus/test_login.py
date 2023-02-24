"""Test login dbus interface."""
# pylint: disable=import-error
from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.logind import Logind
from supervisor.exceptions import DBusNotConnectedError

from tests.common import mock_dbus_services
from tests.dbus_service_mocks.logind import Logind as LogindService


@pytest.fixture(name="logind_service", autouse=True)
async def fixture_logind_service(dbus_session_bus: MessageBus) -> LogindService:
    """Mock logind dbus service."""
    yield (await mock_dbus_services({"logind": None}, dbus_session_bus))["logind"]


async def test_reboot(logind_service: LogindService, dbus_session_bus: MessageBus):
    """Test reboot."""
    logind = Logind()

    with pytest.raises(DBusNotConnectedError):
        await logind.reboot()

    await logind.connect(dbus_session_bus)

    assert await logind.reboot() is None
    assert logind_service.Reboot.calls == [(False,)]


async def test_power_off(logind_service: LogindService, dbus_session_bus: MessageBus):
    """Test power off."""
    logind = Logind()

    with pytest.raises(DBusNotConnectedError):
        await logind.power_off()

    await logind.connect(dbus_session_bus)

    assert await logind.power_off() is None
    assert logind_service.PowerOff.calls == [(False,)]
