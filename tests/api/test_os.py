"""Test OS API."""

from unittest.mock import AsyncMock, Mock, PropertyMock, patch

from aiohttp.test_utils import TestClient
from awesomeversion import AwesomeVersion
from dbus_fast import DBusError, ErrorType
import pytest

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.dbus.agent import OSAgent
from supervisor.dbus.agent.boards import BoardManager
from supervisor.dbus.agent.boards.interface import BoardProxy
from supervisor.exceptions import DBusError as SupervisorDBusError, HostError
from supervisor.host.control import SystemControl
from supervisor.os.manager import OSManager
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue, Suggestion

from tests.common import mock_dbus_services
from tests.dbus_service_mocks.agent_boards import Boards as BoardsService
from tests.dbus_service_mocks.agent_boards_green import Green as GreenService
from tests.dbus_service_mocks.agent_boards_rpi_firmware import (
    RPiFirmware as RPiFirmwareService,
)
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
    return os_agent_services["agent_boards"]


@pytest.fixture
async def os_agent_version(request: pytest.FixtureRequest) -> None:
    """Mock OS Agent version."""
    version = (
        AwesomeVersion(request.param)
        if hasattr(request, "param")
        else AwesomeVersion("1.9.0")
    )
    with patch.object(OSAgent, "version", new=PropertyMock(return_value=version)):
        yield


async def test_api_os_info(api_client_with_prefix: tuple[TestClient, str]):
    """Test os info api."""
    api_client, prefix = api_client_with_prefix
    resp = await api_client.get(f"{prefix}/os/info")
    result = await resp.json()

    for attr in (
        "version",
        "version_latest",
        "version_pending",
        "update_available",
        "board",
        "boot",
        "data_disk",
        "boot_slots",
    ):
        assert attr in result["data"]


async def test_api_os_info_with_agent(
    api_client_with_prefix: tuple[TestClient, str], coresys: CoreSys
):
    """Test os info api for data disk."""
    api_client, prefix = api_client_with_prefix
    resp = await api_client.get(f"{prefix}/os/info")
    result = await resp.json()

    assert result["data"]["data_disk"] == "BJTD4R-0x97cde291"


async def test_api_os_info_boot_slots(
    api_client_with_prefix: tuple[TestClient, str], coresys: CoreSys, os_available
):
    """Test os info api for boot slots."""
    api_client, prefix = api_client_with_prefix
    await coresys.os.load()
    resp = await api_client.get(f"{prefix}/os/info")
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
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    new_disk: str,
    os_available,
):
    """Test datadisk move to non-existent or invalid devices."""
    api_client, prefix = api_client_with_prefix
    resp = await api_client.post(
        f"{prefix}/os/datadisk/move", json={"device": new_disk}
    )
    result = await resp.json()

    assert result["message"] == f"'{new_disk}' not a valid data disk target!"


async def test_api_os_datadisk_list(
    api_client_with_prefix: tuple[TestClient, str], coresys: CoreSys
):
    """Test datadisk list function."""
    api_client, prefix = api_client_with_prefix
    resp = await api_client.get(f"{prefix}/os/datadisk/list")
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
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    os_agent_services: dict[str, DBusServiceMock],
    new_disk: str,
    os_available,
):
    """Test migrating datadisk."""
    api_client, prefix = api_client_with_prefix
    datadisk_service: DataDiskService = os_agent_services["agent_datadisk"]
    datadisk_service.ChangeDevice.calls.clear()

    with patch.object(SystemControl, "reboot") as reboot:
        resp = await api_client.post(
            f"{prefix}/os/datadisk/move", json={"device": new_disk}
        )
        assert resp.status == 200

        assert datadisk_service.ChangeDevice.calls == [("/dev/sda",)]
        reboot.assert_called_once()


async def test_api_os_datadisk_wipe(
    api_client_with_prefix: tuple[TestClient, str],
    os_agent_services: dict[str, DBusServiceMock],
    os_available,
):
    """Test datadisk wipe."""
    api_client, prefix = api_client_with_prefix
    system_service: SystemService = os_agent_services["agent_system"]
    system_service.ScheduleWipeDevice.calls.clear()

    with patch.object(SystemControl, "reboot") as reboot:
        resp = await api_client.post(f"{prefix}/os/datadisk/wipe")
        assert resp.status == 200

        assert system_service.ScheduleWipeDevice.calls == [()]
        reboot.assert_called_once()


