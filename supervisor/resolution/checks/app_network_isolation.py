"""Check that assigned app network isolation endpoints are still valid."""

import logging

from ...const import CoreState
from ...coresys import CoreSys
from ...docker.const import NetworkIsolationConfig
from ...docker.external_network import DockerExternalNetworks
from ...exceptions import HostNetworkNotFound
from ..const import ContextType, IssueType
from .base import CheckBase

_LOGGER: logging.Logger = logging.getLogger(__name__)


def setup(coresys: CoreSys) -> CheckBase:
    """Check setup function."""
    return CheckAppNetworkIsolation(coresys)


class CheckAppNetworkIsolation(CheckBase):
    """CheckAppNetworkIsolation class for check."""

    async def run_check(self) -> None:
        """Run check if not affected by issue."""
        for app in self.sys_apps.installed:
            if (config := app.network_isolation) and self._endpoint_broken(config):
                self.sys_resolution.create_issue(
                    IssueType.NETWORK_ISOLATION_FAILED,
                    ContextType.ADDON,
                    reference=app.slug,
                )

    async def approve_check(self, reference: str | None = None) -> bool:
        """Approve check if it is affected by issue."""
        if not reference:
            return False

        # Uninstalled
        if not (app := self.sys_apps.get_local_only(reference)):
            return False

        # Isolation no longer assigned
        if not (config := app.network_isolation):
            return False

        return self._endpoint_broken(config)

    def _endpoint_broken(self, config: NetworkIsolationConfig) -> bool:
        """Return True if the endpoint no longer matches the host interface."""
        try:
            interface = self.sys_host.network.get(config.interface)
        except HostNetworkNotFound:
            return True

        if not DockerExternalNetworks.capable_interface(interface):
            return True

        subnet = DockerExternalNetworks.interface_subnet(interface)
        return subnet is None or config.ipv4 not in subnet

    @property
    def issue(self) -> IssueType:
        """Return a IssueType enum."""
        return IssueType.NETWORK_ISOLATION_FAILED

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.ADDON

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this check can run."""
        return [CoreState.RUNNING, CoreState.STARTUP]
