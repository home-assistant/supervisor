"""Test network v2 API."""

from unittest.mock import AsyncMock, patch

from aiohttp.test_utils import TestClient
from dbus_fast import Variant
import pytest

from supervisor.const import DOCKER_IPV4_NETWORK_MASK, DOCKER_NETWORK
from supervisor.coresys import CoreSys

from tests.const import TEST_INTERFACE_ETH_NAME, TEST_INTERFACE_WLAN_NAME
from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.network_connection_settings import (
    ConnectionSettings as ConnectionSettingsService,
)
from tests.dbus_service_mocks.network_device import Device as DeviceService
from tests.dbus_service_mocks.network_manager import (
    NetworkManager as NetworkManagerService,
)


@pytest.fixture(name="device_eth0_service")
async def fixture_device_eth0_service(
    network_manager_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
) -> DeviceService:
    """Return mock device eth0 service."""
    return network_manager_services["network_device"][
        "/org/freedesktop/NetworkManager/Devices/1"
    ]


async def test_api_network_info_v2(api_client_v2: TestClient, coresys: CoreSys):
    """Test v2 network info shape."""
    resp = await api_client_v2.get("/v2/network/info")
    result = await resp.json()

    names = {inet["name"] for inet in result["data"]["interfaces"]}
    assert TEST_INTERFACE_ETH_NAME in names
    assert TEST_INTERFACE_WLAN_NAME in names

    for interface in result["data"]["interfaces"]:
        assert "path" in interface
        assert "state" in interface
        assert "config" in interface
        assert "addresses" in interface["state"]["ipv4"]
        if interface["name"] == TEST_INTERFACE_ETH_NAME:
            assert interface["config"] is not None
            assert interface["config"]["wifi"] is None

    assert result["data"]["docker"]["interface"] == DOCKER_NETWORK
    assert result["data"]["docker"]["address"] == str(DOCKER_IPV4_NETWORK_MASK)
    assert result["data"]["docker"]["dns"] == str(coresys.docker.network.dns)
    assert result["data"]["docker"]["gateway"] == str(coresys.docker.network.gateway)


async def test_api_network_interface_info_v2(api_client_v2: TestClient):
    """Test v2 network interface info state/config split."""
    resp = await api_client_v2.get(f"/v2/network/interfaces/{TEST_INTERFACE_ETH_NAME}")
    result = await resp.json()
    data = result["data"]

    assert data["name"] == TEST_INTERFACE_ETH_NAME
    assert data["mac"] == "AA:BB:CC:DD:EE:FF"

    state = data["state"]
    assert state["ipv4"]["addresses"][-1] == "192.168.2.148/24"
    assert state["ipv4"]["gateway"] == "192.168.2.1"
    assert state["ipv4"]["nameservers"] == ["192.168.2.2"]
    assert state["ipv4"]["ready"] is True
    assert state["ipv6"]["addresses"][0] == "2a03:169:3df5:0:6be9:2588:b26a:a679/64"
    assert state["ipv6"]["gateway"] == "fe80::da58:d7ff:fe00:9c69"

    config = data["config"]
    assert config is not None
    assert config["enabled"] is True
    assert config["ipv4"]["method"] == "auto"
    assert config["mdns"] == "announce"
    assert config["llmnr"] == "announce"


async def test_api_network_interface_info_v2_default_not_found(
    api_client_v2: TestClient,
):
    """Test the v1-only `default` alias is not available on v2."""
    resp = await api_client_v2.get("/v2/network/interfaces/default")
    assert resp.status == 404
    result = await resp.json()
    assert result["message"] == "Interface default does not exist"


async def test_api_network_interface_info_v2_config_null(
    api_client_v2: TestClient,
):
    """Test config is null when no stored profile could be resolved at all."""
    resp = await api_client_v2.get(f"/v2/network/interfaces/{TEST_INTERFACE_WLAN_NAME}")
    result = await resp.json()
    assert result["data"]["config"] is None


async def test_api_network_update_config_v2_round_trip(api_client_v2: TestClient):
    """Test PUT with the current config is a no-op (R1 round-trip).

    Uses a static config (rather than the default fixture's auto/DHCP config)
    since only static addresses/gateway are written back to the connection
    profile at all (matches v1's frozen `generate.py` behavior).
    """
    resp = await api_client_v2.get(f"/v2/network/interfaces/{TEST_INTERFACE_ETH_NAME}")
    result = await resp.json()
    config = result["data"]["config"]
    config["ipv4"] = {
        "method": "static",
        "addresses": ["192.168.2.148/24"],
        "gateway": "192.168.2.1",
        "route_metric": 100,
        "nameservers": ["192.168.2.2"],
    }

    resp = await api_client_v2.put(
        f"/v2/network/interfaces/{TEST_INTERFACE_ETH_NAME}/config", json=config
    )
    assert resp.status == 200, await resp.text()
    result = await resp.json()
    first_config = result["data"]["config"]
    assert first_config["ipv4"] == config["ipv4"]

    # PUT the exact same (now current) config again: must be a no-op round-trip
    resp = await api_client_v2.put(
        f"/v2/network/interfaces/{TEST_INTERFACE_ETH_NAME}/config", json=first_config
    )
    assert resp.status == 200, await resp.text()
    result = await resp.json()
    assert result["data"]["config"] == first_config


