"""Test OS API."""

from unittest.mock import Mock, PropertyMock, patch

from aiohttp.test_utils import TestClient
from dbus_fast import DBusError, ErrorType
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
from tests.dbus_service_mocks.agent_swap import Swap as SwapService
from tests.dbus_service_mocks.agent_system import System as SystemService
from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.rauc import Rauc as RaucService


@pytest.fixture(name="boards_service")
async def fixture_boards_service(
    os_agent_services: dict[str, DBusServiceMock],
) -> BoardsService:
    """Return mock Boards service."""
    yield os_agent_services["agent_boards"]


async def test_api_os_info(api_client: TestClient):
    """Test os info api."""
    resp = await api_client.get("/os/info")
    result = await resp.json()

    for attr in (
        "version",
        "version_latest",
        "update_available",
        "board",
        "boot",
        "data_disk",
        "boot_slots",
    ):
        assert attr in result["data"]


async def test_api_os_info_with_agent(api_client: TestClient, coresys: CoreSys):
    """Test os info api for data disk."""
    resp = await api_client.get("/os/info")
    result = await resp.json()

    assert result["data"]["data_disk"] == "BJTD4R-0x97cde291"


async def test_api_os_info_boot_slots(
    api_client: TestClient, coresys: CoreSys, os_available
):
    """Test os info api for boot slots."""
    await coresys.os.load()
    resp = await api_client.get("/os/info")
    result = await resp.json()

    assert result["data"]["boot_slots"] == {
        "A": {
            "state": "inactive",
            "status": "good",
            "version": "9.0.dev20220818",
        },
        "B": {"state": "booted", "status": "good", "version": "9.0.dev20220824"},
    }


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


async def test_api_os_datadisk_wipe(
    api_client: TestClient,
    os_agent_services: dict[str, DBusServiceMock],
    os_available,
):
    """Test datadisk wipe."""
    system_service: SystemService = os_agent_services["agent_system"]
    system_service.ScheduleWipeDevice.calls.clear()

    with patch.object(SystemControl, "reboot") as reboot:
        resp = await api_client.post("/os/datadisk/wipe")
        assert resp.status == 200

        assert system_service.ScheduleWipeDevice.calls == [()]
        reboot.assert_called_once()


async def test_api_set_boot_slot(
    api_client: TestClient,
    all_dbus_services: dict[str, DBusServiceMock],
    coresys: CoreSys,
    os_available,
):
    """Test changing the boot slot via API."""
    rauc_service: RaucService = all_dbus_services["rauc"]
    await coresys.os.load()

    with patch.object(SystemControl, "reboot") as reboot:
        resp = await api_client.post("/os/boot-slot", json={"boot_slot": "A"})
        assert resp.status == 200

        reboot.assert_called_once()
        assert rauc_service.Mark.calls == [("active", "kernel.0")]


async def test_api_set_boot_slot_invalid(api_client: TestClient):
    """Test invalid calls to set boot slot."""
    resp = await api_client.post("/os/boot-slot", json={"boot_slot": "C"})
    assert resp.status == 400
    result = await resp.json()
    assert "expected BootSlot or one of 'A', 'B'" in result["message"]

    resp = await api_client.post("/os/boot-slot", json={"boot_slot": "A"})
    assert resp.status == 400
    result = await resp.json()
    assert "no Home Assistant OS available" in result["message"]


async def test_api_set_boot_slot_error(
    api_client: TestClient,
    all_dbus_services: dict[str, DBusServiceMock],
    coresys: CoreSys,
    capture_exception: Mock,
    os_available,
):
    """Test changing the boot slot via API."""
    rauc_service: RaucService = all_dbus_services["rauc"]
    rauc_service.response_mark = DBusError(ErrorType.FAILED, "fail")
    await coresys.os.load()

    resp = await api_client.post("/os/boot-slot", json={"boot_slot": "A"})
    assert resp.status == 400
    result = await resp.json()
    assert result["message"] == "Can't mark A as active!"
    capture_exception.assert_called_once()


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
    assert result["data"]["system_health_led"] is True

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
            json={
                "activity_led": False,
                "power_led": False,
                "system_health_led": False,
            },
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


@pytest.mark.parametrize("os_available", ["15.0"], indirect=True)
async def test_api_config_swap_info(
    api_client: TestClient, coresys: CoreSys, os_available
):
    """Test swap info."""
    await coresys.dbus.agent.swap.connect(coresys.dbus.bus)

    resp = await api_client.get("/os/config/swap")

    assert resp.status == 200
    result = await resp.json()
    assert result["data"]["swap_size"] == "1M"
    assert result["data"]["swappiness"] == 1


