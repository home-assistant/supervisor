"""Test NetwrokInterface API."""
from unittest.mock import AsyncMock, patch

import pytest

from supervisor.const import DOCKER_NETWORK, DOCKER_NETWORK_MASK

from tests.const import TEST_INTERFACE, TEST_INTERFACE_WLAN


@pytest.mark.asyncio
async def test_api_network_info(api_client, coresys):
    """Test network manager api."""
    resp = await api_client.get("/network/info")
    result = await resp.json()
    assert TEST_INTERFACE in (
        inet["interface"] for inet in result["data"]["interfaces"]
    )
    assert TEST_INTERFACE_WLAN in (
        inet["interface"] for inet in result["data"]["interfaces"]
    )

    for interface in result["data"]["interfaces"]:
        if interface["interface"] == TEST_INTERFACE:
            assert interface["primary"]
            assert interface["ipv4"]["gateway"] == "192.168.2.1"
        if interface["interface"] == TEST_INTERFACE_WLAN:
            assert not interface["primary"]
            assert interface["ipv4"] == {
                "address": [],
                "gateway": None,
                "method": "disabled",
                "nameservers": [],
            }
            assert interface["ipv6"] == {
                "address": [],
                "gateway": None,
                "method": "disabled",
                "nameservers": [],
            }

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
async def test_api_network_interface_update_wifi(api_client):
    """Test network manager api."""
    resp = await api_client.post(
        f"/network/interface/{TEST_INTERFACE_WLAN}/update",
        json={
            "enabled": True,
            "ipv4": {
                "method": "static",
                "nameservers": ["1.1.1.1"],
                "address": ["192.168.2.148/24"],
                "gateway": "192.168.1.1",
            },
            "wifi": {"ssid": "MY_TEST", "auth": "wpa-psk", "psk": "myWifiPassword"},
        },
    )
    result = await resp.json()
    assert result["result"] == "ok"


@pytest.mark.asyncio
async def test_api_network_interface_update_remove(api_client):
    """Test network manager api."""
    resp = await api_client.post(
        f"/network/interface/{TEST_INTERFACE}/update",
        json={"enabled": False},
    )
    result = await resp.json()
    assert result["result"] == "ok"


@pytest.mark.asyncio
async def test_api_network_interface_info_invalid(api_client):
    """Test network manager api."""
    resp = await api_client.get("/network/interface/invalid/info")
    result = await resp.json()

    assert result["message"]
    assert result["result"] == "error"


@pytest.mark.asyncio
async def test_api_network_interface_update_invalid(api_client):
    """Test network manager api."""
    resp = await api_client.post("/network/interface/invalid/update", json={})
    result = await resp.json()
    assert result["message"] == "Interface invalid does not exist"

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


@pytest.mark.asyncio
async def test_api_network_wireless_scan(api_client):
    """Test network manager api."""
    with patch("asyncio.sleep", return_value=AsyncMock()):
        resp = await api_client.get(
            f"/network/interface/{TEST_INTERFACE_WLAN}/accesspoints"
        )
    result = await resp.json()

    assert ["UPC4814466", "VQ@35(55720"] == [
        ap["ssid"] for ap in result["data"]["accesspoints"]
    ]
    assert [47, 63] == [ap["signal"] for ap in result["data"]["accesspoints"]]


@pytest.mark.asyncio
async def test_api_network_reload(api_client, coresys):
    """Test network manager reload api."""
    resp = await api_client.post("/network/reload")
    result = await resp.json()

    assert result["result"] == "ok"
