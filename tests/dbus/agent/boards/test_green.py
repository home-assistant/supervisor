"""Test Green board."""
# pylint: disable=import-error
import asyncio

from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.agent.boards.green import Green

from tests.common import mock_dbus_services
from tests.dbus_service_mocks.agent_boards_green import Green as GreenService


@pytest.fixture(name="green_service", autouse=True)
async def fixture_green_service(dbus_session_bus: MessageBus) -> GreenService:
    """Mock Green Board dbus service."""
    yield (await mock_dbus_services({"agent_boards_green": None}, dbus_session_bus))[
        "agent_boards_green"
    ]


async def test_dbus_green(dbus_session_bus: MessageBus):
    """Test Green board load."""
    green = Green()
    await green.connect(dbus_session_bus)

    assert green.name == "Green"
    assert green.activity_led is True
    assert green.power_led is True
    assert green.user_led is True


async def test_dbus_green_set_activity_led(
    green_service: GreenService, dbus_session_bus: MessageBus
):
    """Test setting activity led for Green board."""
    green = Green()
    await green.connect(dbus_session_bus)

    green.activity_led = False
    await asyncio.sleep(0)  # Set property via dbus is separate async task
    await green_service.ping()
    assert green.activity_led is False


async def test_dbus_green_set_power_led(
    green_service: GreenService, dbus_session_bus: MessageBus
):
    """Test setting power led for Green board."""
    green = Green()
    await green.connect(dbus_session_bus)

    green.power_led = False
    await asyncio.sleep(0)  # Set property via dbus is separate async task
    await green_service.ping()
    assert green.power_led is False


async def test_dbus_green_set_user_led(
    green_service: GreenService, dbus_session_bus: MessageBus
):
    """Test setting user led for Green board."""
    green = Green()
    await green.connect(dbus_session_bus)

    green.user_led = False
    await asyncio.sleep(0)  # Set property via dbus is separate async task
    await green_service.ping()
    assert green.user_led is False