async def test_api_set_boot_slot(
    api_client_with_prefix: tuple[TestClient, str],
    all_dbus_services: dict[str, DBusServiceMock],
    coresys: CoreSys,
    os_available,
):
    """Test changing the boot slot via API."""
    api_client, prefix = api_client_with_prefix
    rauc_service: RaucService = all_dbus_services["rauc"]
    rauc_service.Mark.calls.clear()
    await coresys.os.load()

    with patch.object(SystemControl, "reboot") as reboot:
        resp = await api_client.post(f"{prefix}/os/boot-slot", json={"boot_slot": "A"})
        assert resp.status == 200

        reboot.assert_called_once()
        assert rauc_service.Mark.calls == [("active", "kernel.0")]


async def test_api_set_boot_slot_invalid(
    api_client_with_prefix: tuple[TestClient, str],
):
    """Test invalid calls to set boot slot."""
    api_client, prefix = api_client_with_prefix
    resp = await api_client.post(f"{prefix}/os/boot-slot", json={"boot_slot": "C"})
    assert resp.status == 400
    result = await resp.json()
    assert "expected BootSlot or one of 'A', 'B'" in result["message"]

    resp = await api_client.post(f"{prefix}/os/boot-slot", json={"boot_slot": "A"})
    assert resp.status == 400
    result = await resp.json()
    assert "no Home Assistant OS available" in result["message"]


async def test_api_set_boot_slot_error(
    api_client_with_prefix: tuple[TestClient, str],
    all_dbus_services: dict[str, DBusServiceMock],
    coresys: CoreSys,
    capture_exception: Mock,
    os_available,
):
    """Test changing the boot slot via API."""
    api_client, prefix = api_client_with_prefix
    rauc_service: RaucService = all_dbus_services["rauc"]
    rauc_service.response_mark = DBusError(ErrorType.FAILED, "fail")
    await coresys.os.load()

    resp = await api_client.post(f"{prefix}/os/boot-slot", json={"boot_slot": "A"})
    assert resp.status == 400
    result = await resp.json()
    assert result["message"] == "Can't mark A as active!"
    capture_exception.assert_called_once()


async def test_api_os_update_no_auto_reboot_creates_issue(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    tmp_supervisor_data,
    path_extern: None,
    supervisor_internet,
    os_available,
):
    """Successful OS update does not auto-reboot and creates a reboot issue."""
    api_client, prefix = api_client_with_prefix
    await coresys.core.set_state(CoreState.RUNNING)

    async def fake_download(url, raucb) -> None:
        raucb.touch()

    with (
        patch.object(
            coresys.os,
            "_get_download_url",
            return_value="https://example.invalid/update.raucb",
        ),
        patch.object(coresys.os, "_download_raucb", side_effect=fake_download),
        patch.object(coresys.host.control, "reboot") as reboot,
    ):
        resp = await api_client.post(f"{prefix}/os/update", json={"version": "13.0"})

    assert resp.status == 200
    reboot.assert_not_called()
    assert (
        Issue(IssueType.REBOOT_REQUIRED, ContextType.SYSTEM)
        in coresys.resolution.issues
    )
    assert (
        Suggestion(SuggestionType.EXECUTE_REBOOT, ContextType.SYSTEM)
        in coresys.resolution.suggestions
    )

    resp = await api_client.get(f"{prefix}/os/info")
    result = await resp.json()
    assert result["data"]["version_pending"] == "13.0"
    # Installed update is reported as current version so Core releases
    # unaware of version_pending don't offer the update again
    assert result["data"]["version"] == "13.0"


async def test_api_os_update_failure_no_reboot_no_issue(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    tmp_supervisor_data,
    path_extern: None,
    supervisor_internet,
    os_available,
):
    """Failed OS update does not auto-reboot and does not create reboot issue."""
    api_client, prefix = api_client_with_prefix
    await coresys.core.set_state(CoreState.RUNNING)

    async def fake_download(url, raucb) -> None:
        raucb.touch()

    with (
        patch.object(
            coresys.os,
            "_get_download_url",
            return_value="https://example.invalid/update.raucb",
        ),
        patch.object(coresys.os, "_download_raucb", side_effect=fake_download),
        patch.object(
            coresys.dbus.rauc,
            "install",
            side_effect=SupervisorDBusError("fail"),
        ),
        patch.object(coresys.host.control, "reboot") as reboot,
    ):
        resp = await api_client.post(f"{prefix}/os/update", json={"version": "13.0"})

    assert resp.status == 400
    result = await resp.json()
    assert result["message"] == "Rauc communication error"
    reboot.assert_not_called()
    assert (
        Issue(IssueType.REBOOT_REQUIRED, ContextType.SYSTEM)
        not in coresys.resolution.issues
    )
    assert (
        Suggestion(SuggestionType.EXECUTE_REBOOT, ContextType.SYSTEM)
        not in coresys.resolution.suggestions
    )


