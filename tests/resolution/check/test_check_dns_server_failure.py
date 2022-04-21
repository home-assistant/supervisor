"""Test check DNS Servers for failures."""
from unittest.mock import AsyncMock, call, patch

from aiodns.error import DNSError
import pytest

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.checks.dns_server_failure import CheckDNSServerFailures
from supervisor.resolution.const import ContextType, IssueType


@pytest.fixture(name="dns_query")
async def fixture_dns_query() -> AsyncMock:
    """Mock aiodns query."""
    with patch(
        "supervisor.resolution.checks.dns_server_failure.DNSResolver.query",
        new_callable=AsyncMock,
    ) as dns_query:
        yield dns_query


async def test_base(coresys: CoreSys):
    """Test check basics."""
    dns_server_failures = CheckDNSServerFailures(coresys)
    assert dns_server_failures.slug == "dns_server_failure"
    assert dns_server_failures.enabled


async def test_check(coresys: CoreSys, dns_query: AsyncMock):
    """Test check for DNS server failures."""
    dns_server_failures = CheckDNSServerFailures(coresys)
    coresys.core.state = CoreState.RUNNING

    coresys.plugins.dns.servers = ["dns://1.1.1.1"]
    assert dns_server_failures.dns_servers == [
        "dns://1.1.1.1",
        "dns://192.168.30.1",
    ]
    assert len(coresys.resolution.issues) == 0

    await dns_server_failures.run_check.__wrapped__(dns_server_failures)
    assert dns_query.call_args_list == [
        call("_checkdns.home-assistant.io", "A"),
        call("_checkdns.home-assistant.io", "A"),
    ]
    assert len(coresys.resolution.issues) == 0

    dns_query.reset_mock()
    coresys.plugins.dns.servers = []
    assert dns_server_failures.dns_servers == ["dns://192.168.30.1"]

    dns_query.side_effect = DNSError()
    await dns_server_failures.run_check.__wrapped__(dns_server_failures)
    dns_query.assert_called_once_with("_checkdns.home-assistant.io", "A")

    assert len(coresys.resolution.issues) == 1
    assert coresys.resolution.issues[0].type is IssueType.DNS_SERVER_FAILED
    assert coresys.resolution.issues[0].context is ContextType.DNS_SERVER
    assert coresys.resolution.issues[0].reference == "dns://192.168.30.1"


async def test_approve(coresys: CoreSys, dns_query: AsyncMock):
    """Test approve existing DNS Server failure issues."""
    dns_server_failures = CheckDNSServerFailures(coresys)
    coresys.core.state = CoreState.RUNNING

    assert dns_server_failures.dns_servers == ["dns://192.168.30.1"]
    dns_query.side_effect = DNSError()

    assert await dns_server_failures.approve_check(reference="dns://1.1.1.1") is False
    dns_query.assert_not_called()

    assert (
        await dns_server_failures.approve_check(reference="dns://192.168.30.1") is True
    )
    dns_query.assert_called_once_with("_checkdns.home-assistant.io", "A")

    dns_query.reset_mock()
    dns_query.side_effect = None
    assert (
        await dns_server_failures.approve_check(reference="dns://192.168.30.1") is False
    )
    dns_query.assert_called_once_with("_checkdns.home-assistant.io", "A")


async def test_did_run(coresys: CoreSys):
    """Test that the check ran as expected."""
    dns_server_failures = CheckDNSServerFailures(coresys)
    should_run = dns_server_failures.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert should_run == [CoreState.RUNNING]
    assert len(should_not_run) != 0

    with patch.object(CheckDNSServerFailures, "run_check", return_value=None) as check:
        for state in should_run:
            coresys.core.state = state
            await dns_server_failures()
            check.assert_called_once()
            check.reset_mock()

        for state in should_not_run:
            coresys.core.state = state
            await dns_server_failures()
            check.assert_not_called()
            check.reset_mock()


async def test_check_if_affected(coresys: CoreSys):
    """Test that check is still executed even if already affected."""
    dns_server_failures = CheckDNSServerFailures(coresys)
    coresys.core.state = CoreState.RUNNING

    coresys.resolution.create_issue(
        IssueType.DNS_SERVER_FAILED,
        ContextType.DNS_SERVER,
        reference="dns://192.168.30.1",
    )
    assert len(coresys.resolution.issues) == 1

    with patch.object(
        CheckDNSServerFailures, "approve_check", return_value=True
    ) as approve, patch.object(
        CheckDNSServerFailures, "run_check", return_value=None
    ) as check:
        await dns_server_failures()
        approve.assert_called_once()
        check.assert_called_once()
