"""Helpers to check DNS servers for failure."""
import asyncio
from datetime import timedelta

from aiodns import DNSResolver
from aiodns.error import DNSError

from ...const import CoreState
from ...coresys import CoreSys
from ...jobs.const import JobCondition, JobExecutionLimit
from ...jobs.decorator import Job
from ...utils.sentry import capture_exception
from ..const import DNS_CHECK_HOST, ContextType, IssueType
from .base import CheckBase


def setup(coresys: CoreSys) -> CheckBase:
    """Check setup function."""
    return CheckDNSServer(coresys)


class CheckDNSServer(CheckBase):
    """CheckDNSServer class for check."""

    @Job(
        conditions=[JobCondition.INTERNET_SYSTEM],
        limit=JobExecutionLimit.THROTTLE,
        throttle_period=timedelta(hours=24),
    )
    async def run_check(self) -> None:
        """Run check if not affected by issue."""
        dns_servers = self.dns_servers
        results = await asyncio.gather(
            *[self._check_server(server) for server in dns_servers],
            return_exceptions=True,
        )
        for i in (r for r in range(len(results)) if isinstance(results[r], DNSError)):
            self.sys_resolution.create_issue(
                IssueType.DNS_SERVER_FAILED,
                ContextType.DNS_SERVER,
                reference=dns_servers[i],
            )
            capture_exception(results[i])

    @Job(conditions=[JobCondition.INTERNET_SYSTEM])
    async def approve_check(self, reference: str | None = None) -> bool:
        """Approve check if it is affected by issue."""
        if reference not in self.dns_servers:
            return False

        try:
            await self._check_server(reference)
        except DNSError:
            return True

        return False

    async def _check_server(self, server: str):
        """Check a DNS server and report issues."""
        ip_addr = server[6:] if server.startswith("dns://") else server
        resolver = DNSResolver(nameservers=[ip_addr])
        await resolver.query(DNS_CHECK_HOST, "A")

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