async def test_api_board_yellow_info(
    api_client_with_prefix: tuple[TestClient, str], coresys: CoreSys
):
    """Test yellow board info."""
    api_client, prefix = api_client_with_prefix
    resp = await api_client.get(f"{prefix}/os/boards/yellow")
    assert resp.status == 200

    result = await resp.json()
    assert result["data"]["disk_led"] is True
    assert result["data"]["heartbeat_led"] is True
    assert result["data"]["power_led"] is True

    assert (await api_client.get(f"{prefix}/os/boards/green")).status == 400
    assert (await api_client.get(f"{prefix}/os/boards/supervised")).status == 400
    assert (await api_client.get(f"{prefix}/os/boards/not-real")).status == 400


async def test_api_board_yellow_options(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    os_agent_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
):
    """Test yellow board options."""
    api_client, prefix = api_client_with_prefix
    yellow_service: YellowService = os_agent_services["agent_boards_yellow"]

    assert coresys.dbus.agent.board.yellow.disk_led is True
    assert coresys.dbus.agent.board.yellow.heartbeat_led is True
    assert coresys.dbus.agent.board.yellow.power_led is True
    assert len(coresys.resolution.issues) == 0
    with patch.object(BoardProxy, "save_data") as save_data:
        resp = await api_client.post(
            f"{prefix}/os/boards/yellow",
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
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    boards_service: BoardsService,
):
    """Test green board info."""
    api_client, prefix = api_client_with_prefix
    await mock_dbus_services({"agent_boards_green": None}, coresys.dbus.bus)
    boards_service.board = "Green"
    await coresys.dbus.agent.board.connect(coresys.dbus.bus)

    resp = await api_client.get(f"{prefix}/os/boards/green")
    assert resp.status == 200

    result = await resp.json()
    assert result["data"]["activity_led"] is True
    assert result["data"]["power_led"] is True
    assert result["data"]["system_health_led"] is True

    assert (await api_client.get(f"{prefix}/os/boards/yellow")).status == 400
    assert (await api_client.get(f"{prefix}/os/boards/supervised")).status == 400
    assert (await api_client.get(f"{prefix}/os/boards/not-real")).status == 400


async def test_api_board_green_options(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    boards_service: BoardsService,
):
    """Test yellow board options."""
    api_client, prefix = api_client_with_prefix
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
            f"{prefix}/os/boards/green",
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
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    boards_service: BoardsService,
):
    """Test supervised board info."""
    api_client, prefix = api_client_with_prefix
    await mock_dbus_services({"agent_boards_supervised": None}, coresys.dbus.bus)
    boards_service.board = "Supervised"
    await coresys.dbus.agent.board.connect(coresys.dbus.bus)

    with patch("supervisor.os.manager.CPE.get_product", return_value=["not-hassos"]):
        await coresys.os.load()

        assert (await api_client.get(f"{prefix}/os/boards/supervised")).status == 200
        assert (
            await api_client.post(f"{prefix}/os/boards/supervised", json={})
        ).status == 405
        assert (await api_client.get(f"{prefix}/os/boards/yellow")).status == 400
        assert (await api_client.get(f"{prefix}/os/boards/not-real")).status == 400


async def test_api_board_other_info(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    boards_service: BoardsService,
):
    """Test info for other board without dbus object."""
    api_client, prefix = api_client_with_prefix
    boards_service.board = "not-real"
    await coresys.dbus.agent.board.connect(coresys.dbus.bus)

    with patch.object(OSManager, "board", new=PropertyMock(return_value="not-real")):
        assert (await api_client.get(f"{prefix}/os/boards/not-real")).status == 200
        assert (
            await api_client.post(f"{prefix}/os/boards/not-real", json={})
        ).status == 405
        assert (await api_client.get(f"{prefix}/os/boards/yellow")).status == 400
        assert (await api_client.get(f"{prefix}/os/boards/supervised")).status == 400


