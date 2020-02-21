"""Check ports."""
from ipaddress import ip_address

from supervisor.utils import check_port


def test_exists_open_port():
    """Test a exists network port."""
    assert check_port(ip_address("8.8.8.8"), 53)


def test_not_exists_port():
    """Test a not exists network service."""
    assert not check_port(ip_address("192.0.2.1"), 53)
