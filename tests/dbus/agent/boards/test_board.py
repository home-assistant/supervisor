"""Test Boards manager."""

from unittest.mock import patch

from dbus_fast.aio.message_bus import MessageBus
from dbus_fast.aio.proxy_object import ProxyInterface
import pytest

from supervisor.dbus.agent.boards import BoardManager
from supervisor.exceptions import BoardInvalidError
from supervisor.utils.dbus import DBUS_INTERFACE_PROPERTIES, DBus


@pytest.fixture(name="dbus_mock_board")
async def fixture_dbus_mock_board(request: pytest.FixtureRequest, dbus: list[str]):
    """Mock Boards dbus object to particular board name for tests."""
    call_dbus = DBus.call_dbus

    async def mock_call_dbus_specify_board(
        proxy_interface: ProxyInterface,
        method: str,
        *args,
        unpack_variants: bool = True,
    ):
        if (
            proxy_interface.introspection.name == DBUS_INTERFACE_PROPERTIES
            and method == "call_get_all"
            and proxy_interface.path == "/io/hass/os/Boards"
        ):
            return {"Board": request.param}

        return call_dbus(
            proxy_interface, method, *args, unpack_variants=unpack_variants
        )

    with patch(
        "supervisor.utils.dbus.DBus.call_dbus", new=mock_call_dbus_specify_board
    ):
        yield dbus


async def test_dbus_board(dbus: list[str], dbus_bus: MessageBus):
    """Test DBus Board load."""
    board = BoardManager()
    await board.connect(dbus_bus)

    assert board.board == "Yellow"
    assert board.yellow.power_led is True

    with pytest.raises(BoardInvalidError):
        assert not board.supervised


@pytest.mark.parametrize("dbus_mock_board", ["Supervised"], indirect=True)
async def test_dbus_board_supervised(dbus_mock_board: list[str], dbus_bus: MessageBus):
    """Test DBus Board load with supervised board."""
    board = BoardManager()
    await board.connect(dbus_bus)

    assert board.board == "Supervised"
    assert board.supervised

    with pytest.raises(BoardInvalidError):
        assert not board.yellow


@pytest.mark.parametrize("dbus_mock_board", ["NotReal"], indirect=True)
async def test_dbus_board_other(dbus_mock_board: list[str], dbus_bus: MessageBus):
    """Test DBus Board load with board that has no dbus object."""
    board = BoardManager()
    await board.connect(dbus_bus)

    assert board.board == "NotReal"

    with pytest.raises(BoardInvalidError):
        assert not board.yellow
    with pytest.raises(BoardInvalidError):
        assert not board.supervised
