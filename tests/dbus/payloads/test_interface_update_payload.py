"""Test interface update payload."""
import pytest

from supervisor.dbus.payloads.generate import interface_update_payload
from supervisor.utils.gdbus import DBus


@pytest.mark.asyncio
async def test_interface_update_payload(network_interface):
    """Test interface update payload."""
    data = interface_update_payload(network_interface, **{"method": "auto"})
    assert DBus.parse_gvariant(data)["ipv4"]["method"] == "auto"

    data = interface_update_payload(
        network_interface, **{"address": "1.1.1.1", "dns": ["1.1.1.1", "1.0.0.1"]}
    )
    assert DBus.parse_gvariant(data)["ipv4"]["method"] == "manual"
    assert DBus.parse_gvariant(data)["ipv4"]["address-data"][0]["address"] == "1.1.1.1"
    assert DBus.parse_gvariant(data)["ipv4"]["dns"] == [16843009, 16777217]
