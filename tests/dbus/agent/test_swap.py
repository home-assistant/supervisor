"""Test Swap configuration interface."""

from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.agent import OSAgent

from tests.dbus_service_mocks.agent_swap import Swap as SwapService
from tests.dbus_service_mocks.base import DBusServiceMock


@pytest.fixture(name="swap_service", autouse=True)
async def fixture_swap_service(
    os_agent_services: dict[str, DBusServiceMock],
) -> SwapService:
    """Mock System dbus service."""
    yield os_agent_services["agent_swap"]


async def test_dbus_osagent_swap_size(
    swap_service: SwapService, dbus_session_bus: MessageBus
):
    """Test DBus API for swap size."""
    os_agent = OSAgent()

    assert os_agent.swap.swap_size is None
    await os_agent.swap.connect(dbus_session_bus)

    assert os_agent.swap.swap_size == "1M"

    swap_service.emit_properties_changed({"SwapSize": "2M"})
    await swap_service.ping()
    assert os_agent.swap.swap_size == "2M"


async def test_dbus_osagent_swappiness(
    swap_service: SwapService, dbus_session_bus: MessageBus
):
    """Test DBus API for swappiness."""
    os_agent = OSAgent()

    assert os_agent.swap.swappiness is None
    await os_agent.swap.connect(dbus_session_bus)

    assert os_agent.swap.swappiness == 1

    swap_service.emit_properties_changed({"Swappiness": 10})
    await swap_service.ping()
    assert os_agent.swap.swappiness == 10