@pytest.mark.parametrize("os_available", ["15.0"], indirect=True)
async def test_api_config_swap_info(
    api_client_with_prefix: tuple[TestClient, str], coresys: CoreSys, os_available
):
    """Test swap info."""
    api_client, prefix = api_client_with_prefix
    await coresys.dbus.agent.swap.connect(coresys.dbus.bus)

    resp = await api_client.get(f"{prefix}/os/config/swap")

    assert resp.status == 200
    result = await resp.json()
    assert result["data"]["swap_size"] == "1M"
    assert result["data"]["swappiness"] == 1


@pytest.mark.parametrize("os_available", ["15.0"], indirect=True)
async def test_api_config_swap_options(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    os_agent_services: dict[str, DBusServiceMock],
    os_available,
):
    """Test swap setting."""
    api_client, prefix = api_client_with_prefix
    swap_service: SwapService = os_agent_services["agent_swap"]
    await coresys.dbus.agent.swap.connect(coresys.dbus.bus)

    assert coresys.dbus.agent.swap.swap_size == "1M"
    assert coresys.dbus.agent.swap.swappiness == 1

    resp = await api_client.post(
        f"{prefix}/os/config/swap",
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
        f"{prefix}/os/config/swap",
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
        f"{prefix}/os/config/swap",
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
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    os_agent_services: dict[str, DBusServiceMock],
    os_available,
):
    """Test no resolution is shown when setting are submitted empty or unchanged."""
    api_client, prefix = api_client_with_prefix
    await coresys.dbus.agent.swap.connect(coresys.dbus.bus)

    # empty options
    resp = await api_client.post(
        f"{prefix}/os/config/swap",
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
        f"{prefix}/os/config/swap",
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
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    os_agent_services: dict[str, DBusServiceMock],
):
    """Test 404 is returned for swap endpoints if not running on HAOS."""
    api_client, prefix = api_client_with_prefix
    await coresys.dbus.agent.swap.connect(coresys.dbus.bus)

    resp = await api_client.get(f"{prefix}/os/config/swap")
    assert resp.status == 404

    resp = await api_client.post(
        f"{prefix}/os/config/swap",
        json={
            "swap_size": "2M",
            "swappiness": 10,
        },
    )
    assert resp.status == 404


@pytest.mark.parametrize("os_available", ["14.2"], indirect=True)
async def test_api_config_swap_old_os(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    os_agent_services: dict[str, DBusServiceMock],
    os_available,
):
    """Test 404 is returned for swap endpoints if OS is older than 15.0."""
    api_client, prefix = api_client_with_prefix
    await coresys.dbus.agent.swap.connect(coresys.dbus.bus)

    resp = await api_client.get(f"{prefix}/os/config/swap")
    assert resp.status == 404

    resp = await api_client.post(
        f"{prefix}/os/config/swap",
        json={
            "swap_size": "2M",
            "swappiness": 10,
        },
    )
    assert resp.status == 404


@pytest.mark.usefixtures("os_agent_version")
async def test_api_board_raspberrypi_info(
    api_client_with_prefix: tuple[TestClient, str],
    os_agent_services: dict[str, DBusServiceMock],
    os_available,
):
    """Test Raspberry Pi firmware info endpoint."""
    api_client, prefix = api_client_with_prefix

    resp = await api_client.get(f"{prefix}/os/boards/raspberrypi/firmware")
    assert resp.status == 200
    result = await resp.json()
    assert result["data"] == {
        "current_version": "1618412973",
        "latest_version": "1700000000",
        "update_available": True,
        "update_blocked": False,
        "update_pending": False,
        "blocked_reason": None,
    }


