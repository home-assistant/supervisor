"""Test interface update payload."""
from ipaddress import ip_address, ip_interface

import pytest

from supervisor.dbus.payloads.generate import interface_update_payload
from supervisor.host.const import AuthMethod, InterfaceMethod, InterfaceType, WifiMode
from supervisor.host.network import VlanConfig, WifiConfig
from supervisor.utils.gdbus import DBus

from tests.const import TEST_INTERFACE


@pytest.mark.asyncio
async def test_interface_update_payload_ethernet(coresys):
    """Test interface update payload."""
    interface = coresys.host.network.get(TEST_INTERFACE)

    data = interface_update_payload(interface)
    assert DBus.parse_gvariant(data)["ipv4"]["method"] == "auto"
    assert DBus.parse_gvariant(data)["ipv6"]["method"] == "auto"

    assert (
        DBus.parse_gvariant(data)["802-3-ethernet"]["assigned-mac-address"] == "stable"
    )


@pytest.mark.asyncio
async def test_interface_update_payload_ethernet_ipv4(coresys):
    """Test interface update payload."""
    interface = coresys.host.network.get(TEST_INTERFACE)
    inet = coresys.dbus.network.interfaces[TEST_INTERFACE]

    interface.ipv4.method = InterfaceMethod.STATIC
    interface.ipv4.address = [ip_interface("192.168.1.1/24")]
    interface.ipv4.nameservers = [ip_address("1.1.1.1"), ip_address("1.0.1.1")]
    interface.ipv4.gateway = ip_address("192.168.1.1")

    data = interface_update_payload(
        interface,
        name=inet.settings.connection.id,
        uuid=inet.settings.connection.uuid,
    )
    assert DBus.parse_gvariant(data)["ipv4"]["method"] == "manual"
    assert (
        DBus.parse_gvariant(data)["ipv4"]["address-data"][0]["address"] == "192.168.1.1"
    )
    assert DBus.parse_gvariant(data)["ipv4"]["address-data"][0]["prefix"] == 24
    assert DBus.parse_gvariant(data)["ipv4"]["dns"] == [16843009, 16777473]
    assert (
        DBus.parse_gvariant(data)["connection"]["uuid"] == inet.settings.connection.uuid
    )
    assert DBus.parse_gvariant(data)["connection"]["id"] == inet.settings.connection.id
    assert DBus.parse_gvariant(data)["connection"]["type"] == "802-3-ethernet"
    assert DBus.parse_gvariant(data)["connection"]["interface-name"] == interface.name
    assert DBus.parse_gvariant(data)["ipv4"]["gateway"] == "192.168.1.1"


@pytest.mark.asyncio
async def test_interface_update_payload_ethernet_ipv6(coresys):
    """Test interface update payload."""
    interface = coresys.host.network.get(TEST_INTERFACE)
    inet = coresys.dbus.network.interfaces[TEST_INTERFACE]

    interface.ipv6.method = InterfaceMethod.STATIC
    interface.ipv6.address = [ip_interface("2a03:169:3df5:0:6be9:2588:b26a:a679/64")]
    interface.ipv6.nameservers = [
        ip_address("2606:4700:4700::64"),
        ip_address("2606:4700:4700::6400"),
    ]
    interface.ipv6.gateway = ip_address("fe80::da58:d7ff:fe00:9c69")

    data = interface_update_payload(
        interface,
        name=inet.settings.connection.id,
        uuid=inet.settings.connection.uuid,
    )
    assert DBus.parse_gvariant(data)["ipv6"]["method"] == "manual"
    assert (
        DBus.parse_gvariant(data)["ipv6"]["address-data"][0]["address"]
        == "2a03:169:3df5:0:6be9:2588:b26a:a679"
    )
    assert DBus.parse_gvariant(data)["ipv6"]["address-data"][0]["prefix"] == 64
    assert DBus.parse_gvariant(data)["ipv6"]["dns"] == [
        50543257694033307102031451402929176676,
        50543257694033307102031451402929202176,
    ]
    assert (
        DBus.parse_gvariant(data)["connection"]["uuid"] == inet.settings.connection.uuid
    )
    assert DBus.parse_gvariant(data)["connection"]["id"] == inet.settings.connection.id
    assert DBus.parse_gvariant(data)["connection"]["type"] == "802-3-ethernet"
    assert DBus.parse_gvariant(data)["connection"]["interface-name"] == interface.name
    assert DBus.parse_gvariant(data)["ipv6"]["gateway"] == "fe80::da58:d7ff:fe00:9c69"


