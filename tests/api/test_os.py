"""Test OS API."""
import pytest

from supervisor.coresys import CoreSys


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
async def test_api_os_move_data(api_client, coresys: CoreSys):
    """Test docker info api."""
    await coresys.dbus.agent.connect()
    await coresys.dbus.agent.update()
    coresys.os._available = True

    resp = await api_client.post("/os/datadisk/move", json={"device": "/dev/sdaaaa"})
    result = await resp.json()

    assert result["message"] == "'/dev/sdaaaa' don't exists on the host!"
