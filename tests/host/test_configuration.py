"""Test host configuration interface."""

from unittest.mock import Mock

from dbus_fast import Variant
import pytest

from supervisor.coresys import CoreSys
from supervisor.dbus.const import DeviceType
from supervisor.host.configuration import Interface, VlanConfig, WifiConfig
from supervisor.host.const import AuthMethod, InterfaceType, WifiMode

from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.network_connection_settings import (
    ConnectionSettings as ConnectionSettingsService,
)
from tests.dbus_service_mocks.network_device import Device as DeviceService


async def test_equals_dbus_interface_no_settings(coresys: CoreSys):
    """Test returns False when NetworkInterface has no settings."""
    await coresys.host.network.load()

    # Create test interface
    test_interface = Interface(
        name="eth0",
        enabled=True,
        connected=True,
        primary=False,
        type=InterfaceType.ETHERNET,
        ipv4=None,
        ipv4setting=None,
        ipv6=None,
        ipv6setting=None,
        wifi=None,
        vlan=None,
        path="platform-ff3f0000.ethernet",
        mac="AA:BB:CC:DD:EE:FF",
        mdns=None,
        llmnr=None,
    )

    # Get network interface and remove its connection to simulate no settings
    network_interface = coresys.dbus.network.get("eth0")
    network_interface._connection = None

    assert test_interface.equals_dbus_interface(network_interface) is False


async def test_equals_dbus_interface_connection_name_match(coresys: CoreSys):
    """Test interface comparison returns True when connection interface name matches."""
    await coresys.host.network.load()

    # Create test interface
    test_interface = Interface(
        name="eth0",
        enabled=True,
        connected=True,
        primary=False,
        type=InterfaceType.ETHERNET,
        ipv4=None,
        ipv4setting=None,
        ipv6=None,
        ipv6setting=None,
        wifi=None,
        vlan=None,
        path="platform-ff3f0000.ethernet",
        mac="AA:BB:CC:DD:EE:FF",
        mdns=None,
        llmnr=None,
    )

    # Get the network interface - this should have connection settings with interface-name = "eth0"
    network_interface = coresys.dbus.network.get("eth0")

    assert test_interface.equals_dbus_interface(network_interface) is True


def test_equals_dbus_interface_connection_name_no_match():
    """Test interface comparison returns False when connection interface name differs."""

    # Create test interface
    test_interface = Interface(
        name="eth0",
        enabled=True,
        connected=True,
        primary=False,
        type=InterfaceType.ETHERNET,
        ipv4=None,
        ipv4setting=None,
        ipv6=None,
        ipv6setting=None,
        wifi=None,
        vlan=None,
        path="platform-ff3f0000.ethernet",
        mac="AA:BB:CC:DD:EE:FF",
        mdns=None,
        llmnr=None,
    )

    # Mock network interface with different connection name
    mock_network_interface = Mock()
    mock_network_interface.type = DeviceType.ETHERNET
    mock_network_interface.settings = Mock()
    mock_network_interface.settings.match = None
    mock_network_interface.settings.connection = Mock()
    mock_network_interface.settings.connection.interface_name = "eth1"  # Different name

    assert test_interface.equals_dbus_interface(mock_network_interface) is False


async def test_equals_dbus_interface_path_match(
    coresys: CoreSys,
    connection_settings_service: ConnectionSettingsService,
):
    """Test interface comparison returns True when path matches."""
    await coresys.host.network.load()

    # Create test interface
    test_interface = Interface(
        name="eth0",
        enabled=True,
        connected=True,
        primary=False,
        type=InterfaceType.ETHERNET,
        ipv4=None,
        ipv4setting=None,
        ipv6=None,
        ipv6setting=None,
        wifi=None,
        vlan=None,
        path="platform-ff3f0000.ethernet",
        mac="AA:BB:CC:DD:EE:FF",
        mdns=None,
        llmnr=None,
    )

    # Add match settings with path and remove interface name to force path matching
    connection_settings_service.settings["match"] = {
        "path": Variant("as", ["platform-ff3f0000.ethernet"])
    }
    connection_settings_service.settings["connection"].pop("interface-name", None)

    network_interface = coresys.dbus.network.get("eth0")

    assert test_interface.equals_dbus_interface(network_interface) is True


