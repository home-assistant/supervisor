"""Test Green board."""

from unittest.mock import patch

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


async def test_dbus_green(green_service: GreenService, dbus_session_bus: MessageBus):
    """Test Green board load."""
    green = await Green().load_config()
    await green.connect(dbus_session_bus)

    assert green.board_name == "Green"
    assert green.activity_led is True
    assert green.power_led is True
    assert green.user_led is True

    with (
        patch("supervisor.utils.common.Path.is_file", return_value=True),
        patch(
            "supervisor.utils.common.read_json_file",
            return_value={"activity_led": False, "user_led": False},
        ),
    ):
        green = await Green().load_config()
    await green.connect(dbus_session_bus)

    assert green.activity_led is False
    assert green.user_led is False


async def test_dbus_green_set_activity_led(
    green_service: GreenService, dbus_session_bus: MessageBus
):
    """Test setting activity led for Green board."""
    green = await Green().load_config()
    await green.connect(dbus_session_bus)

    await green.set_activity_led(False)
    await green_service.ping()
    assert green.activity_led is False


async def test_dbus_green_set_power_led(
    green_service: GreenService, dbus_session_bus: MessageBus
):
    """Test setting power led for Green board."""
    green = await Green().load_config()
    await green.connect(dbus_session_bus)

    await green.set_power_led(False)
    await green_service.ping()
    assert green.power_led is False


async def test_dbus_green_set_user_led(
    green_service: GreenService, dbus_session_bus: MessageBus
):
    """Test setting user led for Green board."""
    green = await Green().load_config()
    await green.connect(dbus_session_bus)

    await green.set_user_led(False)
    await green_service.ping()
    assert green.user_led is False