@pytest.mark.parametrize(
    ("ipv4_override", "message_snippet"),
    [
        ({}, "required key not provided"),
        (
            {"method": "static", "addresses": []},
            "at least one address is required when method is static",
        ),
        (
            {"method": "auto", "gateway": "192.168.2.1", "addresses": []},
            "gateway requires at least one address",
        ),
    ],
)
async def test_api_network_update_config_v2_invalid_ipv4(
    api_client_v2: TestClient, ipv4_override: dict, message_snippet: str
):
    """Test v2 config PUT rejects contradictory ipv4 config (R3)."""
    resp = await api_client_v2.get(f"/v2/network/interfaces/{TEST_INTERFACE_ETH_NAME}")
    result = await resp.json()
    config = result["data"]["config"]
    config["ipv4"] = ipv4_override

    resp = await api_client_v2.put(
        f"/v2/network/interfaces/{TEST_INTERFACE_ETH_NAME}/config", json=config
    )
    assert resp.status == 400
    result = await resp.json()
    assert message_snippet in result["message"]


async def test_api_network_update_config_v2_psk_without_wpa(
    api_client_v2: TestClient,
):
    """Test v2 config PUT rejects a psk without a matching auth method (R3)."""
    resp = await api_client_v2.get(f"/v2/network/interfaces/{TEST_INTERFACE_WLAN_NAME}")
    result = await resp.json()
    config = result["data"]["config"] or {
        "enabled": True,
        "ipv4": {"method": "auto"},
        "ipv6": {"method": "auto"},
        "mdns": "default",
        "llmnr": "default",
    }
    config["wifi"] = {
        "mode": "infrastructure",
        "ssid": "test",
        "auth": "open",
        "psk": "supersecret",
    }

    resp = await api_client_v2.put(
        f"/v2/network/interfaces/{TEST_INTERFACE_WLAN_NAME}/config", json=config
    )
    assert resp.status == 400
    result = await resp.json()
    assert "psk is only valid when auth is wpa-psk" in result["message"]


@pytest.mark.parametrize(
    ("interface_name", "wifi_override", "message_snippet"),
    [
        (TEST_INTERFACE_WLAN_NAME, None, "requires a wifi configuration"),
        (
            TEST_INTERFACE_ETH_NAME,
            {"mode": "infrastructure", "ssid": "test", "auth": "open"},
            "does not support a wifi configuration",
        ),
    ],
)
async def test_api_network_update_config_v2_wifi_type_mismatch(
    api_client_v2: TestClient,
    interface_name: str,
    wifi_override: dict | None,
    message_snippet: str,
):
    """Test v2 config PUT enforces wifi <-> interface type consistency.

    This is validated in the handler rather than `SCHEMA_CONFIG_V2` because
    the required shape of `wifi` (present vs. absent) depends on the target
    interface's type, which the schema alone cannot know.
    """
    resp = await api_client_v2.get(f"/v2/network/interfaces/{interface_name}")
    result = await resp.json()
    config = result["data"]["config"] or {
        "enabled": True,
        "ipv4": {"method": "auto"},
        "ipv6": {"method": "auto"},
        "mdns": "default",
        "llmnr": "default",
    }
    config["wifi"] = wifi_override

    resp = await api_client_v2.put(
        f"/v2/network/interfaces/{interface_name}/config", json=config
    )
    assert resp.status == 400
    result = await resp.json()
    assert message_snippet in result["message"]


async def test_api_network_update_config_v2_disable_non_destructive(
    api_client_v2: TestClient,
    device_eth0_service: DeviceService,
):
    """Test disabling via v2 config PUT does not delete the stored profile (R5)."""
    resp = await api_client_v2.get(f"/v2/network/interfaces/{TEST_INTERFACE_ETH_NAME}")
    result = await resp.json()
    config = result["data"]["config"]
    config["enabled"] = False

    resp = await api_client_v2.put(
        f"/v2/network/interfaces/{TEST_INTERFACE_ETH_NAME}/config", json=config
    )
    assert resp.status == 200
    result = await resp.json()
    assert result["data"]["config"]["enabled"] is False
    assert result["data"]["config"] is not None