def test_equals_dbus_interface_vlan_type_mismatch():
    """Test VLAN interface returns False when NetworkInterface type doesn't match."""

    # Create VLAN test interface
    test_vlan_interface = Interface(
        name="eth0.10",
        enabled=True,
        connected=True,
        primary=False,
        type=InterfaceType.VLAN,
        ipv4=None,
        ipv4setting=None,
        ipv6=None,
        ipv6setting=None,
        wifi=None,
        vlan=VlanConfig(id=10, interface="0c23631e-2118-355c-bbb0-8943229cb0d6"),
        path="",
        mac="52:54:00:2B:36:80",
        mdns=None,
        llmnr=None,
    )

    # Mock non-VLAN NetworkInterface - should return False immediately
    mock_network_interface = Mock()
    mock_network_interface.type = DeviceType.ETHERNET  # Not VLAN type
    mock_network_interface.settings = Mock()

    # Should return False immediately since types don't match
    assert test_vlan_interface.equals_dbus_interface(mock_network_interface) is False


def test_equals_dbus_interface_vlan_missing_info():
    """Test VLAN interface raises RuntimeError when VLAN info is missing."""

    # Create VLAN test interface without VLAN config
    test_vlan_interface = Interface(
        name="eth0.10",
        enabled=True,
        connected=True,
        primary=False,
        type=InterfaceType.VLAN,
        ipv4=None,
        ipv4setting=None,
        ipv6=None,
        ipv6setting=None,
        wifi=None,
        vlan=None,  # Missing VLAN config!
        path="",
        mac="52:54:00:2B:36:80",
        mdns=None,
        llmnr=None,
    )

    # Mock VLAN NetworkInterface
    mock_network_interface = Mock()
    mock_network_interface.type = DeviceType.VLAN
    mock_network_interface.settings = Mock()

    # Should raise RuntimeError
    try:
        test_vlan_interface.equals_dbus_interface(mock_network_interface)
        assert False, "Expected RuntimeError"
    except RuntimeError as e:
        assert str(e) == "VLAN information missing"


def test_equals_dbus_interface_vlan_no_vlan_settings():
    """Test VLAN interface returns False when NetworkInterface has no VLAN settings."""

    # Create VLAN test interface
    test_vlan_interface = Interface(
        name="eth0.10",
        enabled=True,
        connected=True,
        primary=False,
        type=InterfaceType.VLAN,
        ipv4=None,
        ipv4setting=None,
        ipv6=None,
        ipv6setting=None,
        wifi=None,
        vlan=VlanConfig(id=10, interface="0c23631e-2118-355c-bbb0-8943229cb0d6"),
        path="",
        mac="52:54:00:2B:36:80",
        mdns=None,
        llmnr=None,
    )

    # Mock VLAN NetworkInterface without VLAN settings
    mock_network_interface = Mock()
    mock_network_interface.type = DeviceType.VLAN
    mock_network_interface.settings = Mock()
    mock_network_interface.settings.vlan = None  # No VLAN settings

    assert test_vlan_interface.equals_dbus_interface(mock_network_interface) is False


@pytest.fixture(name="device_eth0_10_service")
async def fixture_device_eth0_10_service(
    network_manager_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
) -> DeviceService:
    """Mock Device eth0.10 service."""
    yield network_manager_services["network_device"][
        "/org/freedesktop/NetworkManager/Devices/38"
    ]


async def test_equals_dbus_interface_eth0_10_real(
    coresys: CoreSys, device_eth0_10_service: DeviceService
):
    """Test eth0.10 interface with real D-Bus interface."""
    await coresys.host.network.load()

    # Get the eth0.10 interface
    network_interface = coresys.dbus.network.get("eth0.10")

    # Check if it has the expected VLAN type
    assert network_interface.type == DeviceType.VLAN
    assert network_interface.settings is not None
    assert network_interface.settings.vlan is not None

    # Create matching test interface with correct parent UUID
    test_vlan_interface = Interface(
        name="eth0.10",
        enabled=True,
        connected=True,
        primary=False,
        type=InterfaceType.VLAN,
        ipv4=None,
        ipv4setting=None,
        ipv6=None,
        ipv6setting=None,
        wifi=None,
        vlan=VlanConfig(
            id=network_interface.settings.vlan.id,
            interface=network_interface.settings.vlan.parent,
        ),
        path="",
        mac="52:54:00:2B:36:80",
        mdns=None,
        llmnr=None,
    )

    # Test should pass with matching VLAN config
    assert test_vlan_interface.equals_dbus_interface(network_interface) is True


