"""Check ports."""
import asyncio
from ipaddress import ip_address

from supervisor.utils import async_check_port, check_port


def test_exists_open_port():
    """Test a exists network port."""
    assert check_port(ip_address("8.8.8.8"), 53)


def test_not_exists_port():
    """Test a not exists network service."""
    assert not check_port(ip_address("192.0.2.1"), 53)


async def test_async_exists_open_port():
    """Test a exists network port."""
    assert await async_check_port(asyncio.get_running_loop(), ip_address("8.8.8.8"), 53)


async def test_async_not_exists_port():
    """Test a not exists network service."""
    assert not await async_check_port(
        asyncio.get_running_loop(), ip_address("192.0.2.1"), 53
    )
