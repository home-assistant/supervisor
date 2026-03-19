"""Firewall rules for the Supervisor network gateway."""

import asyncio
from contextlib import suppress
import logging

from dbus_fast import Variant

from ..const import DOCKER_IPV4_NETWORK_MASK, DOCKER_IPV6_NETWORK_MASK, DOCKER_NETWORK
from ..coresys import CoreSys, CoreSysAttributes
from ..dbus.const import (
    DBUS_ATTR_ACTIVE_STATE,
    DBUS_IFACE_SYSTEMD_UNIT,
    StartUnitMode,
    UnitActiveState,
)
from ..dbus.systemd import ExecStartEntry
from ..exceptions import DBusError
from ..resolution.const import UnhealthyReason

_LOGGER: logging.Logger = logging.getLogger(__name__)

FIREWALL_SERVICE = "supervisor-firewall-gateway.service"
FIREWALL_UNIT_TIMEOUT = 30
BIN_SH = "/bin/sh"
IPTABLES_CMD = "/usr/sbin/iptables"
IP6TABLES_CMD = "/usr/sbin/ip6tables"

TERMINAL_STATES = {UnitActiveState.INACTIVE, UnitActiveState.FAILED}


class FirewallManager(CoreSysAttributes):
    """Manage firewall rules to protect the Supervisor network gateway.

    Adds iptables rules in the raw PREROUTING chain to drop traffic addressed
    to the bridge gateway IP that does not originate from the bridge or
    loopback interfaces.
    """

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize firewall manager."""
        self.coresys: CoreSys = coresys

    @staticmethod
    def _build_exec_start() -> list[ExecStartEntry]:
        """Build ExecStart entries for gateway firewall rules.

        Each entry uses shell check-or-insert logic for idempotency.
        We insert DROP first, then ACCEPT, using -I (insert at top).
        The last inserted rule ends up first in the chain, so ACCEPT
        for loopback ends up above the DROP for non-bridge interfaces.
        """
        gateway_ipv4 = str(DOCKER_IPV4_NETWORK_MASK[1])
        gateway_ipv6 = str(DOCKER_IPV6_NETWORK_MASK[1])
        bridge = DOCKER_NETWORK

        entries: list[ExecStartEntry] = []
        for cmd, gateway in (
            (IPTABLES_CMD, gateway_ipv4),
            (IP6TABLES_CMD, gateway_ipv6),
        ):
            # DROP packets to gateway from non-bridge, non-loopback interfaces
            entries.append(
                ExecStartEntry(
                    binary=BIN_SH,
                    argv=[
                        BIN_SH,
                        "-c",
                        f"{cmd} -t raw -C PREROUTING ! -i {bridge} -d {gateway}"
                        f" -j DROP 2>/dev/null"
                        f" || {cmd} -t raw -I PREROUTING ! -i {bridge} -d {gateway}"
                        f" -j DROP",
                    ],
                    ignore_failure=False,
                )
            )

            # ACCEPT loopback traffic to gateway (inserted last, ends up first)
            entries.append(
                ExecStartEntry(
                    binary=BIN_SH,
                    argv=[
                        BIN_SH,
                        "-c",
                        f"{cmd} -t raw -C PREROUTING -i lo -d {gateway}"
                        f" -j ACCEPT 2>/dev/null"
                        f" || {cmd} -t raw -I PREROUTING -i lo -d {gateway}"
                        f" -j ACCEPT",
                    ],
                    ignore_failure=False,
                )
            )

        return entries

    async def _apply_gateway_firewall_rules(self) -> bool:
        """Apply iptables rules to restrict access to the Docker gateway.

        Returns True if the rules were successfully applied.
        """
        if not self.sys_dbus.systemd.is_connected:
            _LOGGER.error("Systemd not available, cannot apply gateway firewall rules")
            return False

        # Clean up any previous failed unit
        with suppress(DBusError):
            await self.sys_dbus.systemd.reset_failed_unit(FIREWALL_SERVICE)

        properties: list[tuple[str, Variant]] = [
            ("Description", Variant("s", "Supervisor gateway firewall rules")),
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
            _LOGGER.error("Failed to apply gateway firewall rules: %s", err)
            return False

        # Wait for the oneshot unit to finish and verify it succeeded
        try:
            unit = await self.sys_dbus.systemd.get_unit(FIREWALL_SERVICE)
            async with (
                asyncio.timeout(FIREWALL_UNIT_TIMEOUT),
                unit.properties_changed() as signal,
            ):
                state = await unit.get_active_state()
                while state not in TERMINAL_STATES:
                    props = await signal.wait_for_signal()
                    if (
                        props[0] == DBUS_IFACE_SYSTEMD_UNIT
                        and DBUS_ATTR_ACTIVE_STATE in props[1]
                    ):
                        state = UnitActiveState(props[1][DBUS_ATTR_ACTIVE_STATE].value)
        except (DBusError, TimeoutError) as err:
            _LOGGER.error(
                "Failed waiting for gateway firewall unit to complete: %s", err
            )
            return False

        if state == UnitActiveState.FAILED:
            _LOGGER.error(
                "Gateway firewall unit failed, iptables rules may not be applied"
            )
            return False

        return True

    async def apply_gateway_firewall_rules(self) -> None:
        """Apply gateway firewall rules, marking unsupported on failure."""
        if await self._apply_gateway_firewall_rules():
            _LOGGER.info("Gateway firewall rules applied")
        else:
            self.sys_resolution.add_unhealthy_reason(
                UnhealthyReason.DOCKER_GATEWAY_UNPROTECTED
            )
