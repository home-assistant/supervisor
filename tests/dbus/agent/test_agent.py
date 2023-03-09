"""Test OSAgent dbus interface."""
# pylint: disable=import-error
from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.agent import OSAgent

from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.os_agent import OSAgent as OSAgentService


@pytest.fixture(name="os_agent_service", autouse=True)
async def fixture_os_agent_service(
    os_agent_services: dict[str, DBusServiceMock]
) -> OSAgentService:
    """Mock OS Agent dbus service."""
    yield os_agent_services["os_agent"]


async def test_dbus_osagent(
    os_agent_service: OSAgentService, dbus_session_bus: MessageBus
):
    """Test OS Agent properties."""
    os_agent = OSAgent()

    assert os_agent.version is None
    assert os_agent.diagnostics is None

    await os_agent.connect(dbus_session_bus)

    assert os_agent.version == "1.1.0"
    assert os_agent.diagnostics

    os_agent_service.emit_properties_changed({"Diagnostics": False})
    await os_agent_service.ping()
    assert os_agent.diagnostics is False

    os_agent_service.emit_properties_changed({}, ["Diagnostics"])
    await os_agent_service.ping()
    await os_agent_service.ping()
    assert os_agent.diagnostics is True