@pytest.mark.parametrize("os_available", ["15.0"], indirect=True)
async def test_api_config_swap_options(
    api_client: TestClient,
    coresys: CoreSys,
    os_agent_services: dict[str, DBusServiceMock],
    os_available,
):
    """Test swap setting."""
    swap_service: SwapService = os_agent_services["agent_swap"]
    await coresys.dbus.agent.swap.connect(coresys.dbus.bus)

    assert coresys.dbus.agent.swap.swap_size == "1M"
    assert coresys.dbus.agent.swap.swappiness == 1

    resp = await api_client.post(
        "/os/config/swap",
        json={
            "swap_size": "2M",
            "swappiness": 10,
        },
    )
    assert resp.status == 200

    await swap_service.ping()

    assert coresys.dbus.agent.swap.swap_size == "2M"
    assert coresys.dbus.agent.swap.swappiness == 10

    assert (
        Issue(IssueType.REBOOT_REQUIRED, ContextType.SYSTEM)
        in coresys.resolution.issues
    )
    assert (
        Suggestion(SuggestionType.EXECUTE_REBOOT, ContextType.SYSTEM)
        in coresys.resolution.suggestions
    )

    # test setting only the swap size
    resp = await api_client.post(
        "/os/config/swap",
        json={
            "swap_size": "10M",
        },
    )
    assert resp.status == 200

    await swap_service.ping()

    assert coresys.dbus.agent.swap.swap_size == "10M"
    assert coresys.dbus.agent.swap.swappiness == 10

    # test setting only the swappiness
    resp = await api_client.post(
        "/os/config/swap",
        json={
            "swappiness": 100,
        },
    )
    assert resp.status == 200

    await swap_service.ping()

    assert coresys.dbus.agent.swap.swap_size == "10M"
    assert coresys.dbus.agent.swap.swappiness == 100


@pytest.mark.parametrize("os_available", ["15.0"], indirect=True)
async def test_api_config_swap_options_no_reboot(
    api_client: TestClient,
    coresys: CoreSys,
    os_agent_services: dict[str, DBusServiceMock],
    os_available,
):
    """Test no resolution is shown when setting are submitted empty or unchanged."""
    await coresys.dbus.agent.swap.connect(coresys.dbus.bus)

    # empty options
    resp = await api_client.post(
        "/os/config/swap",
        json={},
    )
    assert resp.status == 200
    assert (
        Issue(IssueType.REBOOT_REQUIRED, ContextType.SYSTEM)
        not in coresys.resolution.issues
    )
    assert (
        Suggestion(SuggestionType.EXECUTE_REBOOT, ContextType.SYSTEM)
        not in coresys.resolution.suggestions
    )

    # no change
    resp = await api_client.post(
        "/os/config/swap",
        json={
            "swappiness": coresys.dbus.agent.swap.swappiness,
            "swap_size": coresys.dbus.agent.swap.swap_size,
        },
    )
    assert resp.status == 200
    assert (
        Issue(IssueType.REBOOT_REQUIRED, ContextType.SYSTEM)
        not in coresys.resolution.issues
    )
    assert (
        Suggestion(SuggestionType.EXECUTE_REBOOT, ContextType.SYSTEM)
        not in coresys.resolution.suggestions
    )


async def test_api_config_swap_not_os(
    api_client: TestClient,
    coresys: CoreSys,
    os_agent_services: dict[str, DBusServiceMock],
):
    """Test 404 is returned for swap endpoints if not running on HAOS."""
    await coresys.dbus.agent.swap.connect(coresys.dbus.bus)

    resp = await api_client.get("/os/config/swap")
    assert resp.status == 404

    resp = await api_client.post(
        "/os/config/swap",
        json={
            "swap_size": "2M",
            "swappiness": 10,
        },
    )
    assert resp.status == 404


@pytest.mark.parametrize("os_available", ["14.2"], indirect=True)
async def test_api_config_swap_old_os(
    api_client: TestClient,
    coresys: CoreSys,
    os_agent_services: dict[str, DBusServiceMock],
    os_available,
):
    """Test 404 is returned for swap endpoints if OS is older than 15.0."""
    await coresys.dbus.agent.swap.connect(coresys.dbus.bus)

    resp = await api_client.get("/os/config/swap")
    assert resp.status == 404

    resp = await api_client.post(
        "/os/config/swap",
        json={
            "swap_size": "2M",
            "swappiness": 10,
        },
    )
    assert resp.status == 404
