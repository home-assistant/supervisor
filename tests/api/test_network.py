"""Test NetwrokInterface API."""
import pytest

from supervisor.const import DOCKER_NETWORK, DOCKER_NETWORK_MASK

from tests.const import TEST_INTERFACE


@pytest.mark.asyncio
async def test_api_network_info(api_client, coresys):
    """Test network manager api."""
    resp = await api_client.get("/network/info")
    result = await resp.json()
    assert TEST_INTERFACE in result["data"]["interfaces"][-1]["interface"]

    assert result["data"]["docker"]["interface"] == DOCKER_NETWORK
    assert result["data"]["docker"]["address"] == str(DOCKER_NETWORK_MASK)
    assert result["data"]["docker"]["dns"] == str(coresys.docker.network.dns)
    assert result["data"]["docker"]["gateway"] == str(coresys.docker.network.gateway)


@pytest.mark.asyncio
async def test_api_network_interface_info(api_client):
    """Test network manager api."""
    resp = await api_client.get(f"/network/interface/{TEST_INTERFACE}/info")
    result = await resp.json()
    assert result["data"]["ipv4"]["address"][-1] == "192.168.2.148/24"
    assert result["data"]["ipv4"]["gateway"] == "192.168.2.1"
    assert result["data"]["ipv4"]["nameservers"] == ["192.168.2.2"]
    assert (
        result["data"]["ipv6"]["address"][0] == "2a03:169:3df5:0:6be9:2588:b26a:a679/64"
    )
    assert (
        result["data"]["ipv6"]["address"][1]
        == "fd14:949b:c9cc:0:522b:8108:8ff8:cca3/64"
    )
    assert result["data"]["ipv6"]["gateway"] == "fe80::da58:d7ff:fe00:9c69"
    assert result["data"]["ipv6"]["nameservers"] == [
        "2001:1620:2777:1::10",
        "2001:1620:2777:2::20",
    ]
    assert result["data"]["interface"] == TEST_INTERFACE


@pytest.mark.asyncio
async def test_api_network_interface_info_default(api_client):
    """Test network manager default api."""
    resp = await api_client.get("/network/interface/default/info")
    result = await resp.json()
    assert result["data"]["ipv4"]["address"][-1] == "192.168.2.148/24"
    assert result["data"]["ipv4"]["gateway"] == "192.168.2.1"
    assert result["data"]["ipv4"]["nameservers"] == ["192.168.2.2"]
    assert (
        result["data"]["ipv6"]["address"][0] == "2a03:169:3df5:0:6be9:2588:b26a:a679/64"
    )
    assert (
        result["data"]["ipv6"]["address"][1]
        == "fd14:949b:c9cc:0:522b:8108:8ff8:cca3/64"
    )
    assert result["data"]["ipv6"]["gateway"] == "fe80::da58:d7ff:fe00:9c69"
    assert result["data"]["ipv6"]["nameservers"] == [
        "2001:1620:2777:1::10",
        "2001:1620:2777:2::20",
    ]
    assert result["data"]["interface"] == TEST_INTERFACE


@pytest.mark.asyncio
async def test_api_network_interface_update(api_client):
    """Test network manager api."""
    resp = await api_client.post(
        f"/network/interface/{TEST_INTERFACE}/update",
        json={
            "ipv4": {
                "method": "static",
                "nameservers": ["1.1.1.1"],
                "address": ["192.168.2.148/24"],
                "gateway": "192.168.1.1",
            }
        },
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
        f"/network/interface/{TEST_INTERFACE}/update",
        json={"ipv4": {"nameservers": "1.1.1.1"}},
    )
    result = await resp.json()
    assert (
        result["message"]
        == "expected a list for dictionary value @ data['ipv4']['nameservers']. Got '1.1.1.1'"
    )