async def test_api_network_update_config_v2_wifi(
    api_client_v2: TestClient,
    network_manager_service: NetworkManagerService,
):
    """Test a full wifi config update via v2 PUT (happy path).

    v2 equivalent of v1's `test_api_network_interface_update_wifi`: unlike v1's
    partial update, v2 always requires the full config (R3), so `mode` must be
    supplied explicitly. Asserts on the outgoing `AddAndActivateConnection`
    call rather than a follow-up GET, since the fixture's dbus mock doesn't
    simulate NetworkManager wiring the newly created connection back onto the
    device (unlike the real service).
    """
    network_manager_service.AddAndActivateConnection.calls.clear()

    resp = await api_client_v2.get(f"/v2/network/interfaces/{TEST_INTERFACE_WLAN_NAME}")
    result = await resp.json()
    config = result["data"]["config"] or {
        "enabled": True,
        "ipv4": {"method": "auto"},
        "ipv6": {"method": "auto"},
        "mdns": "default",
        "llmnr": "default",
    }
    config["enabled"] = True
    config["wifi"] = {
        "mode": "infrastructure",
        "ssid": "MY_TEST",
        "auth": "wpa-psk",
        "psk": "myWifiPassword",
    }

    resp = await api_client_v2.put(
        f"/v2/network/interfaces/{TEST_INTERFACE_WLAN_NAME}/config", json=config
    )
    assert resp.status == 200, await resp.text()

    assert len(network_manager_service.AddAndActivateConnection.calls) == 1
    settings = network_manager_service.AddAndActivateConnection.calls[0][0]
    assert settings["802-11-wireless"]["ssid"] == Variant("ay", b"MY_TEST")
    assert settings["802-11-wireless-security"]["psk"] == Variant("s", "myWifiPassword")


async def test_api_network_update_config_v2_mdns_llmnr(
    api_client_v2: TestClient,
    connection_settings_service: ConnectionSettingsService,
):
    """Test mdns/llmnr mode changes are applied via v2 PUT.

    v2 equivalent of v1's `test_api_network_interface_update_mdns`.
    """
    connection_settings_service.Update.calls.clear()

    resp = await api_client_v2.get(f"/v2/network/interfaces/{TEST_INTERFACE_ETH_NAME}")
    result = await resp.json()
    config = result["data"]["config"]
    config["mdns"] = "resolve"
    config["llmnr"] = "off"

    resp = await api_client_v2.put(
        f"/v2/network/interfaces/{TEST_INTERFACE_ETH_NAME}/config", json=config
    )
    assert resp.status == 200, await resp.text()
    result = await resp.json()
    assert result["data"]["config"]["mdns"] == "resolve"
    assert result["data"]["config"]["llmnr"] == "off"

    assert connection_settings_service.Update.calls
    settings = connection_settings_service.Update.calls[-1][0]
    assert settings["connection"]["mdns"] == Variant("i", 1)
    assert settings["connection"]["llmnr"] == Variant("i", 0)


async def test_api_network_accesspoints_v2(api_client_v2: TestClient):
    """Test the accesspoints endpoint is reused unchanged on v2.

    v2 equivalent of v1's `test_api_network_wireless_scan` - same handler
    (`APINetwork.scan_accesspoints`), mounted under the v2 collection-style
    `/network/interfaces/{name}/accesspoints` path instead of v1's
    `/network/interface/{name}/accesspoints`.
    """
    with patch("asyncio.sleep", return_value=AsyncMock()):
        resp = await api_client_v2.get(
            f"/v2/network/interfaces/{TEST_INTERFACE_WLAN_NAME}/accesspoints"
        )
    result = await resp.json()

    assert [ap["ssid"] for ap in result["data"]["accesspoints"]] == [
        "UPC4814466",
        "VQ@35(55720",
    ]
    assert [ap["signal"] for ap in result["data"]["accesspoints"]] == [47, 63]


@pytest.mark.parametrize(
    ("method", "url"),
    [
        ("get", "/v2/network/interfaces/bad"),
        ("put", "/v2/network/interfaces/bad/config"),
        ("get", "/v2/network/interfaces/bad/accesspoints"),
    ],
)
async def test_network_interface_not_found_v2(
    api_client_v2: TestClient, method: str, url: str
):
    """Test the not-found error for v2 endpoints, including the reused accesspoints route.

    v2 equivalent of v1's `test_network_interface_not_found` (excluding
    `update`/`vlan`, which have no v2 equivalent).
    """
    resp = await api_client_v2.request(method, url)
    assert resp.status == 404
    body = await resp.json()
    assert body["message"] == "Interface bad does not exist"
