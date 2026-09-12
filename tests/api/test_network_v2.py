"""Test network v2 API."""

import asyncio
from unittest.mock import AsyncMock, patch

from aiohttp.test_utils import TestClient
from dbus_fast import Variant
import pytest

from supervisor.const import DOCKER_IPV4_NETWORK_MASK, DOCKER_NETWORK
from supervisor.coresys import CoreSys
from supervisor.host.configuration import ResolvedInterface, WifiConfig
from supervisor.host.const import AuthMethod, WifiMode

from tests.const import TEST_INTERFACE_ETH_NAME, TEST_INTERFACE_WLAN_NAME
from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.network_active_connection import (
    ActiveConnection as ActiveConnectionService,
)
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


async def _wait_for_background_job(coresys: CoreSys, job_id: str) -> None:
    """Wait for a job scheduled by `apply_changes_v2` to finish.

    Creating a new connection profile always triggers a full activation
    cycle, which now runs as a background job (see `apply_changes_v2`)
    instead of blocking the request. Tests that don't care about the outcome
    still need to let it finish before the test ends, or the dbus session
    bus gets disconnected on teardown while it's mid-flight.
    """
    job = coresys.jobs.get_job(job_id)
    while not job.done:
        await asyncio.sleep(0)


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


async def test_api_network_interface_info_v2_unsupported_auth(
    api_client_v2: TestClient,
    coresys: CoreSys,
):
    """Test unsupported auth is reported, not hidden, in both state and config.

    Regression test for a bug caught in review: a stored profile whose auth
    method Supervisor doesn't understand (WPA3/sae, wpa-eap, owe, ...) used
    to make `interface.wifi` (and therefore both `state.wifi` and
    `config.wifi`) `null` entirely - hiding the observed signal/SSID of an
    active connection along with the (partially understood) config.
    """
    resolved = await coresys.host.network.get_with_config(TEST_INTERFACE_WLAN_NAME)
    resolved.interface.wifi = WifiConfig(
        mode=WifiMode.INFRASTRUCTURE,
        ssid="EnterpriseNetwork",
        auth=AuthMethod.UNSUPPORTED,
        psk=None,
        signal=80,
        active_ssid="EnterpriseNetwork",
    )
    existing = ResolvedInterface(
        resolved.interface, has_profile=True, enabled=resolved.enabled
    )

    with patch.object(
        coresys.host.network, "get_with_config", AsyncMock(return_value=existing)
    ):
        resp = await api_client_v2.get(
            f"/v2/network/interfaces/{TEST_INTERFACE_WLAN_NAME}"
        )
    result = await resp.json()

    assert result["data"]["state"]["wifi"] == {
        "ssid": "EnterpriseNetwork",
        "signal": 80,
    }
    config_wifi = result["data"]["config"]["wifi"]
    assert config_wifi["auth"] == "unsupported"
    assert config_wifi["ssid"] == "EnterpriseNetwork"
    assert config_wifi["psk_set"] is False


async def test_api_network_update_config_v2_unsupported_auth_wifi_null_round_trip(
    api_client_v2: TestClient,
    coresys: CoreSys,
):
    """Test PUTting `wifi: null` for an unsupported-auth profile round-trips (R1/R4).

    The only way through for a client that just wants to change unrelated
    settings (e.g. `mdns`) on such an interface: it can't echo back
    `config.wifi` verbatim (auth `unsupported` is refused on write, see
    `_validate_wifi_config_v2`), but explicitly omitting `wifi` must be
    accepted and must leave the existing (not understood) security section
    untouched rather than forcing a supported auth method to be supplied.
    """
    resolved = await coresys.host.network.get_with_config(TEST_INTERFACE_WLAN_NAME)
    resolved.interface.wifi = WifiConfig(
        mode=WifiMode.INFRASTRUCTURE,
        ssid="EnterpriseNetwork",
        auth=AuthMethod.UNSUPPORTED,
        psk=None,
        signal=None,
    )
    existing = ResolvedInterface(
        resolved.interface, has_profile=True, enabled=resolved.enabled
    )

    config = {
        "enabled": True,
        "ipv4": {"method": "auto"},
        "ipv6": {"method": "auto"},
        "mdns": "resolve",
        "llmnr": "default",
        "wifi": None,
    }

    with patch.object(
        coresys.host.network, "get_with_config", AsyncMock(return_value=existing)
    ):
        resp = await api_client_v2.put(
            f"/v2/network/interfaces/{TEST_INTERFACE_WLAN_NAME}/config", json=config
        )
    assert resp.status == 200, await resp.text()


