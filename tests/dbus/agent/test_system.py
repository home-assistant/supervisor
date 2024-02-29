"""Test System/Agent dbus interface."""

from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.agent import OSAgent
from supervisor.exceptions import DBusNotConnectedError

from tests.dbus_service_mocks.agent_system import System as SystemService
from tests.dbus_service_mocks.base import DBusServiceMock


@pytest.fixture(name="system_service", autouse=True)
async def fixture_system_service(
    os_agent_services: dict[str, DBusServiceMock],
) -> SystemService:
    """Mock System dbus service."""
    yield os_agent_services["agent_system"]


async def test_dbus_osagent_system_wipe(
    system_service: SystemService, dbus_session_bus: MessageBus
):
    """Test wipe data partition on host."""
    system_service.ScheduleWipeDevice.calls.clear()
    os_agent = OSAgent()

    with pytest.raises(DBusNotConnectedError):
        await os_agent.system.schedule_wipe_device()

    await os_agent.connect(dbus_session_bus)

    assert await os_agent.system.schedule_wipe_device() is True
    assert system_service.ScheduleWipeDevice.calls == [()]
