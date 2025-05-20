"""Test settings generation from interface."""

from unittest.mock import PropertyMock, patch

from supervisor.dbus.network import NetworkManager
from supervisor.dbus.network.interface import NetworkInterface
from supervisor.dbus.network.setting.generate import get_connection_from_interface
from supervisor.host.configuration import Ip6Setting, IpConfig, IpSetting, VlanConfig
from supervisor.host.const import InterfaceMethod, InterfaceType
from supervisor.host.network import Interface

from tests.const import TEST_INTERFACE_ETH_NAME


async def test_get_connection_from_interface(network_manager: NetworkManager):
    """Test network interface."""
    dbus_interface = network_manager.get(TEST_INTERFACE_ETH_NAME)
    interface = Interface.from_dbus_interface(dbus_interface)
    connection_payload = get_connection_from_interface(interface, network_manager)

    assert "connection" in connection_payload

    assert "interface-name" not in connection_payload["connection"]
    assert connection_payload["connection"]["type"].value == "802-3-ethernet"
    assert connection_payload["match"]["path"].value == ["platform-ff3f0000.ethernet"]

    assert connection_payload["ipv4"]["method"].value == "auto"
    assert "address-data" not in connection_payload["ipv4"]

    assert connection_payload["ipv6"]["method"].value == "auto"
    assert "address-data" not in connection_payload["ipv6"]


async def test_get_connection_no_path(network_manager: NetworkManager):
    """Test network interface without a path."""
    dbus_interface = network_manager.get(TEST_INTERFACE_ETH_NAME)
    with patch.object(NetworkInterface, "path", new=PropertyMock(return_value=None)):
        interface = Interface.from_dbus_interface(dbus_interface)

    connection_payload = get_connection_from_interface(interface, network_manager)

    assert "connection" in connection_payload
    assert "match" not in connection_payload

    assert connection_payload["connection"]["interface-name"].value == "eth0"


async def test_generate_from_vlan(network_manager: NetworkManager):
    """Test generate from a vlan interface."""
    vlan_interface = Interface(
        name="",
        mac="",
        path="",
        enabled=True,
        connected=True,
        primary=False,
        type=InterfaceType.VLAN,
        ipv4=IpConfig([], None, [], None),
        ipv4setting=IpSetting(InterfaceMethod.AUTO, [], None, []),
        ipv6=IpConfig([], None, [], None),
        ipv6setting=Ip6Setting(InterfaceMethod.AUTO, [], None, []),
        wifi=None,
        vlan=VlanConfig(1, "eth0"),
    )

    connection_payload = get_connection_from_interface(vlan_interface, network_manager)
    assert connection_payload["connection"]["id"].value == "Supervisor .1"
    assert connection_payload["connection"]["type"].value == "vlan"
    assert "uuid" in connection_payload["connection"]
    assert "match" not in connection_payload["connection"]
    assert "interface-name" not in connection_payload["connection"]
    assert connection_payload["ipv4"]["method"].value == "auto"
    assert connection_payload["ipv6"]["addr-gen-mode"].value == 1
    assert connection_payload["ipv6"]["ip6-privacy"].value == -1

    assert connection_payload["vlan"]["id"].value == 1
    assert (
        connection_payload["vlan"]["parent"].value
        == "0c23631e-2118-355c-bbb0-8943229cb0d6"
    )

    # Ensure value remains if parent interface is already a UUID
    vlan_interface.vlan.interface = "0c23631e-2118-355c-bbb0-8943229cb0d6"
    connection_payload = get_connection_from_interface(vlan_interface, network_manager)
    assert (
        connection_payload["vlan"]["parent"].value
        == "0c23631e-2118-355c-bbb0-8943229cb0d6"
    )
