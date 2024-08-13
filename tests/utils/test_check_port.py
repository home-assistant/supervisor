"""Check ports."""

from ipaddress import ip_address

from supervisor.coresys import CoreSys
from supervisor.utils import check_port


async def test_exists_open_port(coresys: CoreSys):
    """Test a exists network port."""
    assert await check_port(ip_address("8.8.8.8"), 53)


async def test_not_exists_port(coresys: CoreSys):
    """Test a not exists network service."""
    assert not await check_port(ip_address("192.0.2.1"), 53)
