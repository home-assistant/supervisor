"""Test network utils."""
from supervisor.dbus.network.utils import int2ip, ip2int


def test_int2ip():
    """Test int2ip."""
    assert int2ip(16885952) == "192.168.1.1"


def test_ip2int():
    """Test ip2int."""
    assert ip2int("192.168.1.1") == 16885952
