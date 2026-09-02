"""Test network manager."""

import asyncio
from ipaddress import IPv4Address, IPv6Address
from unittest.mock import AsyncMock, patch

from dbus_fast import DBusError, Variant
import pytest

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.dbus.const import InterfaceMethod
from supervisor.dbus.network.setting import (
    CONF_ATTR_802_WIRELESS_SECURITY,
    CONF_ATTR_802_WIRELESS_SECURITY_PSK,
)
from supervisor.dbus.network.setting.generate import get_connection_from_interface
from supervisor.exceptions import HostNetworkError, HostNotSupportedError
from supervisor.homeassistant.const import WSEvent, WSType
from supervisor.host.const import WifiMode

from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.network_active_connection import (
    ActiveConnection as ActiveConnectionService,
)
from tests.dbus_service_mocks.network_connection_settings import (
    SETTINGS_1_FIXTURE,
    ConnectionSettings as ConnectionSettingsService,
)
from tests.dbus_service_mocks.network_device import Device as DeviceService
from tests.dbus_service_mocks.network_device_wireless import (
    DeviceWireless as DeviceWirelessService,
)
from tests.dbus_service_mocks.network_manager import (
    NetworkManager as NetworkManagerService,
)


@pytest.fixture(name="wireless_service")
async def fixture_wireless_service(
    network_manager_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
) -> DeviceWirelessService:
    """Return mock device wireless service."""
    return network_manager_services["network_device_wireless"]


@pytest.fixture(name="device_eth0_service")
async def fixture_device_eth0_service(
    network_manager_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
) -> DeviceService:
    """Return mock device eth0 service."""
    return network_manager_services["network_device"][
        "/org/freedesktop/NetworkManager/Devices/1"
    ]


@pytest.fixture(name="device_wlan0_service")
async def fixture_device_wlan0_service(
    network_manager_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
) -> DeviceService:
    """Return mock device wlan0 service."""
    return network_manager_services["network_device"][
        "/org/freedesktop/NetworkManager/Devices/3"
    ]


async def test_load(
    coresys: CoreSys,
    network_manager_service: NetworkManagerService,
    connection_settings_service: ConnectionSettingsService,
    device_eth0_service: DeviceService,
):
    """Test network manager load."""
    network_manager_service.ActivateConnection.calls.clear()
    network_manager_service.CheckConnectivity.calls.clear()
    device_eth0_service.Reapply.calls.clear()

    await coresys.host.network.load()

    assert coresys.host.network.connectivity is True

    assert len(coresys.host.network.dns_servers) == 1
    assert str(coresys.host.network.dns_servers[0]) == "192.168.30.1"

    assert len(coresys.host.network.interfaces) == 3
    name_dict = {intr.name: intr for intr in coresys.host.network.interfaces}
    assert "eth0" in name_dict
    assert name_dict["eth0"].mac == "AA:BB:CC:DD:EE:FF"
    assert name_dict["eth0"].enabled is True
    assert name_dict["eth0"].ipv4.gateway == IPv4Address("192.168.2.1")
    assert name_dict["eth0"].ipv4.ready is True
    assert name_dict["eth0"].ipv4setting.method == InterfaceMethod.AUTO
    assert name_dict["eth0"].ipv4setting.address == []
    assert name_dict["eth0"].ipv4setting.gateway is None
    assert name_dict["eth0"].ipv4setting.nameservers == [IPv4Address("192.168.2.1")]
    assert name_dict["eth0"].ipv6.gateway == IPv6Address("fe80::da58:d7ff:fe00:9c69")
    assert name_dict["eth0"].ipv6.ready is True
    assert name_dict["eth0"].ipv6setting.method == InterfaceMethod.AUTO
    assert name_dict["eth0"].ipv6setting.address == []
    assert name_dict["eth0"].ipv6setting.gateway is None
    assert name_dict["eth0"].ipv6setting.nameservers == [
        IPv6Address("2001:4860:4860::8888")
    ]
    assert "wlan0" in name_dict
    assert name_dict["wlan0"].enabled is False

    assert connection_settings_service.settings["ipv4"]["method"].value == "auto"
    assert connection_settings_service.settings["ipv4"]["address-data"] == Variant(
        "aa{sv}", []
    )
    assert "gateway" not in connection_settings_service.settings["ipv4"]
    assert connection_settings_service.settings["ipv4"]["dns"] == Variant(
        "au", [16951488]
    )
    assert connection_settings_service.settings["ipv6"]["method"].value == "auto"
    assert connection_settings_service.settings["ipv6"]["address-data"] == Variant(
        "aa{sv}", []
    )
    assert "gateway" not in connection_settings_service.settings["ipv6"]
    assert connection_settings_service.settings["ipv6"]["dns"] == Variant(
        "aay", [bytearray(b" \x01H`H`\x00\x00\x00\x00\x00\x00\x00\x00\x88\x88")]
    )
    assert "eth0.10" in name_dict
    assert name_dict["eth0.10"].enabled is True

    # The profiles changed (Supervisor defaults applied) with the connections
    # active, so the settings are reapplied in place without re-activation
    assert len(device_eth0_service.Reapply.calls) == 2
    assert (
        "/org/freedesktop/NetworkManager/Devices/1",
        {},
        0,
        0,
    ) in device_eth0_service.Reapply.calls
    assert (
        "/org/freedesktop/NetworkManager/Devices/38",
        {},
        0,
        0,
    ) in device_eth0_service.Reapply.calls
    assert network_manager_service.ActivateConnection.calls == []
    assert network_manager_service.CheckConnectivity.calls == []