@pytest.mark.usefixtures("os_agent_version")
async def test_api_board_raspberrypi_info_blocked_creates_issue(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    os_agent_services: dict[str, DBusServiceMock],
    os_available,
):
    """GET on raspberrypi info while blocked raises a repair issue."""
    api_client, prefix = api_client_with_prefix
    rpi_service: RPiFirmwareService = os_agent_services["agent_boards_rpi_firmware"]
    rpi_service.set_state(update_blocked=True, blocked_reason="unsupported_boot_device")
    await coresys.dbus.agent.board.rpi_firmware.update()

    resp = await api_client.get(f"{prefix}/os/boards/raspberrypi/firmware")
    assert resp.status == 200
    assert (
        Issue(IssueType.RPI_FIRMWARE_UPDATE_BLOCKED, ContextType.SYSTEM)
        in coresys.resolution.issues
    )

    # Clearing the blocked state dismisses the issue on the next info call.
    rpi_service.set_state(update_blocked=False, blocked_reason="")
    await coresys.dbus.agent.board.rpi_firmware.update()
    resp = await api_client.get(f"{prefix}/os/boards/raspberrypi/firmware")
    assert resp.status == 200
    assert (
        Issue(IssueType.RPI_FIRMWARE_UPDATE_BLOCKED, ContextType.SYSTEM)
        not in coresys.resolution.issues
    )


@pytest.mark.usefixtures("os_agent_version")
async def test_api_board_raspberrypi_update(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    os_agent_services: dict[str, DBusServiceMock],
    os_available,
):
    """Successful firmware update creates REBOOT_REQUIRED issue."""
    api_client, prefix = api_client_with_prefix
    rpi_service: RPiFirmwareService = os_agent_services["agent_boards_rpi_firmware"]
    assert rpi_service.update_called is False

    resp = await api_client.post(f"{prefix}/os/boards/raspberrypi/firmware/update")
    assert resp.status == 200

    await rpi_service.ping()
    assert rpi_service.update_called is True
    assert (
        Issue(IssueType.REBOOT_REQUIRED, ContextType.SYSTEM)
        in coresys.resolution.issues
    )
    assert (
        Suggestion(SuggestionType.EXECUTE_REBOOT, ContextType.SYSTEM)
        in coresys.resolution.suggestions
    )


@pytest.mark.usefixtures("os_agent_version")
async def test_api_board_raspberrypi_update_blocked(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    os_agent_services: dict[str, DBusServiceMock],
    os_available,
):
    """POST to raspberrypi update on a blocked device returns an error and surfaces the repair issue."""
    api_client, prefix = api_client_with_prefix
    rpi_service: RPiFirmwareService = os_agent_services["agent_boards_rpi_firmware"]
    rpi_service.set_state(update_blocked=True, blocked_reason="unsupported_boot_device")
    await coresys.dbus.agent.board.rpi_firmware.update()

    resp = await api_client.post(f"{prefix}/os/boards/raspberrypi/firmware/update")
    assert resp.status == 400
    assert rpi_service.update_called is False
    assert (
        Issue(IssueType.RPI_FIRMWARE_UPDATE_BLOCKED, ContextType.SYSTEM)
        in coresys.resolution.issues
    )
    # No reboot issue should be raised when the update was rejected.
    assert (
        Issue(IssueType.REBOOT_REQUIRED, ContextType.SYSTEM)
        not in coresys.resolution.issues
    )


@pytest.mark.parametrize("os_agent_version", ["1.8.0"], indirect=True)
async def test_api_board_raspberrypi_requires_os_agent_version(
    api_client_with_prefix: tuple[TestClient, str],
    os_agent_services: dict[str, DBusServiceMock],
    os_available,
    os_agent_version,  # pylint: disable=redefined-outer-name
):
    """Test 404 is returned for raspberrypi endpoints on an OS Agent older than 1.9.0."""
    api_client, prefix = api_client_with_prefix

    resp = await api_client.get(f"{prefix}/os/boards/raspberrypi/firmware")
    assert resp.status == 404

    resp = await api_client.post(f"{prefix}/os/boards/raspberrypi/firmware/update")
    assert resp.status == 404


@pytest.mark.usefixtures("os_agent_version")
async def test_api_board_raspberrypi_firmware_unavailable_on_board(
    api_client_with_prefix: tuple[TestClient, str],
    os_agent_services: dict[str, DBusServiceMock],
    os_available,
):
    """Test 404 is returned for raspberrypi endpoints on a board without firmware."""
    api_client, prefix = api_client_with_prefix

    with patch.object(
        BoardManager, "has_rpi_firmware", new=PropertyMock(return_value=False)
    ):
        resp = await api_client.get(f"{prefix}/os/boards/raspberrypi/firmware")
        assert resp.status == 404

        resp = await api_client.post(f"{prefix}/os/boards/raspberrypi/firmware/update")
        assert resp.status == 404


