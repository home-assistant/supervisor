"""Test Boards manager."""

# pylint: disable=import-error
from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.agent.boards import BoardManager
from supervisor.exceptions import BoardInvalidError

from tests.common import mock_dbus_services
from tests.dbus_service_mocks.agent_boards import Boards as BoardsService


@pytest.fixture(name="boards_service", autouse=True)
async def fixture_boards_service(dbus_session_bus: MessageBus) -> BoardsService:
    """Mock Boards dbus service."""
    yield (await mock_dbus_services({"agent_boards": None}, dbus_session_bus))[
        "agent_boards"
    ]


async def test_dbus_board(dbus_session_bus: MessageBus):
    """Test DBus Board load."""
    await mock_dbus_services({"agent_boards_yellow": None}, dbus_session_bus)

    board = BoardManager()
    await board.connect(dbus_session_bus)

    assert board.board == "Yellow"
    assert board.yellow.power_led is True

    with pytest.raises(BoardInvalidError):
        assert not board.supervised
    with pytest.raises(BoardInvalidError):
        assert not board.green


async def test_dbus_board_green(
    boards_service: BoardsService, dbus_session_bus: MessageBus
):
    """Test DBus Board load with Green board."""
    await mock_dbus_services({"agent_boards_green": None}, dbus_session_bus)
    boards_service.board = "Green"

    board = BoardManager()
    await board.connect(dbus_session_bus)

    assert board.board == "Green"
    assert board.green.activity_led is True

    with pytest.raises(BoardInvalidError):
        assert not board.supervised
    with pytest.raises(BoardInvalidError):
        assert not board.yellow


async def test_dbus_board_supervised(
    boards_service: BoardsService, dbus_session_bus: MessageBus
):
    """Test DBus Board load with supervised board."""
    await mock_dbus_services({"agent_boards_supervised": None}, dbus_session_bus)
    boards_service.board = "Supervised"

    board = BoardManager()
    await board.connect(dbus_session_bus)

    assert board.board == "Supervised"
    assert board.supervised

    with pytest.raises(BoardInvalidError):
        assert not board.yellow
    with pytest.raises(BoardInvalidError):
        assert not board.green


async def test_dbus_board_other(
    boards_service: BoardsService, dbus_session_bus: MessageBus
):
    """Test DBus Board load with board that has no dbus object."""
    boards_service.board = "NotReal"

    board = BoardManager()
    await board.connect(dbus_session_bus)

    assert board.board == "NotReal"

    with pytest.raises(BoardInvalidError):
        assert not board.yellow
    with pytest.raises(BoardInvalidError):
        assert not board.supervised
    with pytest.raises(BoardInvalidError):
        assert not board.green
