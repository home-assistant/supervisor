"""Test interface update payload."""
import pytest

from supervisor.dbus.payloads.interface_update import interface_update_payload
from supervisor.utils.gdbus import DBus


@pytest.mark.asyncio
async def test_interface_update_payload(network_interface):
    """Test interface update payload."""
    assert (
        interface_update_payload(network_interface, **{"method": "auto"})
        == """{
                    'connection':
                        {
                            'id': <'Wired connection 1'>,
                            'type': <'802-3-ethernet'>
                        },
                    'ipv4':
                        {
                            'method': <'auto'>
                        }
                }"""
    )

    assert (
        interface_update_payload(network_interface, **{})
        == """{
                    'connection':
                        {
                            'id': <'Wired connection 1'>,
                            'type': <'802-3-ethernet'>
                        },
                    'ipv4':
                        {
                            'method': <'manual'>,
                            'dns': <[uint32 16951488]>,
                            'address-data': <[
                                {
                                    'address': <'192.168.2.148'>,
                                    'prefix': <uint32 24>
                                }]>,
                            'gateway': <'192.168.2.1'>
                                }
                }"""
    )

    data = interface_update_payload(network_interface, **{"address": "1.1.1.1"})
    assert DBus.parse_gvariant(data)["ipv4"]["address-data"][0]["address"] == "1.1.1.1"
