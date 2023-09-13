"""Test OS API."""

from unittest.mock import PropertyMock, patch

from aiohttp.test_utils import TestClient
import pytest

from supervisor.coresys import CoreSys
from supervisor.dbus.agent.boards.interface import BoardProxy
from supervisor.host.control import SystemControl
from supervisor.os.manager import OSManager
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue, Suggestion

from tests.common import mock_dbus_services
from tests.dbus_service_mocks.agent_boards import Boards as BoardsService
from tests.dbus_service_mocks.agent_boards_green import Green as GreenService
from tests.dbus_service_mocks.agent_boards_yellow import Yellow as YellowService
from tests.dbus_service_mocks.agent_datadisk import DataDisk as DataDiskService
from tests.dbus_service_mocks.base import DBusServiceMock


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

    assert result["data"]["data_disk"] == "BJTD4R-0x97cde291"


@pytest.mark.parametrize(
    "new_disk",
    ["/dev/sdaaaa", "/dev/mmcblk1", "Generic-Flash-Disk-61BCDDB6"],
    ids=["non-existent", "unavailable drive by path", "unavailable drive by id"],
)
async def test_api_os_datadisk_move_fail(
    api_client: TestClient,
    coresys: CoreSys,
    new_disk: str,
    os_available,
):
    """Test datadisk move to non-existent or invalid devices."""
    resp = await api_client.post("/os/datadisk/move", json={"device": new_disk})
    result = await resp.json()

    assert result["message"] == f"'{new_disk}' not a valid data disk target!"


async def test_api_os_datadisk_list(api_client: TestClient, coresys: CoreSys):
    """Test datadisk list function."""
    resp = await api_client.get("/os/datadisk/list")
    result = await resp.json()

    assert result["data"]["devices"] == ["SSK-SSK-Storage-DF56419883D56"]
    assert result["data"]["disks"] == [
        {
            "vendor": "SSK",
            "model": "SSK Storage",
            "serial": "DF56419883D56",
            "id": "SSK-SSK-Storage-DF56419883D56",
            "size": 250059350016,
            "dev_path": "/dev/sda",
            "name": "SSK SSK Storage (DF56419883D56)",
        }
    ]


@pytest.mark.parametrize(
    "new_disk",
    ["SSK-SSK-Storage-DF56419883D56", "/dev/sda"],
    ids=["by drive id", "by device path"],
)
async def test_api_os_datadisk_migrate(
    api_client: TestClient,
    coresys: CoreSys,
    os_agent_services: dict[str, DBusServiceMock],
    new_disk: str,
    os_available,
):
    """Test migrating datadisk."""
    datadisk_service: DataDiskService = os_agent_services["agent_datadisk"]
    datadisk_service.ChangeDevice.calls.clear()

    with patch.object(SystemControl, "reboot") as reboot:
        resp = await api_client.post("/os/datadisk/move", json={"device": new_disk})
        assert resp.status == 200

        assert datadisk_service.ChangeDevice.calls == [("/dev/sda",)]
        reboot.assert_called_once()


async def test_api_board_yellow_info(api_client: TestClient, coresys: CoreSys):
    """Test yellow board info."""
    resp = await api_client.get("/os/boards/yellow")
    assert resp.status == 200

    result = await resp.json()
    assert result["data"]["disk_led"] is True
    assert result["data"]["heartbeat_led"] is True
    assert result["data"]["power_led"] is True

    assert (await api_client.get("/os/boards/green")).status == 400
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
    with patch.object(BoardProxy, "save_data") as save_data:
        resp = await api_client.post(
            "/os/boards/yellow",
            json={"disk_led": False, "heartbeat_led": False, "power_led": False},
        )
        assert resp.status == 200
        save_data.assert_called_once()

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


async def test_api_board_green_info(
    api_client: TestClient, coresys: CoreSys, boards_service: BoardsService
):
    """Test green board info."""
    await mock_dbus_services({"agent_boards_green": None}, coresys.dbus.bus)
    boards_service.board = "Green"
    await coresys.dbus.agent.board.connect(coresys.dbus.bus)

    resp = await api_client.get("/os/boards/green")
    assert resp.status == 200

    result = await resp.json()
    assert result["data"]["activity_led"] is True
    assert result["data"]["power_led"] is True
    assert result["data"]["user_led"] is True

    assert (await api_client.get("/os/boards/yellow")).status == 400
    assert (await api_client.get("/os/boards/supervised")).status == 400
    assert (await api_client.get("/os/boards/not-real")).status == 400


async def test_api_board_green_options(
    api_client: TestClient,
    coresys: CoreSys,
    boards_service: BoardsService,
):
    """Test yellow board options."""
    green_service: GreenService = (
        await mock_dbus_services({"agent_boards_green": None}, coresys.dbus.bus)
    )["agent_boards_green"]
    boards_service.board = "Green"
    await coresys.dbus.agent.board.connect(coresys.dbus.bus)

    assert coresys.dbus.agent.board.green.activity_led is True
    assert coresys.dbus.agent.board.green.power_led is True
    assert coresys.dbus.agent.board.green.user_led is True
    assert len(coresys.resolution.issues) == 0
    with patch.object(BoardProxy, "save_data") as save_data:
        resp = await api_client.post(
            "/os/boards/green",
            json={"activity_led": False, "power_led": False, "user_led": False},
        )
        assert resp.status == 200
        save_data.assert_called_once()

    await green_service.ping()
    assert coresys.dbus.agent.board.green.activity_led is False
    assert coresys.dbus.agent.board.green.power_led is False
    assert coresys.dbus.agent.board.green.user_led is False
    assert len(coresys.resolution.issues) == 0


async def test_api_board_supervised_info(
    api_client: TestClient, coresys: CoreSys, boards_service: BoardsService
):
    """Test supervised board info."""
    await mock_dbus_services({"agent_boards_supervised": None}, coresys.dbus.bus)
    boards_service.board = "Supervised"
    await coresys.dbus.agent.board.connect(coresys.dbus.bus)

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
    await coresys.dbus.agent.board.connect(coresys.dbus.bus)

    with patch.object(OSManager, "board", new=PropertyMock(return_value="not-real")):
        assert (await api_client.get("/os/boards/not-real")).status == 200
        assert (await api_client.post("/os/boards/not-real", json={})).status == 405
        assert (await api_client.get("/os/boards/yellow")).status == 400
        assert (await api_client.get("/os/boards/supervised")).status == 400
