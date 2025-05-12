"""Test check DNS Servers for IPv6 errors."""

from unittest.mock import AsyncMock, Mock, call, patch

from aiodns.error import DNSError
import pytest

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.checks.dns_server_ipv6 import CheckDNSServerIPv6
from supervisor.resolution.const import ContextType, IssueType


@pytest.fixture(name="dns_query")
async def fixture_dns_query() -> AsyncMock:
    """Mock aiodns query."""
    with patch(
        "supervisor.resolution.checks.dns_server_ipv6.DNSResolver.query",
        new_callable=AsyncMock,
    ) as dns_query:
        yield dns_query


async def test_base(coresys: CoreSys):
    """Test check basics."""
    dns_server_ipv6 = CheckDNSServerIPv6(coresys)
    assert dns_server_ipv6.slug == "dns_server_ipv6"
    assert dns_server_ipv6.enabled


async def test_check(coresys: CoreSys, dns_query: AsyncMock, capture_exception: Mock):
    """Test check for DNS server IPv6 errors."""
    dns_server_ipv6 = CheckDNSServerIPv6(coresys)
    await coresys.core.set_state(CoreState.RUNNING)

    coresys.plugins.dns.servers = ["dns://1.1.1.1"]
    assert dns_server_ipv6.dns_servers == [
        "dns://1.1.1.1",
        "dns://192.168.30.1",
    ]
    assert len(coresys.resolution.issues) == 0

    await dns_server_ipv6.run_check.__wrapped__(dns_server_ipv6)
    assert dns_query.call_args_list == [
        call("_checkdns.home-assistant.io", "AAAA"),
        call("_checkdns.home-assistant.io", "AAAA"),
    ]
    assert len(coresys.resolution.issues) == 0

    dns_query.reset_mock()
    coresys.plugins.dns.servers = []
    assert dns_server_ipv6.dns_servers == ["dns://192.168.30.1"]

    dns_query.side_effect = DNSError(1, "DNS server returned answer with no data")
    await dns_server_ipv6.run_check.__wrapped__(dns_server_ipv6)
    dns_query.assert_called_once_with("_checkdns.home-assistant.io", "AAAA")
    assert len(coresys.resolution.issues) == 0

    dns_query.reset_mock()
    dns_query.side_effect = (err := DNSError(4, "Domain name not found"))
    await dns_server_ipv6.run_check.__wrapped__(dns_server_ipv6)
    dns_query.assert_called_once_with("_checkdns.home-assistant.io", "AAAA")

    assert len(coresys.resolution.issues) == 1
    assert coresys.resolution.issues[0].type is IssueType.DNS_SERVER_IPV6_ERROR
    assert coresys.resolution.issues[0].context is ContextType.DNS_SERVER
    assert coresys.resolution.issues[0].reference == "dns://192.168.30.1"
    capture_exception.assert_called_once_with(err)


async def test_approve(coresys: CoreSys, supervisor_internet, dns_query: AsyncMock):
    """Test approve existing DNS Server IPv6 error issues."""
    dns_server_ipv6 = CheckDNSServerIPv6(coresys)
    await coresys.core.set_state(CoreState.RUNNING)

    assert dns_server_ipv6.dns_servers == ["dns://192.168.30.1"]
    dns_query.side_effect = DNSError(4, "Domain name not found")

    assert await dns_server_ipv6.approve_check(reference="dns://1.1.1.1") is False
    dns_query.assert_not_called()

    assert await dns_server_ipv6.approve_check(reference="dns://192.168.30.1") is True
    dns_query.assert_called_once_with("_checkdns.home-assistant.io", "AAAA")

    dns_query.reset_mock()
    dns_query.side_effect = DNSError(1, "DNS server returned answer with no data")
    assert await dns_server_ipv6.approve_check(reference="dns://192.168.30.1") is False
    dns_query.assert_called_once_with("_checkdns.home-assistant.io", "AAAA")

    dns_query.reset_mock()
    dns_query.side_effect = None
    assert await dns_server_ipv6.approve_check(reference="dns://192.168.30.1") is False
    dns_query.assert_called_once_with("_checkdns.home-assistant.io", "AAAA")


async def test_did_run(coresys: CoreSys):
    """Test that the check ran as expected."""
    dns_server_ipv6 = CheckDNSServerIPv6(coresys)
    should_run = dns_server_ipv6.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert should_run == [CoreState.RUNNING]
    assert len(should_not_run) != 0

    with patch.object(CheckDNSServerIPv6, "run_check", return_value=None) as check:
        for state in should_run:
            await coresys.core.set_state(state)
            await dns_server_ipv6()
            check.assert_called_once()
            check.reset_mock()

        for state in should_not_run:
            await coresys.core.set_state(state)
            await dns_server_ipv6()
            check.assert_not_called()
            check.reset_mock()


async def test_check_if_affected(coresys: CoreSys):
    """Test that check is still executed even if already affected."""
    dns_server_ipv6 = CheckDNSServerIPv6(coresys)
    await coresys.core.set_state(CoreState.RUNNING)

    coresys.resolution.create_issue(
        IssueType.DNS_SERVER_IPV6_ERROR,
        ContextType.DNS_SERVER,
        reference="dns://192.168.30.1",
    )
    assert len(coresys.resolution.issues) == 1

    with (
        patch.object(CheckDNSServerIPv6, "approve_check", return_value=True) as approve,
        patch.object(CheckDNSServerIPv6, "run_check", return_value=None) as check,
    ):
        await dns_server_ipv6()
        approve.assert_called_once()
        check.assert_called_once()