def test_map_nm_wifi_non_wireless_interface():
    """Test _map_nm_wifi returns None for non-wireless interface."""
    # Mock non-wireless interface
    mock_interface = Mock()
    mock_interface.type = DeviceType.ETHERNET
    mock_interface.settings = Mock()

    result = Interface._map_nm_wifi(mock_interface)
    assert result is None


def test_map_nm_wifi_no_settings():
    """Test _map_nm_wifi returns None when interface has no settings."""
    # Mock wireless interface without settings
    mock_interface = Mock()
    mock_interface.type = DeviceType.WIRELESS
    mock_interface.settings = None

    result = Interface._map_nm_wifi(mock_interface)
    assert result is None


def test_map_nm_wifi_open_authentication():
    """Test _map_nm_wifi with open authentication (no security)."""
    # Mock wireless interface with open authentication
    mock_interface = Mock()
    mock_interface.type = DeviceType.WIRELESS
    mock_interface.settings = Mock()
    mock_interface.settings.wireless_security = None
    mock_interface.settings.wireless = Mock()
    mock_interface.settings.wireless.ssid = "TestSSID"
    mock_interface.settings.wireless.mode = "infrastructure"
    mock_interface.wireless = None
    mock_interface.interface_name = "wlan0"

    result = Interface._map_nm_wifi(mock_interface)

    assert result is not None
    assert isinstance(result, WifiConfig)
    assert result.mode == WifiMode.INFRASTRUCTURE
    assert result.ssid == "TestSSID"
    assert result.auth == AuthMethod.OPEN
    assert result.psk is None
    assert result.signal is None


def test_map_nm_wifi_wep_authentication():
    """Test _map_nm_wifi with WEP authentication."""
    # Mock wireless interface with WEP authentication
    mock_interface = Mock()
    mock_interface.type = DeviceType.WIRELESS
    mock_interface.settings = Mock()
    mock_interface.settings.wireless_security = Mock()
    mock_interface.settings.wireless_security.key_mgmt = "none"
    mock_interface.settings.wireless_security.psk = None
    mock_interface.settings.wireless = Mock()
    mock_interface.settings.wireless.ssid = "WEPNetwork"
    mock_interface.settings.wireless.mode = "infrastructure"
    mock_interface.wireless = None
    mock_interface.interface_name = "wlan0"

    result = Interface._map_nm_wifi(mock_interface)

    assert result is not None
    assert isinstance(result, WifiConfig)
    assert result.auth == AuthMethod.WEP
    assert result.ssid == "WEPNetwork"
    assert result.psk is None


def test_map_nm_wifi_wpa_psk_authentication():
    """Test _map_nm_wifi with WPA-PSK authentication."""
    # Mock wireless interface with WPA-PSK authentication
    mock_interface = Mock()
    mock_interface.type = DeviceType.WIRELESS
    mock_interface.settings = Mock()
    mock_interface.settings.wireless_security = Mock()
    mock_interface.settings.wireless_security.key_mgmt = "wpa-psk"
    mock_interface.settings.wireless_security.psk = "SecretPassword123"
    mock_interface.settings.wireless = Mock()
    mock_interface.settings.wireless.ssid = "SecureNetwork"
    mock_interface.settings.wireless.mode = "infrastructure"
    mock_interface.wireless = None
    mock_interface.interface_name = "wlan0"

    result = Interface._map_nm_wifi(mock_interface)

    assert result is not None
    assert isinstance(result, WifiConfig)
    assert result.auth == AuthMethod.WPA_PSK
    assert result.ssid == "SecureNetwork"
    assert result.psk == "SecretPassword123"


def test_map_nm_wifi_unsupported_authentication():
    """Test _map_nm_wifi returns None for unsupported authentication method."""
    # Mock wireless interface with unsupported authentication
    mock_interface = Mock()
    mock_interface.type = DeviceType.WIRELESS
    mock_interface.settings = Mock()
    mock_interface.settings.wireless_security = Mock()
    mock_interface.settings.wireless_security.key_mgmt = "wpa-eap"  # Unsupported
    mock_interface.settings.wireless = Mock()
    mock_interface.settings.wireless.ssid = "EnterpriseNetwork"
    mock_interface.interface_name = "wlan0"

    result = Interface._map_nm_wifi(mock_interface)

    assert result is None


