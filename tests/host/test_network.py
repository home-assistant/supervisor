"""Test network manager."""

import asyncio
from ipaddress import IPv4Address, IPv6Address
from unittest.mock import AsyncMock, patch

from dbus_fast import Variant
import pytest

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.dbus.const import InterfaceMethod
from supervisor.exceptions import HostNotSupportedError
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
from tests.dbus_service_mocks.network_device_wireless import (
    DeviceWireless as DeviceWirelessService,
)
from tests.dbus_service_mocks.network_manager import (
    NetworkManager as NetworkManagerService,
)


@pytest.fixture(name="active_connection_service")
async def fixture_active_connection_service(
    network_manager_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
) -> ActiveConnectionService:
    """Return mock active connection service."""
    yield network_manager_services["network_active_connection"]


@pytest.fixture(name="wireless_service")
async def fixture_wireless_service(
    network_manager_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
) -> DeviceWirelessService:
    """Return mock device wireless service."""
    yield network_manager_services["network_device_wireless"]


async def test_load(
    coresys: CoreSys,
    network_manager_service: NetworkManagerService,
    connection_settings_service: ConnectionSettingsService,
):
    """Test network manager load."""
    network_manager_service.ActivateConnection.calls.clear()
    network_manager_service.CheckConnectivity.calls.clear()

    await coresys.host.network.load()

    assert coresys.host.network.connectivity is True

    assert len(coresys.host.network.dns_servers) == 1
    assert str(coresys.host.network.dns_servers[0]) == "192.168.30.1"

    assert len(coresys.host.network.interfaces) == 2
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

    assert network_manager_service.ActivateConnection.calls == [
        (
            "/org/freedesktop/NetworkManager/Settings/1",
            "/org/freedesktop/NetworkManager/Devices/1",
            "/",
        )
    ]
    assert network_manager_service.CheckConnectivity.calls == []


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
    assert network_manager_service.ActivateConnection.calls == []


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

    assert network_manager_service.ActivateConnection.calls == []
    assert len(coresys.host.network.interfaces) == 2
    name_dict = {intr.name: intr for intr in coresys.host.network.interfaces}
    assert "eth0" in name_dict
    assert name_dict["eth0"].enabled is True
    assert name_dict["eth0"].ipv4setting.method == InterfaceMethod.AUTO
    assert name_dict["eth0"].ipv4.gateway is None
    assert name_dict["eth0"].ipv6setting.method == InterfaceMethod.AUTO
    assert name_dict["eth0"].ipv6.gateway == IPv6Address("fe80::da58:d7ff:fe00:9c69")


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