@pytest.mark.asyncio
async def test_interface_update_payload_wireless_wpa_psk(coresys):
    """Test interface update payload."""
    interface = coresys.host.network.get(TEST_INTERFACE)

    interface.type = InterfaceType.WIRELESS
    interface.wifi = WifiConfig(
        WifiMode.INFRASTRUCTURE, "Test", AuthMethod.WPA_PSK, "password", 0
    )

    data = interface_update_payload(interface)

    assert DBus.parse_gvariant(data)["connection"]["type"] == "802-11-wireless"
    assert DBus.parse_gvariant(data)["802-11-wireless"]["ssid"] == [84, 101, 115, 116]
    assert DBus.parse_gvariant(data)["802-11-wireless"]["mode"] == "infrastructure"

    assert DBus.parse_gvariant(data)["802-11-wireless-security"]["auth-alg"] == "open"
    assert (
        DBus.parse_gvariant(data)["802-11-wireless-security"]["key-mgmt"] == "wpa-psk"
    )
    assert DBus.parse_gvariant(data)["802-11-wireless-security"]["psk"] == "password"


@pytest.mark.asyncio
async def test_interface_update_payload_wireless_web(coresys):
    """Test interface update payload."""
    interface = coresys.host.network.get(TEST_INTERFACE)

    interface.type = InterfaceType.WIRELESS
    interface.wifi = WifiConfig(
        WifiMode.INFRASTRUCTURE, "Test", AuthMethod.WEP, "password", 0
    )

    data = interface_update_payload(interface)

    assert DBus.parse_gvariant(data)["connection"]["type"] == "802-11-wireless"
    assert DBus.parse_gvariant(data)["802-11-wireless"]["ssid"] == [84, 101, 115, 116]
    assert DBus.parse_gvariant(data)["802-11-wireless"]["mode"] == "infrastructure"

    assert DBus.parse_gvariant(data)["802-11-wireless-security"]["auth-alg"] == "none"
    assert DBus.parse_gvariant(data)["802-11-wireless-security"]["key-mgmt"] == "none"
    assert DBus.parse_gvariant(data)["802-11-wireless-security"]["psk"] == "password"


@pytest.mark.asyncio
async def test_interface_update_payload_wireless_open(coresys):
    """Test interface update payload."""
    interface = coresys.host.network.get(TEST_INTERFACE)

    interface.type = InterfaceType.WIRELESS
    interface.wifi = WifiConfig(
        WifiMode.INFRASTRUCTURE, "Test", AuthMethod.OPEN, None, 0
    )

    data = interface_update_payload(interface)

    assert DBus.parse_gvariant(data)["connection"]["type"] == "802-11-wireless"
    assert DBus.parse_gvariant(data)["802-11-wireless"]["ssid"] == [84, 101, 115, 116]
    assert DBus.parse_gvariant(data)["802-11-wireless"]["mode"] == "infrastructure"
    assert (
        DBus.parse_gvariant(data)["802-11-wireless"]["assigned-mac-address"] == "stable"
    )
    assert "802-11-wireless-security" not in DBus.parse_gvariant(data)


@pytest.mark.asyncio
async def test_interface_update_payload_vlan(coresys):
    """Test interface update payload."""
    interface = coresys.host.network.get(TEST_INTERFACE)

    interface.type = InterfaceType.VLAN
    interface.vlan = VlanConfig(10, interface.name)

    data = interface_update_payload(interface)
    assert DBus.parse_gvariant(data)["ipv4"]["method"] == "auto"
    assert DBus.parse_gvariant(data)["ipv6"]["method"] == "auto"

    assert DBus.parse_gvariant(data)["vlan"]["id"] == 10
    assert DBus.parse_gvariant(data)["vlan"]["parent"] == interface.name
    assert DBus.parse_gvariant(data)["connection"]["type"] == "vlan"
    assert "interface-name" not in DBus.parse_gvariant(data)["connection"]
