"""Test Docker API."""

from pathlib import Path

from aiohttp.test_utils import TestClient
import pytest

from supervisor.coresys import CoreSys
from supervisor.hardware.data import Device


@pytest.mark.asyncio
async def test_api_hardware_info(api_client: TestClient):
    """Test docker info api."""
    resp = await api_client.get("/hardware/info")
    result = await resp.json()

    assert result["result"] == "ok"


@pytest.mark.asyncio
async def test_api_hardware_info_device(api_client: TestClient, coresys: CoreSys):
    """Test docker info api."""
    coresys.hardware.update_device(
        Device(
            "sda",
            Path("/dev/sda"),
            Path("/sys/bus/usb/000"),
            "sound",
            None,
            [Path("/dev/serial/by-id/test")],
            {"ID_NAME": "xy"},
            [],
        )
    )

    resp = await api_client.get("/hardware/info")
    result = await resp.json()

    assert result["result"] == "ok"
    assert result["data"]["devices"][-1]["name"] == "sda"
    assert result["data"]["devices"][-1]["by_id"] == "/dev/serial/by-id/test"


async def test_api_hardware_info_drives(api_client: TestClient, coresys: CoreSys):
    """Test drive info."""
    await coresys.dbus.udisks2.connect(coresys.dbus.bus)

    resp = await api_client.get("/hardware/info")
    result = await resp.json()

    assert result["result"] == "ok"
    assert {
        drive["id"]: {fs["id"] for fs in drive["filesystems"]}
        for drive in result["data"]["drives"]
    } == {
        "BJTD4R-0x97cde291": {
            "by-id-mmc-BJTD4R_0x97cde291-part1",
            "by-id-mmc-BJTD4R_0x97cde291-part3",
        },
        "SSK-SSK-Storage-DF56419883D56": {
            "by-id-usb-SSK_SSK_Storage_DF56419883D56-0:0-part1"
        },
        "Generic-Flash-Disk-61BCDDB6": {"by-uuid-2802-1EDE"},
    }