async def test_load_unchanged_settings_skips_activation(
    coresys: CoreSys,
    network_manager_service: NetworkManagerService,
    device_eth0_service: DeviceService,
):
    """Test load does not touch connections when settings are unchanged."""
    # First load updates the profiles to Supervisor defaults and applies them
    await coresys.host.network.load()

    network_manager_service.ActivateConnection.calls.clear()
    device_eth0_service.Reapply.calls.clear()

    # Profiles now match what Supervisor generates, nothing to apply
    await coresys.host.network.load()
    assert network_manager_service.ActivateConnection.calls == []
    assert device_eth0_service.Reapply.calls == []


async def test_load_outdated_settings_reapplies(
    coresys: CoreSys,
    network_manager_service: NetworkManagerService,
    connection_settings_service: ConnectionSettingsService,
    device_eth0_service: DeviceService,
):
    """Test load applies an out of date profile in place."""
    await coresys.host.network.load()
    network_manager_service.ActivateConnection.calls.clear()
    device_eth0_service.Reapply.calls.clear()

    # Simulate a profile predating a change of Supervisor defaults
    connection_settings_service.settings["connection"]["id"] = Variant(
        "s", "Wired connection 1"
    )
    await coresys.dbus.network.get("eth0").settings.reload()

    await coresys.host.network.load()
    assert device_eth0_service.Reapply.calls == [
        ("/org/freedesktop/NetworkManager/Devices/1", {}, 0, 0)
    ]
    assert network_manager_service.ActivateConnection.calls == []


async def test_load_reapply_fails_activates(
    coresys: CoreSys,
    network_manager_service: NetworkManagerService,
    connection_settings_service: ConnectionSettingsService,
    device_eth0_service: DeviceService,
):
    """Test load re-activates when changed settings can't be reapplied in place."""
    await coresys.host.network.load()
    network_manager_service.ActivateConnection.calls.clear()

    # Simulate a profile predating a change of Supervisor defaults
    connection_settings_service.settings["connection"]["id"] = Variant(
        "s", "Wired connection 1"
    )
    await coresys.dbus.network.get("eth0").settings.reload()
    device_eth0_service.reapply_error = DBusError(
        "org.freedesktop.NetworkManager.Device.IncompatibleConnection",
        "Can't reapply any changes to '802-3-ethernet' setting",
    )

    await coresys.host.network.load()
    assert (
        "/org/freedesktop/NetworkManager/Settings/1",
        "/org/freedesktop/NetworkManager/Devices/1",
        "/",
    ) in network_manager_service.ActivateConnection.calls


async def test_apply_changes_reapplies_in_place(
    coresys: CoreSys,
    network_manager_service: NetworkManagerService,
    device_eth0_service: DeviceService,
):
    """Test user-initiated apply of changed settings reapplies in place."""
    await coresys.host.network.load()
    network_manager_service.ActivateConnection.calls.clear()
    device_eth0_service.Reapply.calls.clear()

    interface = coresys.host.network.get("eth0")
    interface.ipv4setting.nameservers = [IPv4Address("1.1.1.1")]
    await coresys.host.network.apply_changes(interface)

    assert device_eth0_service.Reapply.calls == [
        ("/org/freedesktop/NetworkManager/Devices/1", {}, 0, 0)
    ]
    assert network_manager_service.ActivateConnection.calls == []


