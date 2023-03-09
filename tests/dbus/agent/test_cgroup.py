"""Test CGroup/Agent dbus interface."""
# pylint: disable=import-error
from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.agent import OSAgent
from supervisor.exceptions import DBusNotConnectedError

from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.cgroup import CGroup as CGroupService


@pytest.fixture(name="cgroup_service", autouse=True)
async def fixture_cgroup_service(
    os_agent_services: dict[str, DBusServiceMock]
) -> CGroupService:
    """Mock CGroup dbus service."""
    yield os_agent_services["cgroup"]


async def test_dbus_osagent_cgroup_add_devices(
    cgroup_service: CGroupService, dbus_session_bus: MessageBus
):
    """Test wipe data partition on host."""
    os_agent = OSAgent()

    with pytest.raises(DBusNotConnectedError):
        await os_agent.cgroup.add_devices_allowed("9324kl23j4kl", "*:* rwm")

    await os_agent.connect(dbus_session_bus)

    assert await os_agent.cgroup.add_devices_allowed("9324kl23j4kl", "*:* rwm") is None
    assert cgroup_service.AddDevicesAllowed.calls == [("9324kl23j4kl", "*:* rwm")]
