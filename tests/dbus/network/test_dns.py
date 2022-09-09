"""Test DNS Manager object."""
from ipaddress import IPv4Address

from supervisor.dbus.network import NetworkManager
from supervisor.dbus.network.configuration import DNSConfiguration


async def test_dns(network_manager: NetworkManager):
    """Test dns manager."""
    assert network_manager.dns.mode == "default"
    assert network_manager.dns.rc_manager == "file"
    assert network_manager.dns.configuration == [
        DNSConfiguration(
            [IPv4Address("192.168.30.1")], ["syshack.ch"], "eth0", 100, False
        )
    ]