async def test_apply_changes_unchanged_reactivates(
    coresys: CoreSys,
    network_manager_service: NetworkManagerService,
    device_eth0_service: DeviceService,
):
    """Test user-initiated apply of unchanged settings re-activates."""
    await coresys.host.network.load()
    network_manager_service.ActivateConnection.calls.clear()
    device_eth0_service.Reapply.calls.clear()

    await coresys.host.network.apply_changes(coresys.host.network.get("eth0"))

    assert device_eth0_service.Reapply.calls == []
    assert (
        "/org/freedesktop/NetworkManager/Settings/1",
        "/org/freedesktop/NetworkManager/Devices/1",
        "/",
    ) in network_manager_service.ActivateConnection.calls


async def test_apply_changes_with_psk_reactivates(
    coresys: CoreSys,
    network_manager_service: NetworkManagerService,
    device_eth0_service: DeviceService,
):
    """Test apply with a Wi-Fi PSK in the payload re-activates."""
    await coresys.host.network.load()
    network_manager_service.ActivateConnection.calls.clear()
    device_eth0_service.Reapply.calls.clear()

    interface = coresys.host.network.get("eth0")
    interface.ipv4setting.nameservers = [IPv4Address("1.1.1.1")]

    def add_psk(*args, **kwargs):
        conn = get_connection_from_interface(*args, **kwargs)
        conn[CONF_ATTR_802_WIRELESS_SECURITY] = {
            CONF_ATTR_802_WIRELESS_SECURITY_PSK: Variant("s", "supersecret")
        }
        return conn

    with patch("supervisor.host.network.get_connection_from_interface", new=add_psk):
        await coresys.host.network.apply_changes(interface)

    assert device_eth0_service.Reapply.calls == []
    assert (
        "/org/freedesktop/NetworkManager/Settings/1",
        "/org/freedesktop/NetworkManager/Devices/1",
        "/",
    ) in network_manager_service.ActivateConnection.calls


async def test_apply_changes_activation_timeout(
    coresys: CoreSys,
    network_manager_service: NetworkManagerService,
    active_connection_service: ActiveConnectionService,
):
    """Test apply_changes times out instead of hanging if activation never completes."""
    await coresys.host.network.load()
    network_manager_service.ActivateConnection.calls.clear()

    # Simulate NetworkManager getting stuck activating and never reaching a
    # terminal state (ACTIVATED/DEACTIVATED), which would otherwise hang
    # apply_changes indefinitely (see `_wait_for_activation`). The fixture is
    # module-level shared state, so it must be restored afterwards to avoid
    # bleeding into other tests.
    original_state = active_connection_service.fixture.state
    active_connection_service.fixture.state = 1  # ACTIVATING
    try:
        with (
            patch("supervisor.host.network.CONNECTION_ACTIVATION_TIMEOUT", 0.1),
            pytest.raises(HostNetworkError, match="Timed out waiting"),
        ):
            await coresys.host.network.apply_changes(coresys.host.network.get("eth0"))
    finally:
        active_connection_service.fixture.state = original_state

    assert (
        "/org/freedesktop/NetworkManager/Settings/1",
        "/org/freedesktop/NetworkManager/Devices/1",
        "/",
    ) in network_manager_service.ActivateConnection.calls


async def test_load_with_disabled_methods(
    coresys: CoreSys,
    network_manager_service: NetworkManagerService,
    connection_settings_service: ConnectionSettingsService,
):
    """Test load does not disable methods of interfaces."""
    network_manager_service.ActivateConnection.calls.clear()

    disabled = {"method": Variant("s", "disabled")}
    connection_settings_service.settings = SETTINGS_1_FIXTURE | {
        "ipv4": disabled,
        "ipv6": disabled,
    }
    await coresys.dbus.network.get("eth0").settings.reload()

    await coresys.host.network.load()
    assert (
        "/org/freedesktop/NetworkManager/Settings/1",
        "/org/freedesktop/NetworkManager/Devices/1",
        "/",
    ) not in network_manager_service.ActivateConnection.calls


async def test_load_with_network_connection_issues(
    coresys: CoreSys,
    network_manager_service: NetworkManagerService,
    active_connection_service: ActiveConnectionService,
):
    """Test load does not update interfaces with network connection issues."""
    network_manager_service.ActivateConnection.calls.clear()

    active_connection_service.emit_properties_changed(
        {"StateFlags": 0x10, "Ip4Config": "/"}
    )
    await active_connection_service.ping()

    await coresys.host.network.load()
    await coresys.host.network.update()

    assert (
        "/org/freedesktop/NetworkManager/Settings/1",
        "/org/freedesktop/NetworkManager/Devices/1",
        "/",
    ) not in network_manager_service.ActivateConnection.calls
    assert len(coresys.host.network.interfaces) == 3
    name_dict = {intr.name: intr for intr in coresys.host.network.interfaces}
    assert "eth0" in name_dict
    assert name_dict["eth0"].enabled is True
    assert name_dict["eth0"].ipv4setting.method == InterfaceMethod.AUTO
    assert name_dict["eth0"].ipv6setting.method == InterfaceMethod.AUTO


