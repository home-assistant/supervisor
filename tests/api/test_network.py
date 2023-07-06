"""Test NetwrokInterface API."""
from unittest.mock import AsyncMock, patch

from aiohttp.test_utils import TestClient
from dbus_fast import Variant
import pytest

from supervisor.const import DOCKER_NETWORK, DOCKER_NETWORK_MASK
from supervisor.coresys import CoreSys

from tests.const import TEST_INTERFACE, TEST_INTERFACE_WLAN
from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.network_connection_settings import (
    ConnectionSettings as ConnectionSettingsService,
)
from tests.dbus_service_mocks.network_manager import (
    NetworkManager as NetworkManagerService,
)
from tests.dbus_service_mocks.network_settings import Settings as SettingsService


async def test_api_network_info(api_client: TestClient, coresys: CoreSys):
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
            assert interface["mac"] == "AA:BB:CC:DD:EE:FF"
        if interface["interface"] == TEST_INTERFACE_WLAN:
            assert not interface["primary"]
            assert interface["mac"] == "FF:EE:DD:CC:BB:AA"
            assert interface["ipv4"] == {
                "address": [],
                "gateway": None,
                "method": "disabled",
                "nameservers": [],
                "ready": False,
            }
            assert interface["ipv6"] == {
                "address": [],
                "gateway": None,
                "method": "disabled",
                "nameservers": [],
                "ready": False,
            }

    assert result["data"]["docker"]["interface"] == DOCKER_NETWORK
    assert result["data"]["docker"]["address"] == str(DOCKER_NETWORK_MASK)
    assert result["data"]["docker"]["dns"] == str(coresys.docker.network.dns)
    assert result["data"]["docker"]["gateway"] == str(coresys.docker.network.gateway)


@pytest.mark.parametrize("intr_id", [TEST_INTERFACE, "AA:BB:CC:DD:EE:FF"])
async def test_api_network_interface_info(api_client: TestClient, intr_id: str):
    """Test network manager api."""
    resp = await api_client.get(f"/network/interface/{intr_id}/info")
    result = await resp.json()
    assert result["data"]["ipv4"]["address"][-1] == "192.168.2.148/24"
    assert result["data"]["ipv4"]["gateway"] == "192.168.2.1"
    assert result["data"]["ipv4"]["nameservers"] == ["192.168.2.2"]
    assert result["data"]["ipv4"]["ready"] is True
    assert (
        result["data"]["ipv6"]["address"][0] == "2a03:169:3df5:0:6be9:2588:b26a:a679/64"
    )
    assert result["data"]["ipv6"]["address"][1] == "2a03:169:3df5::2f1/128"
    assert result["data"]["ipv6"]["gateway"] == "fe80::da58:d7ff:fe00:9c69"
    assert result["data"]["ipv6"]["nameservers"] == [
        "2001:1620:2777:1::10",
        "2001:1620:2777:2::20",
    ]
    assert result["data"]["ipv6"]["ready"] is True
    assert result["data"]["interface"] == TEST_INTERFACE


async def test_api_network_interface_info_default(api_client: TestClient):
    """Test network manager default api."""
    resp = await api_client.get("/network/interface/default/info")
    result = await resp.json()
    assert result["data"]["ipv4"]["address"][-1] == "192.168.2.148/24"
    assert result["data"]["ipv4"]["gateway"] == "192.168.2.1"
    assert result["data"]["ipv4"]["nameservers"] == ["192.168.2.2"]
    assert result["data"]["ipv4"]["ready"] is True
    assert (
        result["data"]["ipv6"]["address"][0] == "2a03:169:3df5:0:6be9:2588:b26a:a679/64"
    )
    assert result["data"]["ipv6"]["address"][1] == "2a03:169:3df5::2f1/128"
    assert result["data"]["ipv6"]["gateway"] == "fe80::da58:d7ff:fe00:9c69"
    assert result["data"]["ipv6"]["nameservers"] == [
        "2001:1620:2777:1::10",
        "2001:1620:2777:2::20",
    ]
    assert result["data"]["ipv6"]["ready"] is True
    assert result["data"]["interface"] == TEST_INTERFACE


@pytest.mark.parametrize("intr_id", [TEST_INTERFACE, "AA:BB:CC:DD:EE:FF"])
async def test_api_network_interface_update(
    api_client: TestClient,
    coresys: CoreSys,
    network_manager_service: NetworkManagerService,
    connection_settings_service: ConnectionSettingsService,
    intr_id: str,
):
    """Test network manager api."""
    network_manager_service.CheckConnectivity.calls.clear()
    connection_settings_service.Update.calls.clear()
    assert coresys.dbus.network.get(TEST_INTERFACE).settings.ipv4.method == "auto"

    resp = await api_client.post(
        f"/network/interface/{intr_id}/update",
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
    assert network_manager_service.CheckConnectivity.calls == [tuple()]
    assert len(connection_settings_service.Update.calls) == 1

    await connection_settings_service.ping()
    await connection_settings_service.ping()
    assert coresys.dbus.network.get(TEST_INTERFACE).settings.ipv4.method == "manual"


async def test_api_network_interface_update_wifi(api_client: TestClient):
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


async def test_api_network_interface_update_remove(api_client: TestClient):
    """Test network manager api."""
    resp = await api_client.post(
        f"/network/interface/{TEST_INTERFACE}/update",
        json={"enabled": False},
    )
    result = await resp.json()
    assert result["result"] == "ok"


async def test_api_network_interface_info_invalid(api_client: TestClient):
    """Test network manager api."""
    resp = await api_client.get("/network/interface/invalid/info")
    result = await resp.json()

    assert result["message"]
    assert result["result"] == "error"


async def test_api_network_interface_update_invalid(api_client: TestClient):
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


async def test_api_network_wireless_scan(api_client: TestClient):
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


async def test_api_network_reload(
    api_client: TestClient,
    coresys: CoreSys,
    network_manager_service: NetworkManagerService,
):
    """Test network manager reload api."""
    network_manager_service.CheckConnectivity.calls.clear()
    resp = await api_client.post("/network/reload")
    result = await resp.json()

    assert result["result"] == "ok"
    # Check that we forced NM to do an immediate connectivity check
    assert network_manager_service.CheckConnectivity.calls == [tuple()]


async def test_api_network_vlan(
    api_client: TestClient,
    coresys: CoreSys,
    network_manager_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
):
    """Test creating a vlan."""
    settings_service: SettingsService = network_manager_services["network_settings"]
    settings_service.AddConnection.calls.clear()
    resp = await api_client.post(
        f"/network/interface/{TEST_INTERFACE}/vlan/1", json={"ipv4": {"method": "auto"}}
    )
    result = await resp.json()
    assert result["result"] == "ok"
    assert len(settings_service.AddConnection.calls) == 1

    connection = settings_service.AddConnection.calls[0][0]
    assert "uuid" in connection["connection"]
    assert connection["connection"] == {
        "id": Variant("s", "Supervisor .1"),
        "type": Variant("s", "vlan"),
        "llmnr": Variant("i", 2),
        "mdns": Variant("i", 2),
        "autoconnect": Variant("b", True),
        "uuid": connection["connection"]["uuid"],
    }
    assert connection["ipv4"] == {"method": Variant("s", "auto")}
    assert connection["ipv6"] == {"method": Variant("s", "auto")}
    assert connection["vlan"] == {
        "id": Variant("u", 1),
        "parent": Variant("s", "eth0"),
    }
