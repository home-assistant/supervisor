"""Helpers to check core security."""
from ...const import CoreState
from ...coresys import CoreSys
from ...dbus.const import InterfaceMethod
from ...dbus.network.interface import NetworkInterface
from ..const import ContextType, IssueType
from .base import CheckBase


def setup(coresys: CoreSys) -> CheckBase:
    """Check setup function."""
    return CheckDHCP(coresys)


class CheckDHCP(CheckBase):
    """CheckDHCP class for check."""

    async def run_check(self) -> None:
        """Run check if not affected by issue."""
        for interface in self.sys_dbus.network.interfaces.values():
            if CheckDHCP.check_interface(interface):
                self.sys_resolution.create_issue(
                    IssueType.DHCP_FAILURE,
                    ContextType.SYSTEM,
                    interface.name,
                )

    async def approve_check(self, reference: str | None = None) -> bool:
        """Approve check if it is affected by issue."""
        interface = self.sys_dbus.network.interfaces.get(reference)

        return interface and CheckDHCP.check_interface(interface)

    @staticmethod
    def check_interface(interface: NetworkInterface) -> bool:
        """Return true if a managed interface has a DHCP issue."""
        if not (interface.managed and interface.settings):
            return False

        return (
            interface.settings.ipv4
            and interface.settings.ipv4.method == InterfaceMethod.AUTO.value
            and not interface.connection.ipv4
            or interface.settings.ipv6
            and interface.settings.ipv6.method == InterfaceMethod.AUTO.value
            and not interface.connection.ipv6
        )

    @property
    def issue(self) -> IssueType:
        """Return a IssueType enum."""
        return IssueType.DHCP_FAILURE

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.SYSTEM

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this check can run."""
        return [CoreState.RUNNING, CoreState.STARTUP]