async def test_scan_wifi(coresys: CoreSys):
    """Test scanning wifi."""
    with pytest.raises(HostNotSupportedError):
        await coresys.host.network.scan_wifi(coresys.host.network.get("eth0"))

    with patch("supervisor.host.network.asyncio.sleep"):
        aps = await coresys.host.network.scan_wifi(coresys.host.network.get("wlan0"))

    assert len(aps) == 2
    assert aps[0].mac == "E4:57:40:A9:D7:DE"
    assert aps[0].mode == WifiMode.INFRASTRUCTURE
    assert aps[1].mac == "18:4B:0D:23:A1:9C"
    assert aps[1].mode == WifiMode.INFRASTRUCTURE


async def test_scan_wifi_with_failures(
    coresys: CoreSys, wireless_service: DeviceWirelessService, caplog
):
    """Test scanning wifi with accesspoint processing failures."""
    wireless_service.all_access_points = [
        "/org/freedesktop/NetworkManager/AccessPoint/43099",
        "/org/freedesktop/NetworkManager/AccessPoint/43100",
        "/org/freedesktop/NetworkManager/AccessPoint/99999",
    ]

    with patch("supervisor.host.network.asyncio.sleep"):
        aps = await coresys.host.network.scan_wifi(coresys.host.network.get("wlan0"))

    assert len(aps) == 2
    assert "Can't process an AP" in caplog.text


async def test_host_connectivity_changed(
    coresys: CoreSys,
    network_manager_service: NetworkManagerService,
    ha_ws_client: AsyncMock,
):
    """Test host connectivity changed."""
    await coresys.host.load()
    assert coresys.host.network.connectivity is True

    network_manager_service.emit_properties_changed({"Connectivity": 1})
    await network_manager_service.ping()
    assert coresys.host.network.connectivity is False
    await asyncio.sleep(0)
    assert {
        "type": WSType.SUPERVISOR_EVENT,
        "data": {
            "event": WSEvent.SUPERVISOR_UPDATE,
            "update_key": "network",
            "data": {"host_internet": False},
        },
    } in [call.args[0] for call in ha_ws_client.async_send_command.call_args_list]

    ha_ws_client.async_send_command.reset_mock()
    network_manager_service.emit_properties_changed({}, ["Connectivity"])
    await network_manager_service.ping()
    await network_manager_service.ping()
    assert coresys.host.network.connectivity is True
    await asyncio.sleep(0)
    assert {
        "type": WSType.SUPERVISOR_EVENT,
        "data": {
            "event": WSEvent.SUPERVISOR_UPDATE,
            "update_key": "network",
            "data": {"host_internet": True},
        },
    } in [call.args[0] for call in ha_ws_client.async_send_command.call_args_list]


async def test_host_connectivity_disabled(
    coresys: CoreSys,
    network_manager_service: NetworkManagerService,
    ha_ws_client: AsyncMock,
):
    """Test host connectivity check disabled."""
    await coresys.host.network.load()

    await coresys.core.set_state(CoreState.RUNNING)
    await asyncio.sleep(0)
    ha_ws_client.async_send_command.reset_mock()

    assert "connectivity_check" not in coresys.resolution.unsupported
    assert coresys.host.network.connectivity is True

    network_manager_service.emit_properties_changed({"ConnectivityCheckEnabled": False})
    await network_manager_service.ping()
    assert coresys.host.network.connectivity is None
    await asyncio.sleep(0)
    ha_ws_client.async_send_command.assert_any_call(
        {
            "type": WSType.SUPERVISOR_EVENT,
            "data": {
                "event": WSEvent.SUPERVISOR_UPDATE,
                "update_key": "network",
                "data": {"host_internet": None},
            },
        }
    )
    assert "connectivity_check" in coresys.resolution.unsupported

    ha_ws_client.async_send_command.reset_mock()
    network_manager_service.emit_properties_changed({"ConnectivityCheckEnabled": True})
    await network_manager_service.ping()
    await network_manager_service.ping()
    assert coresys.host.network.connectivity is True
    await asyncio.sleep(0)
    ha_ws_client.async_send_command.assert_any_call(
        {
            "type": WSType.SUPERVISOR_EVENT,
            "data": {
                "event": WSEvent.SUPERVISOR_UPDATE,
                "update_key": "network",
                "data": {"host_internet": True},
            },
        }
    )
    assert "connectivity_check" not in coresys.resolution.unsupported