TEST_SSH_KEY_ED25519 = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDXD8u9KB94/l1YukYflKOsO7KzoSEQD4dNNlWY9zaQP test@example.com"
TEST_SSH_KEY_ECDSA = "ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBIGeXP8EbMxj8Ws5m7tdN5YR9BryZNyG+L9670o7eSZog4G03n16bs7Yz0oV1J4sWOkhZNUak6g3IM1jnMLFvgE= ecdsa@example"


@pytest.mark.usefixtures("os_available")
async def test_api_os_ssh_authorized_keys(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    os_agent_services: dict[str, DBusServiceMock],
):
    """Test replacing SSH authorized keys clears and adds them in order."""
    api_client, prefix = api_client_with_prefix
    system_service: SystemService = os_agent_services["agent_system"]
    system_service.AddSSHAuthKey.calls.clear()
    system_service.ClearSSHAuthKeys.calls.clear()

    with patch.object(coresys.host.services, "start", new=AsyncMock()) as start:
        resp = await api_client.post(
            f"{prefix}/os/ssh/authorized_keys",
            # Trailing newline from a pasted key is stripped before writing
            json={"keys": [TEST_SSH_KEY_ED25519 + "\n", TEST_SSH_KEY_ECDSA]},
        )
    assert resp.status == 200

    assert system_service.ClearSSHAuthKeys.calls == [()]
    assert system_service.AddSSHAuthKey.calls == [
        (TEST_SSH_KEY_ED25519,),
        (TEST_SSH_KEY_ECDSA,),
    ]
    # dropbear only starts if authorized_keys is non-empty when the unit
    # starts, so a stopped service must be started after adding keys
    start.assert_called_once_with("dropbear.service")


@pytest.mark.usefixtures("os_available")
async def test_api_os_ssh_authorized_keys_empty_list_clears(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    os_agent_services: dict[str, DBusServiceMock],
):
    """Test an empty key list only clears the authorized keys."""
    api_client, prefix = api_client_with_prefix
    system_service: SystemService = os_agent_services["agent_system"]
    system_service.AddSSHAuthKey.calls.clear()
    system_service.ClearSSHAuthKeys.calls.clear()

    with patch.object(coresys.host.services, "start", new=AsyncMock()) as start:
        resp = await api_client.post(
            f"{prefix}/os/ssh/authorized_keys", json={"keys": []}
        )
    assert resp.status == 200

    assert system_service.ClearSSHAuthKeys.calls == [()]
    assert system_service.AddSSHAuthKey.calls == []
    start.assert_not_called()


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"keys": TEST_SSH_KEY_ED25519},
        {"keys": [42]},
        {"keys": [""]},
        # Newline injection must not smuggle extra authorized_keys lines
        {"keys": [f"{TEST_SSH_KEY_ED25519}\n{TEST_SSH_KEY_ECDSA}"]},
        {"keys": [TEST_SSH_KEY_ED25519.replace(" test@", "\x1b test@")]},
        # dropbear ignores authorized_keys lines longer than 3000 bytes
        {"keys": [f"{TEST_SSH_KEY_ED25519} {'a' * 3000}"]},
    ],
    ids=[
        "missing keys",
        "keys not a list",
        "key not a string",
        "empty key",
        "newline injection",
        "control character",
        "oversized key",
    ],
)
@pytest.mark.usefixtures("os_available")
async def test_api_os_ssh_authorized_keys_invalid(
    api_client_with_prefix: tuple[TestClient, str],
    os_agent_services: dict[str, DBusServiceMock],
    body: dict,
):
    """Test malformed bodies are rejected before touching the host."""
    api_client, prefix = api_client_with_prefix
    system_service: SystemService = os_agent_services["agent_system"]
    system_service.AddSSHAuthKey.calls.clear()
    system_service.ClearSSHAuthKeys.calls.clear()

    resp = await api_client.post(f"{prefix}/os/ssh/authorized_keys", json=body)
    assert resp.status == 400

    assert system_service.ClearSSHAuthKeys.calls == []
    assert system_service.AddSSHAuthKey.calls == []


