"""Helpers to check DNS servers for failure."""

import asyncio
from datetime import timedelta
from typing import Literal

from aiodns import DNSResolver
from aiodns.error import DNSError

from ...const import CoreState
from ...coresys import CoreSys
from ...jobs.const import JobCondition, JobExecutionLimit
from ...jobs.decorator import Job
from ...utils.sentry import async_capture_exception
from ..const import DNS_CHECK_HOST, ContextType, IssueType
from .base import CheckBase


async def check_server(
    loop: asyncio.AbstractEventLoop, server: str, qtype: Literal["A"] | Literal["AAAA"]
) -> None:
    """Check a DNS server and report issues."""
    ip_addr = server[6:] if server.startswith("dns://") else server
    async with DNSResolver(loop=loop, nameservers=[ip_addr]) as resolver:
        await resolver.query(DNS_CHECK_HOST, qtype)


def setup(coresys: CoreSys) -> CheckBase:
    """Check setup function."""
    return CheckDNSServer(coresys)


class CheckDNSServer(CheckBase):
    """CheckDNSServer class for check."""

    @Job(
        name="check_dns_server_run",
        conditions=[JobCondition.INTERNET_SYSTEM],
        limit=JobExecutionLimit.THROTTLE,
        throttle_period=timedelta(hours=24),
    )
    async def run_check(self) -> None:
        """Run check if not affected by issue."""
        dns_servers = self.dns_servers
        results = await asyncio.gather(
            *[check_server(self.sys_loop, server, "A") for server in dns_servers],
            return_exceptions=True,
        )
        # pylint: disable-next=consider-using-enumerate
        for i in range(len(results)):
            if isinstance(result := results[i], DNSError):
                self.sys_resolution.create_issue(
                    IssueType.DNS_SERVER_FAILED,
                    ContextType.DNS_SERVER,
                    reference=dns_servers[i],
                )
                await async_capture_exception(result)

    @Job(name="check_dns_server_approve", conditions=[JobCondition.INTERNET_SYSTEM])
    async def approve_check(self, reference: str | None = None) -> bool:
        """Approve check if it is affected by issue."""
        if reference not in self.dns_servers:
            return False

        try:
            await check_server(self.sys_loop, reference, "A")
        except DNSError:
            return True

        return False

    @property
    def dns_servers(self) -> list[str]:
        """All user and system provided dns servers."""
        return self.sys_plugins.dns.servers + self.sys_plugins.dns.locals

    @property
    def issue(self) -> IssueType:
        """Return a IssueType enum."""
        return IssueType.DNS_SERVER_FAILED

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.DNS_SERVER

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this check can run."""
        return [CoreState.RUNNING]
