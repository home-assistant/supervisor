"""Test Yellow board."""
# pylint: disable=import-error
import asyncio

from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.agent.boards.yellow import Yellow

from tests.common import mock_dbus_services
from tests.dbus_service_mocks.boards_yellow import Yellow as YellowService


@pytest.fixture(name="yellow_service", autouse=True)
async def fixture_yellow_service(dbus_session_bus: MessageBus) -> YellowService:
    """Mock Yellow Board dbus service."""
    yield (await mock_dbus_services({"boards_yellow": None}, dbus_session_bus))[
        "boards_yellow"
    ]


async def test_dbus_yellow(dbus_session_bus: MessageBus):
    """Test Yellow board load."""
    yellow = Yellow()
    await yellow.connect(dbus_session_bus)

    assert yellow.name == "Yellow"
    assert yellow.disk_led is True
    assert yellow.heartbeat_led is True
    assert yellow.power_led is True


async def test_dbus_yellow_set_disk_led(
    yellow_service: YellowService, dbus_session_bus: MessageBus
):
    """Test setting disk led for Yellow board."""
    yellow = Yellow()
    await yellow.connect(dbus_session_bus)

    yellow.disk_led = False
    await asyncio.sleep(0)  # Set property via dbus is separate async task
    await yellow_service.ping()
    assert yellow.disk_led is False


async def test_dbus_yellow_set_heartbeat_led(
    yellow_service: YellowService, dbus_session_bus: MessageBus
):
    """Test setting heartbeat led for Yellow board."""
    yellow = Yellow()
    await yellow.connect(dbus_session_bus)

    yellow.heartbeat_led = False
    await asyncio.sleep(0)  # Set property via dbus is separate async task
    await yellow_service.ping()
    assert yellow.heartbeat_led is False


async def test_dbus_yellow_set_power_led(
    yellow_service: YellowService, dbus_session_bus: MessageBus
):
    """Test setting power led for Yellow board."""
    yellow = Yellow()
    await yellow.connect(dbus_session_bus)

    yellow.power_led = False
    await asyncio.sleep(0)  # Set property via dbus is separate async task
    await yellow_service.ping()
    assert yellow.power_led is False
