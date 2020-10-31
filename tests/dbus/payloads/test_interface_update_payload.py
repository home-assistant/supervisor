"""Test interface update payload."""
import pytest

from supervisor.dbus.const import ConnectionType
from supervisor.dbus.payloads.generate import interface_update_payload
from supervisor.utils.gdbus import DBus


@pytest.mark.asyncio
async def test_interface_update_payload_ethernet(network_interface):
    """Test interface update payload."""
    data = interface_update_payload(network_interface, **{"method": "auto"})
    assert DBus.parse_gvariant(data)["ipv4"]["method"] == "auto"

    data = interface_update_payload(
        network_interface, **{"address": "1.1.1.1", "dns": ["1.1.1.1", "1.0.0.1"]}
    )
    assert DBus.parse_gvariant(data)["ipv4"]["method"] == "manual"
    assert DBus.parse_gvariant(data)["ipv4"]["address-data"][0]["address"] == "1.1.1.1"
    assert DBus.parse_gvariant(data)["ipv4"]["dns"] == [16843009, 16777217]
    assert (
        DBus.parse_gvariant(data)["connection"]["uuid"]
        == "0c23631e-2118-355c-bbb0-8943229cb0d6"
    )


@pytest.mark.asyncio
async def test_interface_update_payload_wireless(network_interface):
    """Test interface update payload."""
    network_interface.connection._properties["Type"] = ConnectionType.WIRELESS
    data = interface_update_payload(network_interface, **{"method": "auto"})
    assert DBus.parse_gvariant(data)["ipv4"]["method"] == "auto"

    data = interface_update_payload(
        network_interface, **{"address": "1.1.1.1", "dns": ["1.1.1.1", "1.0.0.1"]}
    )
    assert DBus.parse_gvariant(data)["ipv4"]["method"] == "manual"
    assert DBus.parse_gvariant(data)["ipv4"]["address-data"][0]["address"] == "1.1.1.1"
    assert DBus.parse_gvariant(data)["802-11-wireless"]["ssid"] == [78, 69, 84, 84]


@pytest.mark.asyncio
async def test_interface_update_disable_type_ethernet(network_interface):
    """Test disable interface IP version update payload."""
    network_interface.connection._properties["Type"] = ConnectionType.ETHERNET
    data = interface_update_payload(network_interface, **{"method": "disabled"})
    assert DBus.parse_gvariant(data)["ipv4"]["method"] == "disabled"

    data = interface_update_payload(
        network_interface, **{"method": "disabled", "ip_version": "ipv6"}
    )
    assert DBus.parse_gvariant(data)["ipv6"]["method"] == "disabled"


@pytest.mark.asyncio
async def test_interface_update_disable_type_wireless(network_interface):
    """Test disable interface IP version update payload."""
    network_interface.connection._properties["Type"] = ConnectionType.WIRELESS
    data = interface_update_payload(network_interface, **{"method": "disabled"})
    assert DBus.parse_gvariant(data)["ipv4"]["method"] == "disabled"
    assert "802-11-wireless" not in DBus.parse_gvariant(data)

    data = interface_update_payload(
        network_interface, **{"method": "disabled", "ip_version": "ipv6"}
    )
    assert DBus.parse_gvariant(data)["ipv6"]["method"] == "disabled"
    assert "802-11-wireless" not in DBus.parse_gvariant(data)
