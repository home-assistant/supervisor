"""Test Yellow board."""

from unittest.mock import patch

from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.agent.boards.yellow import Yellow

from tests.common import mock_dbus_services
from tests.dbus_service_mocks.agent_boards_yellow import Yellow as YellowService


@pytest.fixture(name="yellow_service", autouse=True)
async def fixture_yellow_service(dbus_session_bus: MessageBus) -> YellowService:
    """Mock Yellow Board dbus service."""
    yield (await mock_dbus_services({"agent_boards_yellow": None}, dbus_session_bus))[
        "agent_boards_yellow"
    ]


async def test_dbus_yellow(yellow_service: YellowService, dbus_session_bus: MessageBus):
    """Test Yellow board load."""
    yellow = await Yellow().load_config()
    await yellow.connect(dbus_session_bus)

    assert yellow.board_name == "Yellow"
    assert yellow.disk_led is True
    assert yellow.heartbeat_led is True
    assert yellow.power_led is True

    with (
        patch("supervisor.utils.common.Path.is_file", return_value=True),
        patch(
            "supervisor.utils.common.read_json_file",
            return_value={"disk_led": False, "heartbeat_led": False},
        ),
    ):
        yellow = await Yellow().load_config()
    await yellow.connect(dbus_session_bus)

    assert yellow.disk_led is False
    assert yellow.heartbeat_led is False


async def test_dbus_yellow_set_disk_led(
    yellow_service: YellowService, dbus_session_bus: MessageBus
):
    """Test setting disk led for Yellow board."""
    yellow = await Yellow().load_config()
    await yellow.connect(dbus_session_bus)

    await yellow.set_disk_led(False)
    await yellow_service.ping()
    assert yellow.disk_led is False


async def test_dbus_yellow_set_heartbeat_led(
    yellow_service: YellowService, dbus_session_bus: MessageBus
):
    """Test setting heartbeat led for Yellow board."""
    yellow = await Yellow().load_config()
    await yellow.connect(dbus_session_bus)

    await yellow.set_heartbeat_led(False)
    await yellow_service.ping()
    assert yellow.heartbeat_led is False


async def test_dbus_yellow_set_power_led(
    yellow_service: YellowService, dbus_session_bus: MessageBus
):
    """Test setting power led for Yellow board."""
    yellow = await Yellow().load_config()
    await yellow.connect(dbus_session_bus)

    await yellow.set_power_led(False)
    await yellow_service.ping()
    assert yellow.power_led is False
