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
    return os_agent_services["agent_system"]


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


async def test_dbus_osagent_system_ssh_auth_keys(
    system_service: SystemService, dbus_session_bus: MessageBus
):
    """Test add and clear of SSH authorized keys on host."""
    system_service.AddSSHAuthKey.calls.clear()
    system_service.ClearSSHAuthKeys.calls.clear()
    os_agent = OSAgent()
    key = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDXD8u9KB94/l1YukYflKOsO7KzoSEQD4dNNlWY9zaQP test@example.com"

    with pytest.raises(DBusNotConnectedError):
        await os_agent.system.add_ssh_auth_key(key)

    with pytest.raises(DBusNotConnectedError):
        await os_agent.system.clear_ssh_auth_keys()

    await os_agent.connect(dbus_session_bus)

    await os_agent.system.clear_ssh_auth_keys()
    await os_agent.system.add_ssh_auth_key(key)

    assert system_service.ClearSSHAuthKeys.calls == [()]
    assert system_service.AddSSHAuthKey.calls == [(key,)]