def test_map_nm_wifi_different_modes():
    """Test _map_nm_wifi with different wifi modes."""
    modes_to_test = [
        ("infrastructure", WifiMode.INFRASTRUCTURE),
        ("mesh", WifiMode.MESH),
        ("adhoc", WifiMode.ADHOC),
        ("ap", WifiMode.AP),
    ]

    for mode_value, expected_mode in modes_to_test:
        mock_interface = Mock()
        mock_interface.type = DeviceType.WIRELESS
        mock_interface.settings = Mock()
        mock_interface.settings.wireless_security = None
        mock_interface.settings.wireless = Mock()
        mock_interface.settings.wireless.ssid = "TestSSID"
        mock_interface.settings.wireless.mode = mode_value
        mock_interface.wireless = None
        mock_interface.interface_name = "wlan0"

        result = Interface._map_nm_wifi(mock_interface)

        assert result is not None
        assert result.mode == expected_mode


def test_map_nm_wifi_with_signal():
    """Test _map_nm_wifi with wireless signal strength."""
    # Mock wireless interface with active connection and signal
    mock_interface = Mock()
    mock_interface.type = DeviceType.WIRELESS
    mock_interface.settings = Mock()
    mock_interface.settings.wireless_security = None
    mock_interface.settings.wireless = Mock()
    mock_interface.settings.wireless.ssid = "TestSSID"
    mock_interface.settings.wireless.mode = "infrastructure"
    mock_interface.wireless = Mock()
    mock_interface.wireless.active = Mock()
    mock_interface.wireless.active.strength = 75
    mock_interface.interface_name = "wlan0"

    result = Interface._map_nm_wifi(mock_interface)

    assert result is not None
    assert result.signal == 75


def test_map_nm_wifi_without_signal():
    """Test _map_nm_wifi without wireless signal (no active connection)."""
    # Mock wireless interface without active connection
    mock_interface = Mock()
    mock_interface.type = DeviceType.WIRELESS
    mock_interface.settings = Mock()
    mock_interface.settings.wireless_security = None
    mock_interface.settings.wireless = Mock()
    mock_interface.settings.wireless.ssid = "TestSSID"
    mock_interface.settings.wireless.mode = "infrastructure"
    mock_interface.wireless = None
    mock_interface.interface_name = "wlan0"

    result = Interface._map_nm_wifi(mock_interface)

    assert result is not None
    assert result.signal is None


def test_map_nm_wifi_wireless_no_active_ap():
    """Test _map_nm_wifi with wireless object but no active access point."""
    # Mock wireless interface with wireless object but no active AP
    mock_interface = Mock()
    mock_interface.type = DeviceType.WIRELESS
    mock_interface.settings = Mock()
    mock_interface.settings.wireless_security = None
    mock_interface.settings.wireless = Mock()
    mock_interface.settings.wireless.ssid = "TestSSID"
    mock_interface.settings.wireless.mode = "infrastructure"
    mock_interface.wireless = Mock()
    mock_interface.wireless.active = None
    mock_interface.interface_name = "wlan0"

    result = Interface._map_nm_wifi(mock_interface)

    assert result is not None
    assert result.signal is None


def test_map_nm_wifi_no_wireless_settings():
    """Test _map_nm_wifi when wireless settings are missing."""
    # Mock wireless interface without wireless settings
    mock_interface = Mock()
    mock_interface.type = DeviceType.WIRELESS
    mock_interface.settings = Mock()
    mock_interface.settings.wireless_security = None
    mock_interface.settings.wireless = None
    mock_interface.wireless = None
    mock_interface.interface_name = "wlan0"

    result = Interface._map_nm_wifi(mock_interface)

    assert result is not None
    assert result.ssid == ""
    assert result.mode == WifiMode.INFRASTRUCTURE  # Default mode


def test_map_nm_wifi_no_wireless_mode():
    """Test _map_nm_wifi when wireless mode is not specified."""
    # Mock wireless interface without mode specified
    mock_interface = Mock()
    mock_interface.type = DeviceType.WIRELESS
    mock_interface.settings = Mock()
    mock_interface.settings.wireless_security = None
    mock_interface.settings.wireless = Mock()
    mock_interface.settings.wireless.ssid = "TestSSID"
    mock_interface.settings.wireless.mode = None
    mock_interface.wireless = None
    mock_interface.interface_name = "wlan0"

    result = Interface._map_nm_wifi(mock_interface)

    assert result is not None
    assert result.mode == WifiMode.INFRASTRUCTURE  # Default mode
