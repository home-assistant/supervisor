"""Test check DNS Servers for IPv6 errors."""
from unittest.mock import AsyncMock, call, patch

from aiodns.error import DNSError
import pytest

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.checks.dns_server_ipv6_error import CheckDNSServerIPv6Errors
from supervisor.resolution.const import ContextType, IssueType


@pytest.fixture(name="dns_query")
async def fixture_dns_query() -> AsyncMock:
    """Mock aiodns query."""
    with patch(
        "supervisor.resolution.checks.dns_server_ipv6_error.DNSResolver.query",
        new_callable=AsyncMock,
    ) as dns_query:
        yield dns_query


async def test_base(coresys: CoreSys):
    """Test check basics."""
    dns_server_ipv6_errors = CheckDNSServerIPv6Errors(coresys)
    assert dns_server_ipv6_errors.slug == "dns_server_ipv6_error"
    assert dns_server_ipv6_errors.enabled


async def test_check(coresys: CoreSys, dns_query: AsyncMock):
    """Test check for DNS server IPv6 errors."""
    dns_server_ipv6_errors = CheckDNSServerIPv6Errors(coresys)
    coresys.core.state = CoreState.RUNNING

    coresys.plugins.dns.servers = ["dns://1.1.1.1"]
    assert dns_server_ipv6_errors.dns_servers == [
        "dns://1.1.1.1",
        "dns://192.168.30.1",
    ]
    assert len(coresys.resolution.issues) == 0

    await dns_server_ipv6_errors.run_check.__wrapped__(dns_server_ipv6_errors)
    assert dns_query.call_args_list == [
        call("_checkdns.home-assistant.io", "AAAA"),
        call("_checkdns.home-assistant.io", "AAAA"),
    ]
    assert len(coresys.resolution.issues) == 0

    dns_query.reset_mock()
    coresys.plugins.dns.servers = []
    assert dns_server_ipv6_errors.dns_servers == ["dns://192.168.30.1"]

    dns_query.side_effect = DNSError(1, "DNS server returned answer with no data")
    await dns_server_ipv6_errors.run_check.__wrapped__(dns_server_ipv6_errors)
    dns_query.assert_called_once_with("_checkdns.home-assistant.io", "AAAA")
    assert len(coresys.resolution.issues) == 0

    dns_query.reset_mock()
    dns_query.side_effect = DNSError(4, "Domain name not found")
    await dns_server_ipv6_errors.run_check.__wrapped__(dns_server_ipv6_errors)
    dns_query.assert_called_once_with("_checkdns.home-assistant.io", "AAAA")

    assert len(coresys.resolution.issues) == 1
    assert coresys.resolution.issues[0].type is IssueType.DNS_SERVER_IPV6_ERROR
    assert coresys.resolution.issues[0].context is ContextType.DNS_SERVER
    assert coresys.resolution.issues[0].reference == "dns://192.168.30.1"


async def test_approve(coresys: CoreSys, dns_query: AsyncMock):
    """Test approve existing DNS Server IPv6 error issues."""
    dns_server_ipv6_errors = CheckDNSServerIPv6Errors(coresys)
    coresys.core.state = CoreState.RUNNING

    assert dns_server_ipv6_errors.dns_servers == ["dns://192.168.30.1"]
    dns_query.side_effect = DNSError(4, "Domain name not found")

    assert (
        await dns_server_ipv6_errors.approve_check(reference="dns://1.1.1.1") is False
    )
    dns_query.assert_not_called()

    assert (
        await dns_server_ipv6_errors.approve_check(reference="dns://192.168.30.1")
        is True
    )
    dns_query.assert_called_once_with("_checkdns.home-assistant.io", "AAAA")

    dns_query.reset_mock()
    dns_query.side_effect = DNSError(1, "DNS server returned answer with no data")
    assert (
        await dns_server_ipv6_errors.approve_check(reference="dns://192.168.30.1")
        is False
    )
    dns_query.assert_called_once_with("_checkdns.home-assistant.io", "AAAA")

    dns_query.reset_mock()
    dns_query.side_effect = None
    assert (
        await dns_server_ipv6_errors.approve_check(reference="dns://192.168.30.1")
        is False
    )
    dns_query.assert_called_once_with("_checkdns.home-assistant.io", "AAAA")


async def test_did_run(coresys: CoreSys):
    """Test that the check ran as expected."""
    dns_server_ipv6_errors = CheckDNSServerIPv6Errors(coresys)
    should_run = dns_server_ipv6_errors.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert should_run == [CoreState.RUNNING]
    assert len(should_not_run) != 0

    with patch.object(
        CheckDNSServerIPv6Errors, "run_check", return_value=None
    ) as check:
        for state in should_run:
            coresys.core.state = state
            await dns_server_ipv6_errors()
            check.assert_called_once()
            check.reset_mock()

        for state in should_not_run:
            coresys.core.state = state
            await dns_server_ipv6_errors()
            check.assert_not_called()
            check.reset_mock()