async def test_api_network_update_config_v2_unsupported_auth_rejected(
    api_client_v2: TestClient,
):
    """Test `auth: unsupported` cannot be set explicitly via PUT.

    It's a read-only marker reported for a profile Supervisor doesn't fully
    understand, not something a client can (re)create.
    """
    config = {
        "enabled": True,
        "ipv4": {"method": "auto"},
        "ipv6": {"method": "auto"},
        "mdns": "default",
        "llmnr": "default",
        "wifi": {
            "mode": "infrastructure",
            "ssid": "test",
            "auth": "unsupported",
        },
    }

    resp = await api_client_v2.put(
        f"/v2/network/interfaces/{TEST_INTERFACE_WLAN_NAME}/config", json=config
    )
    assert resp.status == 400
    result = await resp.json()
    assert "unsupported is read-only and cannot be set" in result["message"]


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
    first_config = result["data"]["interface"]["config"]
    assert first_config["ipv4"] == config["ipv4"]

    # PUT the exact same (now current) config again: must be a no-op round-trip
    resp = await api_client_v2.put(
        f"/v2/network/interfaces/{TEST_INTERFACE_ETH_NAME}/config", json=first_config
    )
    assert resp.status == 200, await resp.text()
    result = await resp.json()
    assert result["data"]["interface"]["config"] == first_config


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
            "addresses and gateway are only supported when method is static",
        ),
        (
            {"method": "auto", "addresses": ["192.168.2.148/24"]},
            "addresses and gateway are only supported when method is static",
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


async def test_api_network_update_config_v2_empty_ssid(
    api_client_v2: TestClient,
):
    """Test v2 config PUT rejects an empty ssid.

    An empty ssid passes through to NetworkManager as if no ssid was set at
    all (the generator only sets the property for a truthy ssid), which is
    rejected at activation time with a confusing error rather than an
    immediate 400 - so reject it up front instead.
    """
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
        "ssid": "",
        "auth": "open",
    }

    resp = await api_client_v2.put(
        f"/v2/network/interfaces/{TEST_INTERFACE_WLAN_NAME}/config", json=config
    )
    assert resp.status == 400


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
    # The fixture's stored ipv4 config has leftover addresses/gateway despite
    # an `auto` method, which isn't itself under test here (and is now
    # rejected on PUT, see `test_api_network_update_config_v2_invalid_ipv4`).
    config["ipv4"] = {"method": "auto"}
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
    # The fixture's stored ipv4 config has leftover addresses/gateway despite
    # an `auto` method, which isn't itself under test here (and is now
    # rejected on PUT, see `test_api_network_update_config_v2_invalid_ipv4`).
    config["ipv4"] = {"method": "auto"}
    config["enabled"] = False

    resp = await api_client_v2.put(
        f"/v2/network/interfaces/{TEST_INTERFACE_ETH_NAME}/config", json=config
    )
    assert resp.status == 200
    result = await resp.json()
    assert result["data"]["interface"]["config"]["enabled"] is False
    assert result["data"]["interface"]["config"] is not None


