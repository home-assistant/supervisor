"""Test NetwrokInterface API."""
from aiohttp import web
import pytest

from supervisor.api.network import APINetwork

from tests.const import TEST_INTERFACE


async def create_app(coresys):
    """Create web app for test."""
    app = web.Application()
    api_network = APINetwork()
    api_network.coresys = coresys
    app.add_routes(
        [
            web.get("/network/info", api_network.info),
            web.get("/network/interface/{interface}/info", api_network.interface_info),
            web.post(
                "/network/interface/{interface}/update", api_network.interface_update,
            ),
        ]
    )
    return app


@pytest.mark.asyncio
async def test_api_network_info(aiohttp_client, coresys):
    """Test network manager api."""
    client = await aiohttp_client(await create_app(coresys))
    resp = await client.get("/network/info")
    result = await resp.json()
    assert TEST_INTERFACE in result["data"]["interfaces"]


@pytest.mark.asyncio
async def test_api_network_interface_info(aiohttp_client, coresys):
    """Test network manager api."""
    client = await aiohttp_client(await create_app(coresys))
    resp = await client.get(f"/network/interface/{TEST_INTERFACE}/info")
    result = await resp.json()
    assert result["data"]["ip_address"] == "192.168.2.148/24"


@pytest.mark.asyncio
async def test_api_network_interface_update(aiohttp_client, coresys):
    """Test network manager api."""
    client = await aiohttp_client(await create_app(coresys))
    resp = await client.post(
        f"/network/interface/{TEST_INTERFACE}/update", json={"method": "static"}
    )
    result = await resp.json()
    assert result["result"] == "ok"


@pytest.mark.asyncio
async def test_api_network_interface_info_invalid(aiohttp_client, coresys):
    """Test network manager api."""
    client = await aiohttp_client(await create_app(coresys))
    resp = await client.get("/network/interface/invalid/info")
    result = await resp.json()
    assert not result["data"]


@pytest.mark.asyncio
async def test_api_network_interface_update_invalid(aiohttp_client, coresys):
    """Test network manager api."""
    client = await aiohttp_client(await create_app(coresys))
    resp = await client.post("/network/interface/invalid/update", json={})
    result = await resp.json()
    assert result["message"] == "Interface invalid does not exsist"

    resp = await client.post(f"/network/interface/{TEST_INTERFACE}/update", json={})
    result = await resp.json()
    assert result["message"] == "You need to supply at least one option to update"
