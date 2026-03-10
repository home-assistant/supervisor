"""Firewall management to protect Supervisor network gateway."""

from contextlib import suppress
import logging

from dbus_fast import Variant

from ..const import DOCKER_IPV4_NETWORK_MASK, DOCKER_IPV6_NETWORK_MASK, DOCKER_NETWORK
from ..coresys import CoreSys, CoreSysAttributes
from ..dbus.const import StartUnitMode
from ..exceptions import DBusError

_LOGGER: logging.Logger = logging.getLogger(__name__)

FIREWALL_SERVICE = "supervisor-firewall-gateway.service"
SHELL_CMD = "/bin/sh"
IPTABLES_CMD = "/usr/sbin/iptables"
IP6TABLES_CMD = "/usr/sbin/ip6tables"


class FirewallManager(CoreSysAttributes):
    """Manage firewall rules to protect the Supervisor network gateway.

    Adds iptables rules in the raw PREROUTING chain to drop traffic addressed
    to the bridge gateway IP from external interfaces. This prevents hosts
    with a static route to the bridge subnet from reaching services bound to
    the gateway address.
    """

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize firewall manager."""
        self.coresys: CoreSys = coresys

    @staticmethod
    def _build_exec_start() -> list[tuple[str, list[str], bool]]:
        """Build ExecStart entries for gateway protection rules.

        Each entry uses shell check-or-insert logic for idempotency.
        We insert DROP first, then ACCEPT, using -I (insert at top).
        The last inserted rule ends up first in the chain, so ACCEPT
        for loopback ends up above the DROP for non-bridge interfaces.
        """
        gateway_ipv4 = str(DOCKER_IPV4_NETWORK_MASK[1])
        gateway_ipv6 = str(DOCKER_IPV6_NETWORK_MASK[1])
        bridge = DOCKER_NETWORK

        entries: list[tuple[str, list[str], bool]] = []
        for cmd, gateway in (
            (IPTABLES_CMD, gateway_ipv4),
            (IP6TABLES_CMD, gateway_ipv6),
        ):
            # DROP packets to gateway from non-bridge, non-loopback interfaces
            entries.append(
                (
                    SHELL_CMD,
                    [
                        SHELL_CMD,
                        "-c",
                        f"{cmd} -t raw -C PREROUTING ! -i {bridge} -d {gateway}"
                        f" -j DROP 2>/dev/null"
                        f" || {cmd} -t raw -I PREROUTING ! -i {bridge} -d {gateway}"
                        f" -j DROP",
                    ],
                    False,
                )
            )

            # ACCEPT loopback traffic to gateway (inserted last, ends up first)
            entries.append(
                (
                    SHELL_CMD,
                    [
                        SHELL_CMD,
                        "-c",
                        f"{cmd} -t raw -C PREROUTING -i lo -d {gateway}"
                        f" -j ACCEPT 2>/dev/null"
                        f" || {cmd} -t raw -I PREROUTING -i lo -d {gateway}"
                        f" -j ACCEPT",
                    ],
                    False,
                )
            )

        return entries

    async def apply_gateway_protection(self) -> None:
        """Apply iptables rules to protect the Docker gateway from external access."""
        if not self.sys_dbus.systemd.is_connected:
            _LOGGER.warning(
                "Systemd not available, cannot apply gateway firewall protection"
            )
            return

        # Clean up any previous failed unit
        with suppress(DBusError):
            await self.sys_dbus.systemd.reset_failed_unit(FIREWALL_SERVICE)

        properties: list[tuple[str, Variant]] = [
            ("Description", Variant("s", "Supervisor gateway firewall protection")),
            ("Type", Variant("s", "oneshot")),
            ("ExecStart", Variant("a(sasb)", self._build_exec_start())),
        ]

        try:
            await self.sys_dbus.systemd.start_transient_unit(
                FIREWALL_SERVICE,
                StartUnitMode.REPLACE,
                properties,
            )
        except DBusError as err:
            _LOGGER.warning("Failed to apply gateway firewall protection: %s", err)
            return

        _LOGGER.info("Gateway firewall protection applied")