async def test_api_network_update_config_v2_disable_without_profile(
    api_client_v2: TestClient,
):
    """Test disabling via v2 config PUT is rejected when there's no stored profile.

    Unlike a PUT that would create a new (enabled) profile, a disabled one
    can never be activated, so it wouldn't actually get persisted - silently
    accepting it would leave `config: null` unchanged, breaking the
    full-document replace contract (R5). This is an explicit exception to
    round-tripping for now, see #7110.
    """
    resp = await api_client_v2.get(f"/v2/network/interfaces/{TEST_INTERFACE_WLAN_NAME}")
    result = await resp.json()
    assert result["data"]["config"] is None

    config = {
        "enabled": False,
        "ipv4": {"method": "auto"},
        "ipv6": {"method": "auto"},
        "mdns": "default",
        "llmnr": "default",
        "wifi": {
            "mode": "infrastructure",
            "ssid": "test",
            "auth": "open",
        },
    }

    resp = await api_client_v2.put(
        f"/v2/network/interfaces/{TEST_INTERFACE_WLAN_NAME}/config", json=config
    )
    assert resp.status == 400


async def test_api_network_update_config_v2_wifi(
    api_client_v2: TestClient,
    network_manager_service: NetworkManagerService,
    coresys: CoreSys,
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

    # New connections always activate, which now runs as a background job
    # (see apply_changes_v2). Let it finish instead of leaving it dangling.
    result = await resp.json()
    await _wait_for_background_job(coresys, result["data"]["job_id"])


async def test_api_network_update_config_v2_wifi_open_auth_create(
    api_client_v2: TestClient,
    network_manager_service: NetworkManagerService,
    coresys: CoreSys,
):
    """Test creating a new open-auth wifi profile doesn't send a broken security section.

    Regression test for a bug caught in review: `get_connection_from_interface()`
    used to always emit an explicit-empty `802-11-wireless-security: {}` for
    open auth as a sentinel for `NetworkSetting.update()`'s merge logic to
    clear a stale section. That sentinel is meaningless to
    `AddAndActivateConnection`/`AddConnection` (there's no merge step - the
    settings hash is handed to NetworkManager as-is), and a present-but-empty
    `802-11-wireless-security` section there would make NetworkManager
    instantiate one with an unset `key-mgmt`, which fails connection verify.
    Creating a brand new open-auth profile (wlan0 has no stored profile by
    default, see `test_api_network_interface_info_v2_config_null`) must omit
    the section entirely instead.
    """
    network_manager_service.AddAndActivateConnection.calls.clear()

    config = {
        "enabled": True,
        "ipv4": {"method": "auto"},
        "ipv6": {"method": "auto"},
        "mdns": "default",
        "llmnr": "default",
        "wifi": {
            "mode": "infrastructure",
            "ssid": "MY_OPEN_TEST",
            "auth": "open",
        },
    }

    resp = await api_client_v2.put(
        f"/v2/network/interfaces/{TEST_INTERFACE_WLAN_NAME}/config", json=config
    )
    assert resp.status == 200, await resp.text()

    assert len(network_manager_service.AddAndActivateConnection.calls) == 1
    settings = network_manager_service.AddAndActivateConnection.calls[0][0]
    assert settings["802-11-wireless"]["ssid"] == Variant("ay", b"MY_OPEN_TEST")
    assert "security" not in settings["802-11-wireless"]
    assert "802-11-wireless-security" not in settings

    # New connections always activate, which now runs as a background job
    # (see apply_changes_v2). Let it finish instead of leaving it dangling.
    result = await resp.json()
    await _wait_for_background_job(coresys, result["data"]["job_id"])


async def test_api_network_update_config_v2_wifi_psk_required_for_new_profile(
    api_client_v2: TestClient,
):
    """Test v2 config PUT requires a psk when (re)creating a wpa-psk profile.

    Regression test for a bug caught in review: `auth: wpa-psk` with no `psk`
    used to pass schema validation outright for a brand new profile (wlan0
    has no stored profile by default, see
    `test_api_network_interface_info_v2_config_null`, so there's no existing
    secret to keep). `AddAndActivateConnection` accepts a `key-mgmt: wpa-psk`
    section with no secret (missing secrets are only checked at activation),
    so this would persist the profile and only fail asynchronously with
    `NO_SECRETS` - while a subsequent GET would still report `psk_set: true`
    (inferred purely from `auth`), leaving a client with no signal to ever
    re-prompt for the password.
    """
    resp = await api_client_v2.get(f"/v2/network/interfaces/{TEST_INTERFACE_WLAN_NAME}")
    result = await resp.json()
    assert result["data"]["config"] is None  # No existing profile/secret to keep

    config = {
        "enabled": True,
        "ipv4": {"method": "auto"},
        "ipv6": {"method": "auto"},
        "mdns": "default",
        "llmnr": "default",
        "wifi": {
            "mode": "infrastructure",
            "ssid": "MY_TEST",
            "auth": "wpa-psk",
        },
    }

    resp = await api_client_v2.put(
        f"/v2/network/interfaces/{TEST_INTERFACE_WLAN_NAME}/config", json=config
    )
    assert resp.status == 400
    result = await resp.json()
    assert result["error_key"] == "host_network_wifi_psk_required_error"
    assert "psk is required when auth is wpa-psk" in result["message"]


async def test_api_network_update_config_v2_wifi_psk_set_round_trip(
    api_client_v2: TestClient,
    coresys: CoreSys,
):
    """Test the read-only `psk_set` marker from GET can be echoed back on PUT (R1).

    GET never returns the actual `psk`, only whether one is set (`psk_set`).
    A client that fetches a config for an *existing* wpa-psk profile and PUTs
    it back unchanged must not be rejected just because it omits the actual
    secret (which it was never given) alongside the read-only `psk_set`
    marker. Uses a patched `get_with_config()` to simulate an existing
    wpa-psk profile, since the fixture's stored wlan0 settings normally have
    no `802-11-wireless-security` section at all (see
    `test_api_network_update_config_v2_wifi_psk_required_for_new_profile`).
    """
    resolved = await coresys.host.network.get_with_config(TEST_INTERFACE_WLAN_NAME)
    resolved.interface.wifi = WifiConfig(
        mode=WifiMode.INFRASTRUCTURE,
        ssid="MY_TEST",
        auth=AuthMethod.WPA_PSK,
        psk=None,
        signal=None,
    )
    existing = ResolvedInterface(
        resolved.interface, has_profile=True, enabled=resolved.enabled
    )

    config = {
        "enabled": True,
        "ipv4": {"method": "auto"},
        "ipv6": {"method": "auto"},
        "mdns": "default",
        "llmnr": "default",
    }
    # Simulates a client echoing back a GET response for an existing WPA
    # profile: `psk_set` is present (read-only marker) but the actual `psk`
    # is not, since GET never returns it.
    config["wifi"] = {
        "mode": "infrastructure",
        "ssid": "MY_TEST",
        "auth": "wpa-psk",
        "psk_set": True,
    }

    with patch.object(
        coresys.host.network, "get_with_config", AsyncMock(return_value=existing)
    ):
        resp = await api_client_v2.put(
            f"/v2/network/interfaces/{TEST_INTERFACE_WLAN_NAME}/config", json=config
        )
    assert resp.status == 200, await resp.text()

    # New connections always activate, which now runs as a background job
    # (see apply_changes_v2). Let it finish instead of leaving it dangling.
    result = await resp.json()
    await _wait_for_background_job(coresys, result["data"]["job_id"])


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
    # The fixture's stored ipv4 config has leftover addresses/gateway despite
    # an `auto` method, which isn't itself under test here (and is now
    # rejected on PUT, see `test_api_network_update_config_v2_invalid_ipv4`).
    config["ipv4"] = {"method": "auto"}
    config["mdns"] = "resolve"
    config["llmnr"] = "off"

    resp = await api_client_v2.put(
        f"/v2/network/interfaces/{TEST_INTERFACE_ETH_NAME}/config", json=config
    )
    assert resp.status == 200, await resp.text()
    result = await resp.json()
    assert result["data"]["interface"]["config"]["mdns"] == "resolve"
    assert result["data"]["interface"]["config"]["llmnr"] == "off"

    assert connection_settings_service.Update.calls
    settings = connection_settings_service.Update.calls[-1][0]
    assert settings["connection"]["mdns"] == Variant("i", 1)
    assert settings["connection"]["llmnr"] == Variant("i", 0)


async def test_api_network_update_config_v2_no_carrier_does_not_block(
    api_client_v2: TestClient,
    active_connection_service: ActiveConnectionService,
    coresys: CoreSys,
):
    """Test a PUT on an interface stuck activating (e.g. no carrier) doesn't block.

    Regression test for a bug caught in review: `apply_changes_v2()` used to
    always await the full activation cycle inline on the request. NetworkManager
    accepts an activation request for an interface without a carrier (e.g. an
    unplugged ethernet cable) and leaves it in ACTIVATING indefinitely, so that
    wait would block the request for `CONNECTION_ACTIVATION_TIMEOUT` (60s) and
    then raise `HostNetworkActivationTimeoutError`, which the API mapped to a
    400 blaming the *settings* - even though they had already been persisted
    successfully and a subsequent GET would show them applied.

    Activation now always runs as a background job for v2 (see
    `NetworkManager.apply_changes_v2`): the request returns as soon as
    settings are persisted, with a job ID the client can use to check on the
    outcome, instead of a stuck/failed activation surfacing as a misleading
    400 on the request that only changed unrelated settings.
    """
    # Simulate NetworkManager accepting an activation request but never
    # reaching a terminal state (no carrier, so it stays ACTIVATING forever
    # instead of reaching ACTIVATED or DEACTIVATED). Module-level shared
    # fixture, must be restored to avoid bleeding into other tests. Emit the
    # matching signal (and ping to let it be processed) so the already
    # cached client-side state is actually updated, not just the fixture the
    # mock reads from for future calls.
    original_state = active_connection_service.fixture.state
    active_connection_service.fixture.state = 1  # ACTIVATING
    active_connection_service.emit_properties_changed({"State": 1})
    await active_connection_service.ping()
    try:
        resp = await api_client_v2.get(
            f"/v2/network/interfaces/{TEST_INTERFACE_ETH_NAME}"
        )
        result = await resp.json()
        config = result["data"]["config"]
        config["ipv4"] = {"method": "auto"}
        config["mdns"] = "resolve"

        # Avoid actually waiting out the real (60s) timeout: only how quickly
        # the request itself returns is under test here, not the timeout
        # duration, which is already covered by
        # `test_apply_changes_activation_timeout`.
        with patch("supervisor.host.network.CONNECTION_ACTIVATION_TIMEOUT", 0.1):
            resp = await api_client_v2.put(
                f"/v2/network/interfaces/{TEST_INTERFACE_ETH_NAME}/config",
                json=config,
            )
            assert resp.status == 200, await resp.text()
            result = await resp.json()

            # Settings are visible immediately even though activation hasn't
            # (and in this scenario never will) complete.
            assert result["data"]["interface"]["config"]["mdns"] == "resolve"
            job_id = result["data"]["job_id"]

            # The background job eventually times out on its own; the PUT
            # above never waited on it.
            await _wait_for_background_job(coresys, job_id)
    finally:
        active_connection_service.fixture.state = original_state
        active_connection_service.emit_properties_changed({"State": original_state})
        await active_connection_service.ping()

    job = coresys.jobs.get_job(job_id)
    assert job.errors
    assert "Timed out waiting" in job.errors[-1].message


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
