"""Test Docker API."""
from pathlib import Path

import pytest

from supervisor.hardware.data import Device


@pytest.mark.asyncio
async def test_api_hardware_info(api_client):
    """Test docker info api."""
    resp = await api_client.get("/hardware/info")
    result = await resp.json()

    assert result["result"] == "ok"


@pytest.mark.asyncio
async def test_api_hardware_info_device(api_client, coresys):
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
