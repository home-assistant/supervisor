"""Test OS API."""
from pathlib import Path

import pytest

from supervisor.coresys import CoreSys
from supervisor.hardware.data import Device

# pylint: disable=protected-access


@pytest.mark.asyncio
async def test_api_os_info(api_client):
    """Test docker info api."""
    resp = await api_client.get("/os/info")
    result = await resp.json()

    for attr in (
        "version",
        "version_latest",
        "update_available",
        "board",
        "boot",
        "disk_data",
    ):
        assert attr in result["data"]


@pytest.mark.asyncio
async def test_api_os_info_with_agent(api_client, coresys: CoreSys):
    """Test docker info api."""
    await coresys.dbus.agent.connect()
    await coresys.dbus.agent.update()

    resp = await api_client.get("/os/info")
    result = await resp.json()

    assert result["data"]["disk_data"] == "/dev/sda"


@pytest.mark.asyncio
async def test_api_os_datadisk_move(api_client, coresys: CoreSys):
    """Test docker info api."""
    await coresys.dbus.agent.connect()
    await coresys.dbus.agent.update()
    coresys.os._available = True

    resp = await api_client.post("/os/datadisk/move", json={"device": "/dev/sdaaaa"})
    result = await resp.json()

    assert result["message"] == "'/dev/sdaaaa' don't exists on the host!"


@pytest.mark.asyncio
async def test_api_os_datadisk_list(api_client, coresys: CoreSys):
    """Test docker info api."""
    await coresys.dbus.agent.connect()
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