@pytest.mark.parametrize(
    ("os_agent_version", "expected_status"),
    [("1.9.0", 200), ("1.10.0", 400)],
    indirect=["os_agent_version"],
)
@pytest.mark.usefixtures("os_available", "os_agent_version")
async def test_api_os_ssh_authorized_keys_old_os_agent_clear_missing_file(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    os_agent_services: dict[str, DBusServiceMock],
    expected_status: int,
):
    """Test the missing-file clear error is only tolerated on affected OS Agents.

    OS Agent before 1.10.0 returns an error when the file is already absent
    (inverted error check); on 1.10.0 or newer the same error is genuine.
    """
    api_client, prefix = api_client_with_prefix
    system_service: SystemService = os_agent_services["agent_system"]
    system_service.AddSSHAuthKey.calls.clear()
    system_service.response_clear_ssh_auth_keys = DBusError(
        ErrorType.FAILED,
        "remove /root/.ssh/authorized_keys: no such file or directory",
    )

    with patch.object(coresys.host.services, "start", new=AsyncMock()) as start:
        resp = await api_client.post(
            f"{prefix}/os/ssh/authorized_keys", json={"keys": [TEST_SSH_KEY_ED25519]}
        )
    assert resp.status == expected_status

    if expected_status == 200:
        assert system_service.AddSSHAuthKey.calls == [(TEST_SSH_KEY_ED25519,)]
        start.assert_called_once_with("dropbear.service")
    else:
        result = await resp.json()
        assert "Can't clear SSH authorized keys" in result["message"]
        assert system_service.AddSSHAuthKey.calls == []
        start.assert_not_called()


async def test_api_os_ssh_authorized_keys_no_os(
    api_client_with_prefix: tuple[TestClient, str],
    os_agent_services: dict[str, DBusServiceMock],
):
    """Test SSH authorized keys endpoint requires Home Assistant OS."""
    api_client, prefix = api_client_with_prefix
    resp = await api_client.post(
        f"{prefix}/os/ssh/authorized_keys", json={"keys": [TEST_SSH_KEY_ED25519]}
    )
    assert resp.status == 400
    result = await resp.json()
    assert "no Home Assistant OS available" in result["message"]


@pytest.mark.usefixtures("os_available")
async def test_api_os_ssh_authorized_keys_rejected_key(
    api_client_with_prefix: tuple[TestClient, str],
    os_agent_services: dict[str, DBusServiceMock],
):
    """Test a key rejected by OS Agent validation is reported."""
    api_client, prefix = api_client_with_prefix
    system_service: SystemService = os_agent_services["agent_system"]
    system_service.response_add_ssh_auth_key = DBusError(
        ErrorType.FAILED, "invalid SSH authorized key: ssh: no key found"
    )

    resp = await api_client.post(
        f"{prefix}/os/ssh/authorized_keys", json={"keys": ["not a key"]}
    )
    assert resp.status == 400
    result = await resp.json()
    assert "Can't add SSH authorized key" in result["message"]
    assert "invalid SSH authorized key" in result["message"]


@pytest.mark.usefixtures("os_available")
async def test_api_os_ssh_authorized_keys_clear_error(
    api_client_with_prefix: tuple[TestClient, str],
    os_agent_services: dict[str, DBusServiceMock],
):
    """Test a clear failure aborts the replacement."""
    api_client, prefix = api_client_with_prefix
    system_service: SystemService = os_agent_services["agent_system"]
    system_service.AddSSHAuthKey.calls.clear()
    system_service.response_clear_ssh_auth_keys = DBusError(
        ErrorType.FAILED, "remove /root/.ssh/authorized_keys: permission denied"
    )

    resp = await api_client.post(
        f"{prefix}/os/ssh/authorized_keys", json={"keys": [TEST_SSH_KEY_ED25519]}
    )
    assert resp.status == 400
    result = await resp.json()
    assert "Can't clear SSH authorized keys" in result["message"]
    assert system_service.AddSSHAuthKey.calls == []


@pytest.mark.usefixtures("os_available")
async def test_api_os_ssh_authorized_keys_dropbear_start_error(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    os_agent_services: dict[str, DBusServiceMock],
):
    """Test a dropbear start failure is reported after keys were written."""
    api_client, prefix = api_client_with_prefix

    with patch.object(
        coresys.host.services, "start", new=AsyncMock(side_effect=HostError("boom"))
    ):
        resp = await api_client.post(
            f"{prefix}/os/ssh/authorized_keys", json={"keys": [TEST_SSH_KEY_ED25519]}
        )
    assert resp.status == 400
    result = await resp.json()
    assert "can't start dropbear" in result["message"]
