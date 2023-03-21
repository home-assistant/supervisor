"""Test OS API."""

from pathlib import Path
from unittest.mock import PropertyMock, patch

from aiohttp.test_utils import TestClient
import pytest

from supervisor.coresys import CoreSys
from supervisor.hardware.data import Device
from supervisor.os.manager import OSManager
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue, Suggestion

from tests.common import mock_dbus_services
from tests.dbus_service_mocks.agent_boards import Boards as BoardsService
from tests.dbus_service_mocks.agent_boards_yellow import Yellow as YellowService
from tests.dbus_service_mocks.base import DBusServiceMock

# pylint: disable=protected-access


@pytest.fixture(name="boards_service")
async def fixture_boards_service(
    os_agent_services: dict[str, DBusServiceMock]
) -> BoardsService:
    """Return mock Boards service."""
    yield os_agent_services["agent_boards"]


async def test_api_os_info(api_client: TestClient):
    """Test docker info api."""
    resp = await api_client.get("/os/info")
    result = await resp.json()

    for attr in (
        "version",
        "version_latest",
        "update_available",
        "board",
        "boot",
        "data_disk",
    ):
        assert attr in result["data"]


async def test_api_os_info_with_agent(api_client: TestClient, coresys: CoreSys):
    """Test docker info api."""
    resp = await api_client.get("/os/info")
    result = await resp.json()

    assert result["data"]["data_disk"] == "/dev/sda"


async def test_api_os_datadisk_move(api_client: TestClient, coresys: CoreSys):
    """Test datadisk move without exists disk."""
    coresys.os._available = True

    resp = await api_client.post("/os/datadisk/move", json={"device": "/dev/sdaaaa"})
    result = await resp.json()

    assert result["message"] == "'/dev/sdaaaa' don't exists on the host!"


async def test_api_os_datadisk_list(api_client: TestClient, coresys: CoreSys):
    """Test datadisk list function."""
    coresys.hardware.update_device(
        Device(
            "sda",
            Path("/dev/sda"),
            Path("/sys/bus/usb/000"),
            "block",
            None,
            [Path("/dev/serial/by-id/test")],
            {"ID_NAME": "xy", "MINOR": "0", "DEVTYPE": "disk"},
            [],
        )
    )
    coresys.hardware.update_device(
        Device(
            "sda1",
            Path("/dev/sda1"),
            Path("/sys/bus/usb/000/1"),
            "block",
            None,
            [Path("/dev/serial/by-id/test1")],
            {"ID_NAME": "xy", "MINOR": "1", "DEVTYPE": "partition"},
            [],
        )
    )

    resp = await api_client.get("/os/datadisk/list")
    result = await resp.json()

    assert result["data"]["devices"] == ["/dev/sda"]


async def test_api_board_yellow_info(api_client: TestClient, coresys: CoreSys):
    """Test yellow board info."""
    resp = await api_client.get("/os/boards/yellow")
    assert resp.status == 200

    result = await resp.json()
    assert result["data"]["disk_led"] is True
    assert result["data"]["heartbeat_led"] is True
    assert result["data"]["power_led"] is True

    assert (await api_client.get("/os/boards/supervised")).status == 400
    assert (await api_client.get("/os/boards/not-real")).status == 400


async def test_api_board_yellow_options(
    api_client: TestClient,
    coresys: CoreSys,
    os_agent_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
):
    """Test yellow board options."""
    yellow_service: YellowService = os_agent_services["agent_boards_yellow"]

    assert coresys.dbus.agent.board.yellow.disk_led is True
    assert coresys.dbus.agent.board.yellow.heartbeat_led is True
    assert coresys.dbus.agent.board.yellow.power_led is True
    assert len(coresys.resolution.issues) == 0
    resp = await api_client.post(
        "/os/boards/yellow",
        json={"disk_led": False, "heartbeat_led": False, "power_led": False},
    )
    assert resp.status == 200

    await yellow_service.ping()
    assert coresys.dbus.agent.board.yellow.disk_led is False
    assert coresys.dbus.agent.board.yellow.heartbeat_led is False
    assert coresys.dbus.agent.board.yellow.power_led is False

    assert (
        Issue(IssueType.REBOOT_REQUIRED, ContextType.SYSTEM)
        in coresys.resolution.issues
    )
    assert (
        Suggestion(SuggestionType.EXECUTE_REBOOT, ContextType.SYSTEM)
        in coresys.resolution.suggestions
    )


async def test_api_board_supervised_info(
    api_client: TestClient, coresys: CoreSys, boards_service: BoardsService
):
    """Test supervised board info."""
    await mock_dbus_services({"agent_boards_supervised": None}, coresys.dbus.bus)
    boards_service.board = "Supervised"
    await coresys.dbus.agent.board.update()

    with patch("supervisor.os.manager.CPE.get_product", return_value=["not-hassos"]):
        await coresys.os.load()

        assert (await api_client.get("/os/boards/supervised")).status == 200
        assert (await api_client.post("/os/boards/supervised", json={})).status == 405
        assert (await api_client.get("/os/boards/yellow")).status == 400
        assert (await api_client.get("/os/boards/not-real")).status == 400


async def test_api_board_other_info(
    api_client: TestClient, coresys: CoreSys, boards_service: BoardsService
):
    """Test info for other board without dbus object."""
    boards_service.board = "not-real"
    await coresys.dbus.agent.board.update()

    with patch.object(OSManager, "board", new=PropertyMock(return_value="not-real")):
        assert (await api_client.get("/os/boards/not-real")).status == 200
        assert (await api_client.post("/os/boards/not-real", json={})).status == 405
        assert (await api_client.get("/os/boards/yellow")).status == 400
        assert (await api_client.get("/os/boards/supervised")).status == 400
