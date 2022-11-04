"""Test OS API."""

import asyncio
from pathlib import Path
from unittest.mock import PropertyMock, patch

from aiohttp.test_utils import TestClient
import pytest

from supervisor.coresys import CoreSys
from supervisor.dbus.agent.boards import BoardManager
from supervisor.hardware.data import Device
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue, Suggestion

# pylint: disable=protected-access


@pytest.mark.asyncio
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
        "cpe_board",
    ):
        assert attr in result["data"]


@pytest.mark.asyncio
async def test_api_os_info_with_agent(api_client: TestClient, coresys: CoreSys):
    """Test docker info api."""
    await coresys.dbus.agent.connect(coresys.dbus.bus)
    await coresys.dbus.agent.update()

    resp = await api_client.get("/os/info")
    result = await resp.json()

    assert result["data"]["data_disk"] == "/dev/sda"


@pytest.mark.asyncio
async def test_api_os_datadisk_move(api_client: TestClient, coresys: CoreSys):
    """Test datadisk move without exists disk."""
    await coresys.dbus.agent.connect(coresys.dbus.bus)
    await coresys.dbus.agent.update()
    coresys.os._available = True

    resp = await api_client.post("/os/datadisk/move", json={"device": "/dev/sdaaaa"})
    result = await resp.json()

    assert result["message"] == "'/dev/sdaaaa' don't exists on the host!"


@pytest.mark.asyncio
async def test_api_os_datadisk_list(api_client: TestClient, coresys: CoreSys):
    """Test datadisk list function."""
    await coresys.dbus.agent.connect(coresys.dbus.bus)
    await coresys.dbus.agent.update()

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


@pytest.mark.parametrize("name", ["Yellow", "yellow"])
async def test_api_board_yellow_info(
    api_client: TestClient, coresys: CoreSys, name: str
):
    """Test yellow board info."""
    await coresys.dbus.agent.board.connect(coresys.dbus.bus)

    resp = await api_client.get(f"/os/boards/{name}")
    assert resp.status == 200

    result = await resp.json()
    assert result["data"]["disk_led"] is True
    assert result["data"]["heartbeat_led"] is True
    assert result["data"]["power_led"] is True

    assert (await api_client.get("/os/boards/supervised")).status == 400
    assert (await api_client.get("/os/boards/NotReal")).status == 400


@pytest.mark.parametrize("name", ["Yellow", "yellow"])
async def test_api_board_yellow_options(
    api_client: TestClient, coresys: CoreSys, dbus: list[str], name: str
):
    """Test yellow board options."""
    await coresys.dbus.agent.board.connect(coresys.dbus.bus)

    assert len(coresys.resolution.issues) == 0
    dbus.clear()
    resp = await api_client.post(
        f"/os/boards/{name}",
        json={"disk_led": False, "heartbeat_led": False, "power_led": False},
    )
    assert resp.status == 200

    await asyncio.sleep(0)
    assert dbus == [
        "/io/hass/os/Boards/Yellow-io.hass.os.Boards.Yellow.DiskLED",
        "/io/hass/os/Boards/Yellow-io.hass.os.Boards.Yellow.HeartbeatLED",
        "/io/hass/os/Boards/Yellow-io.hass.os.Boards.Yellow.PowerLED",
    ]

    assert (
        Issue(IssueType.REBOOT_REQUIRED, ContextType.SYSTEM)
        in coresys.resolution.issues
    )
    assert (
        Suggestion(SuggestionType.EXECUTE_REBOOT, ContextType.SYSTEM)
        in coresys.resolution.suggestions
    )


@pytest.mark.parametrize("name", ["Supervised", "supervised"])
async def test_api_board_supervised_info(
    api_client: TestClient, coresys: CoreSys, name: str
):
    """Test supervised board info."""
    with patch.object(
        BoardManager, "board", new=PropertyMock(return_value="Supervised")
    ):
        await coresys.dbus.agent.board.connect(coresys.dbus.bus)

        assert (await api_client.get(f"/os/boards/{name}")).status == 200
        assert (await api_client.post(f"/os/boards/{name}", json={})).status == 405
        assert (await api_client.get("/os/boards/yellow")).status == 400
        assert (await api_client.get("/os/boards/NotReal")).status == 400


async def test_api_board_other_info(api_client: TestClient, coresys: CoreSys):
    """Test info for other board without dbus object."""
    with patch.object(BoardManager, "board", new=PropertyMock(return_value="NotReal")):
        await coresys.dbus.agent.board.connect(coresys.dbus.bus)

        assert (await api_client.get("/os/boards/NotReal")).status == 200
        assert (await api_client.post("/os/boards/NotReal", json={})).status == 405
        assert (await api_client.get("/os/boards/yellow")).status == 400
        assert (await api_client.get("/os/boards/supervised")).status == 400
