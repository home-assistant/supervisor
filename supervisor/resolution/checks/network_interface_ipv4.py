"""Helpers to check core security."""

from ...const import CoreState
from ...coresys import CoreSys
from ...dbus.const import ConnectionStateFlags, ConnectionStateType
from ...dbus.network.interface import NetworkInterface
from ...exceptions import NetworkInterfaceNotFound
from ..const import ContextType, IssueType
from .base import CheckBase


def setup(coresys: CoreSys) -> CheckBase:
    """Check setup function."""
    return CheckNetworkInterfaceIPV4(coresys)


class CheckNetworkInterfaceIPV4(CheckBase):
    """CheckNetworkInterfaceIPV4 class for check."""

    async def run_check(self) -> None:
        """Run check if not affected by issue."""
        for interface in self.sys_dbus.network.interfaces:
            if CheckNetworkInterfaceIPV4.check_interface(interface):
                self.sys_resolution.create_issue(
                    IssueType.IPV4_CONNECTION_PROBLEM,
                    ContextType.SYSTEM,
                    interface.name,
                )

    async def approve_check(self, reference: str | None = None) -> bool:
        """Approve check if it is affected by issue."""
        if not reference:
            return False

        try:
            return CheckNetworkInterfaceIPV4.check_interface(
                self.sys_dbus.network.get(reference)
            )
        except NetworkInterfaceNotFound:
            return False

    @staticmethod
    def check_interface(interface: NetworkInterface) -> bool:
        """Return true if a managed, connected interface has an issue."""
        if not (interface.managed and interface.connection):
            return False

        return not (
            interface.connection.state
            in [ConnectionStateType.ACTIVATED, ConnectionStateType.ACTIVATING]
            and ConnectionStateFlags.IP4_READY in interface.connection.state_flags
        )

    @property
    def issue(self) -> IssueType:
        """Return a IssueType enum."""
        return IssueType.IPV4_CONNECTION_PROBLEM

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.SYSTEM

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this check can run."""
        return [CoreState.RUNNING, CoreState.STARTUP]
