"""Test NetwrokInterface API."""
import pytest

from tests.const import TEST_INTERFACE


@pytest.mark.asyncio
async def test_api_network_info(api_client):
    """Test network manager api."""
    resp = await api_client.get("/network/info")
    result = await resp.json()
    assert TEST_INTERFACE in result["data"]["interfaces"]


@pytest.mark.asyncio
async def test_api_network_interface_info(api_client):
    """Test network manager api."""
    resp = await api_client.get(f"/network/interface/{TEST_INTERFACE}/info")
    result = await resp.json()
    assert result["data"]["ip_address"] == "192.168.2.148/24"
    assert result["data"]["interface"] == TEST_INTERFACE


@pytest.mark.asyncio
async def test_api_network_interface_info_default(api_client):
    """Test network manager default api."""
    resp = await api_client.get("/network/interface/default/info")
    result = await resp.json()
    assert result["data"]["ip_address"] == "192.168.2.148/24"
    assert result["data"]["interface"] == TEST_INTERFACE


@pytest.mark.asyncio
async def test_api_network_interface_update(api_client):
    """Test network manager api."""
    resp = await api_client.post(
        f"/network/interface/{TEST_INTERFACE}/update",
        json={"method": "static", "dns": ["1.1.1.1"], "address": "192.168.2.148/24"},
    )
    result = await resp.json()
    assert result["result"] == "ok"


@pytest.mark.asyncio
async def test_api_network_interface_info_invalid(api_client):
    """Test network manager api."""
    resp = await api_client.get("/network/interface/invalid/info")
    result = await resp.json()
    assert not result["data"]


@pytest.mark.asyncio
async def test_api_network_interface_update_invalid(api_client):
    """Test network manager api."""
    resp = await api_client.post("/network/interface/invalid/update", json={})
    result = await resp.json()
    assert result["message"] == "Interface invalid does not exsist"

    resp = await api_client.post(f"/network/interface/{TEST_INTERFACE}/update", json={})
    result = await resp.json()
    assert result["message"] == "You need to supply at least one option to update"

    resp = await api_client.post(
        f"/network/interface/{TEST_INTERFACE}/update", json={"dns": "1.1.1.1"}
    )
    result = await resp.json()
    assert (
        result["message"]
        == "expected a list for dictionary value @ data['dns']. Got '1.1.1.1'"
    )