async def test_get_with_config_down_interface_has_profile(
    coresys: CoreSys,
    device_eth0_service: DeviceService,
):
    """Test config stays visible for a down interface with a matching stored profile (R2)."""
    await coresys.host.network.load()

    device_eth0_service.emit_properties_changed({"ActiveConnection": "/"})
    await device_eth0_service.ping()
    assert coresys.host.network.get("eth0").connected is False

    resolved = await coresys.host.network.get_with_config("eth0")

    assert resolved.has_profile is True
    assert resolved.enabled is True
    assert resolved.interface.connected is False
    assert resolved.interface.ipv4setting is not None
    assert resolved.interface.ipv4setting.method == InterfaceMethod.AUTO


async def test_get_with_config_down_interface_no_profile(
    coresys: CoreSys,
):
    """Test config resolves to no profile for a down interface with no matching stored profile."""
    await coresys.host.network.load()

    # wlan0 is disconnected by default and has no matching stored connection
    assert coresys.host.network.get("wlan0").connected is False

    resolved = await coresys.host.network.get_with_config("wlan0")

    assert resolved.has_profile is False


async def test_interfaces_with_config(
    coresys: CoreSys,
    device_eth0_service: DeviceService,
):
    """Test interfaces_with_config resolves config for every interface."""
    await coresys.host.network.load()

    device_eth0_service.emit_properties_changed({"ActiveConnection": "/"})
    await device_eth0_service.ping()

    resolved_by_name = {
        resolved.interface.name: resolved
        for resolved in await coresys.host.network.interfaces_with_config()
    }

    assert resolved_by_name["eth0"].has_profile is True
    assert resolved_by_name["wlan0"].has_profile is False


async def test_apply_changes_v2_non_destructive_disable(
    coresys: CoreSys,
    network_manager_service: NetworkManagerService,
    connection_settings_service: ConnectionSettingsService,
    device_eth0_service: DeviceService,
):
    """Test v2 disable deactivates and clears autoconnect instead of deleting the profile (R5)."""
    await coresys.host.network.load()
    network_manager_service.DeactivateConnection.calls.clear()
    connection_settings_service.Delete.calls.clear()
    connection_settings_service.Update.calls.clear()

    interface = coresys.host.network.get("eth0")
    interface.enabled = False

    await coresys.host.network.apply_changes_v2(interface)

    assert connection_settings_service.Delete.calls == []
    assert network_manager_service.DeactivateConnection.calls == [
        ("/org/freedesktop/NetworkManager/ActiveConnection/1",)
    ]
    assert connection_settings_service.Update.calls
    updated_settings = connection_settings_service.Update.calls[-1][0]
    assert updated_settings["connection"]["autoconnect"] == Variant("b", False)


async def test_apply_changes_v2_reenable_reuses_profile(
    coresys: CoreSys,
    network_manager_service: NetworkManagerService,
    connection_settings_service: ConnectionSettingsService,
    device_eth0_service: DeviceService,
):
    """Test re-enabling after a non-destructive disable reuses the profile (R2+R5)."""
    await coresys.host.network.load()

    # Disable non-destructively
    interface = coresys.host.network.get("eth0")
    interface.enabled = False
    await coresys.host.network.apply_changes_v2(interface)

    # Simulate NetworkManager deactivating the device as a result
    device_eth0_service.emit_properties_changed({"ActiveConnection": "/"})
    await device_eth0_service.ping()

    resolved = await coresys.host.network.get_with_config("eth0")
    assert resolved.has_profile is True
    assert resolved.enabled is False

    network_manager_service.AddAndActivateConnection.calls.clear()
    network_manager_service.ActivateConnection.calls.clear()

    resolved.interface.enabled = True
    await coresys.host.network.apply_changes_v2(resolved.interface)

    # No new connection profile is created, the existing one is reused/reactivated
    assert network_manager_service.AddAndActivateConnection.calls == []
    assert (
        "/org/freedesktop/NetworkManager/Settings/1",
        "/org/freedesktop/NetworkManager/Devices/1",
        "/",
    ) in network_manager_service.ActivateConnection.calls
