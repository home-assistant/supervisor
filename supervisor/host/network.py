"""Info control for host."""

import asyncio
from contextlib import suppress
import logging
from typing import Any

from dbus_fast import Variant

from ..const import ATTR_HOST_INTERNET
from ..coresys import CoreSys, CoreSysAttributes
from ..dbus.const import (
    DBUS_ATTR_CONFIGURATION,
    DBUS_ATTR_CONNECTION_ENABLED,
    DBUS_ATTR_CONNECTIVITY,
    DBUS_IFACE_DNS,
    DBUS_IFACE_NM,
    DBUS_SIGNAL_NM_CONNECTION_ACTIVE_CHANGED,
    ConnectionState,
    ConnectivityState,
    DeviceType,
    WirelessMethodType,
)
from ..dbus.network.connection import NetworkConnection
from ..dbus.network.interface import NetworkInterface
from ..dbus.network.setting import (
    CONF_ATTR_802_WIRELESS_SECURITY,
    CONF_ATTR_802_WIRELESS_SECURITY_PSK,
    CONF_ATTR_CONNECTION,
    CONF_ATTR_CONNECTION_AUTOCONNECT,
    NetworkSetting,
)
from ..dbus.network.setting.generate import get_connection_from_interface
from ..exceptions import (
    DBusError,
    DBusNotConnectedError,
    HostNetworkActivationFailedError,
    HostNetworkActivationTimeoutError,
    HostNetworkCreateConfigError,
    HostNetworkDeactivateConfigError,
    HostNetworkDeleteConfigError,
    HostNetworkError,
    HostNetworkInterfaceUpdateError,
    HostNetworkInterfaceUpdateNotFoundError,
    HostNetworkNotFound,
    HostNetworkUpdateConfigError,
    HostNotSupportedError,
    NetworkInterfaceNotFound,
)
from ..jobs.const import JobCondition
from ..jobs.decorator import Job
from ..resolution.checks.network_interface_ipv4 import CheckNetworkInterfaceIPV4
from ..utils.sentry import async_capture_exception
from .configuration import AccessPoint, Interface, ResolvedInterface
from .const import InterfaceMethod, WifiMode

_LOGGER: logging.Logger = logging.getLogger(__name__)

# Safety net for `_wait_for_activation()`: NetworkManager should always emit a
# terminal state (ACTIVATED/DEACTIVATED), but this guards against it silently
# getting stuck (e.g. a dropped D-Bus signal), which would otherwise hang the
# caller indefinitely.
CONNECTION_ACTIVATION_TIMEOUT = 60


class NetworkManager(CoreSysAttributes):
    """Handle local network setup."""

    def __init__(self, coresys: CoreSys):
        """Initialize system center handling."""
        self.coresys: CoreSys = coresys
        self._connectivity: bool | None = None
        # No event need on initial change (NetworkManager initializes with empty list)
        self._dns_configuration: list = []

    @property
    def connectivity(self) -> bool | None:
        """Return true current connectivity state."""
        return self._connectivity

    @connectivity.setter
    def connectivity(self, state: bool | None) -> None:
        """Set host connectivity state."""
        if self._connectivity == state:
            return

        if state is None or self._connectivity is None:
            self.sys_create_task(
                self.sys_resolution.evaluate.get("connectivity_check")()
            )

        self._connectivity = state
        self.sys_homeassistant.websocket.supervisor_update_event(
            "network", {ATTR_HOST_INTERNET: state}
        )
        if state:
            # Host just regained connectivity; kick a fresh Supervisor probe.
            # Coalescing in request_connectivity_check means redundant calls
            # are safe, so no "only if supervisor is False" guard is needed.
            self.sys_supervisor.request_connectivity_check(force=True)

    @property
    def interfaces(self) -> list[Interface]:
        """Return a dictionary of active interfaces."""
        interfaces: list[Interface] = []
        for inet in self.sys_dbus.network.interfaces:
            interfaces.append(Interface.from_dbus_interface(inet))

        return interfaces

    @property
    def dns_servers(self) -> list[str]:
        """Return a list of local DNS servers."""
        # Read all local dns servers with priority for stable ordering
        servers_with_priority: list[tuple[int, str]] = []
        for config in self.sys_dbus.network.dns.configuration:
            if config.vpn or not config.nameservers:
                continue
            for ns in config.nameservers:
                servers_with_priority.append((config.priority, str(ns)))

        # Sort by priority (ascending) then by server address for stable ordering
        # Remove duplicates while preserving the highest priority (lowest number)
        seen_servers: set[str] = set()
        unique_servers: list[str] = []
        for _, server in sorted(servers_with_priority):
            if server not in seen_servers:
                seen_servers.add(server)
                unique_servers.append(server)

        return unique_servers

    async def check_connectivity(self, *, force: bool = False):
        """Check the internet connection."""
        if not self.sys_dbus.network.connectivity_enabled:
            self.connectivity = None
            return

        # Check connectivity
        try:
            state = await self.sys_dbus.network.check_connectivity(force=force)
            self.connectivity = state == ConnectivityState.CONNECTIVITY_FULL
        except DBusError as err:
            _LOGGER.warning("Can't update connectivity information: %s", err)
            self.connectivity = False

    def get(self, inet_name: str) -> Interface:
        """Return interface from interface name."""
        if inet_name not in self.sys_dbus.network:
            raise HostNetworkNotFound

        return Interface.from_dbus_interface(self.sys_dbus.network.get(inet_name))

    async def get_with_config(self, inet_name: str) -> ResolvedInterface:
        """Return interface from interface name, resolving config independent of activation.

        Unlike `get()`, this also looks up a stored connection profile (via
        `NetworkManager.find_connection_settings()`) when the interface has no
        active connection, so its configuration stays visible while the
        device is down (unplugged, wrong wifi password, etc). Used by the v2
        API.
        """
        if inet_name not in self.sys_dbus.network:
            raise HostNetworkNotFound

        inet = self.sys_dbus.network.get(inet_name)
        resolved_settings = inet.settings
        temp_settings: NetworkSetting | None = None
        if not resolved_settings:
            resolved_settings = (
                temp_settings
            ) = await self.sys_dbus.network.find_connection_settings(inet)

        interface = Interface.from_dbus_interface(
            inet, resolved_settings=resolved_settings
        )

        enabled = True
        if resolved_settings and resolved_settings.connection:
            enabled = resolved_settings.connection.autoconnect is not False

        if temp_settings:
            temp_settings.shutdown()

        return ResolvedInterface(
            interface, has_profile=resolved_settings is not None, enabled=enabled
        )

    async def interfaces_with_config(self) -> list[ResolvedInterface]:
        """Return all interfaces, resolving config independent of activation for each.

        See `get_with_config()`. Used by the v2 API.
        """
        return [
            await self.get_with_config(inet.interface_name)
            for inet in self.sys_dbus.network.interfaces
        ]

    @Job(
        name="network_manager_load",
        conditions=[JobCondition.HOST_NETWORK],
        internal=True,
    )
    async def load(self):
        """Load network information and reapply defaults over dbus."""
        # Apply current settings on each interface so OS can update any out of date defaults
        interfaces = [
            Interface.from_dbus_interface(interface)
            for interface in self.sys_dbus.network.interfaces
            if not CheckNetworkInterfaceIPV4.check_interface(interface)
        ]
        with suppress(HostNetworkNotFound):
            await asyncio.gather(
                *[
                    self.apply_changes(interface, update_only=True)
                    for interface in interfaces
                    if interface.enabled
                    and (
                        interface.ipv4setting.method != InterfaceMethod.DISABLED
                        or interface.ipv6setting.method != InterfaceMethod.DISABLED
                    )
                ]
            )

        self.sys_dbus.network.dbus.properties.on(
            "properties_changed", self._check_connectivity_changed
        )

        self.sys_dbus.network.dns.dbus.properties.on(
            "properties_changed", self._check_dns_changed
        )

    async def _check_connectivity_changed(
        self, interface: str, changed: dict[str, Any], invalidated: list[str]
    ):
        """Check if connectivity property has changed."""
        if interface != DBUS_IFACE_NM:
            return

        connectivity_check: bool | None = changed.get(DBUS_ATTR_CONNECTION_ENABLED)
        connectivity: int | None = changed.get(DBUS_ATTR_CONNECTIVITY)

        if (
            connectivity_check is True
            or DBUS_ATTR_CONNECTION_ENABLED in invalidated
            or DBUS_ATTR_CONNECTIVITY in invalidated
        ):
            self.sys_create_task(self.check_connectivity())

        elif connectivity_check is False:
            self.connectivity = None

        elif connectivity is not None:
            self.connectivity = connectivity == ConnectivityState.CONNECTIVITY_FULL

    async def _check_dns_changed(
        self, interface: str, changed: dict[str, Any], invalidated: list[str]
    ):
        """Check if DNS properties have changed."""
        if interface != DBUS_IFACE_DNS:
            return

        if (
            DBUS_ATTR_CONFIGURATION in changed
            and self._dns_configuration != changed[DBUS_ATTR_CONFIGURATION]
        ):
            self._dns_configuration = changed[DBUS_ATTR_CONFIGURATION]
            self.sys_plugins.dns.notify_locals_changed()

    async def update(self, *, force_connectivity_check: bool = False):
        """Update properties over dbus."""
        _LOGGER.info("Updating local network information")
        try:
            await self.sys_dbus.network.update()
        except DBusError:
            _LOGGER.warning("Can't update network information!")
        except DBusNotConnectedError as err:
            raise HostNotSupportedError(
                "No network D-Bus connection available", _LOGGER.error
            ) from err

        await self.check_connectivity(force=force_connectivity_check)

    async def create_vlan(self, interface: Interface) -> None:
        """Create a VLAN interface."""
        if interface.vlan is None:
            raise RuntimeError("VLAN information is missing")
        # For VLAN interfaces, check if one already exists with same ID on same parent
        try:
            self.sys_dbus.network.get(interface.name)
        except NetworkInterfaceNotFound:
            _LOGGER.debug(
                "VLAN interface %s does not exist, creating it", interface.name
            )
        else:
            raise HostNetworkError(
                f"VLAN {interface.vlan.id} already exists on interface {interface.vlan.interface}",
                _LOGGER.error,
            )

        settings = get_connection_from_interface(interface, self.sys_dbus.network)

        try:
            await self.sys_dbus.network.settings.add_connection(settings)
        except DBusError as err:
            raise HostNetworkError(
                f"Can't create new interface: {err}", _LOGGER.error
            ) from err

        await self.update(force_connectivity_check=True)

    async def _apply_settings_in_place(
        self,
        inet: NetworkInterface,
        interface: Interface,
        settings: dict[str, dict[str, Variant]],
        settings_changed: bool,
        *,
        update_only: bool,
    ) -> bool:
        """Try to make updated connection settings effective in place.

        Return True if the settings are in effect without a full re-activation
        cycle (unchanged or reapplied in place), False if the connection needs
        to be activated.
        """
        # Secrets (Wi-Fi PSK) are excluded from GetSettings and ignored by
        # NetworkManager's Reapply, so a change to them is neither detected
        # nor applied in place. Always re-activate when the payload contains
        # a PSK.
        if CONF_ATTR_802_WIRELESS_SECURITY_PSK in settings.get(
            CONF_ATTR_802_WIRELESS_SECURITY, {}
        ):
            return False

        # In-place application requires an active connection
        if not inet.connection or inet.connection.state != ConnectionState.ACTIVATED:
            return False

        if not settings_changed:
            # User-initiated updates with unchanged settings still re-activate,
            # both as a way to force a reconnect and to cover secret-only
            # changes.
            if not update_only:
                return False
            _LOGGER.debug(
                "Settings for %s unchanged, skipping activation", interface.name
            )
            return True

        try:
            await inet.reapply()
        except DBusError as err:
            _LOGGER.debug(
                "Can't reapply settings for %s in place: %s", interface.name, err
            )
            return False

        _LOGGER.info(
            "Reapplied changed settings for interface %s in place", interface.name
        )
        return True

    async def _apply_update(
        self,
        inet: NetworkInterface,
        interface: Interface,
        existing_settings: NetworkSetting,
        *,
        update_only: bool,
    ) -> NetworkConnection | None:
        """Update an existing stored connection profile.

        Return the newly (re)activated connection if a full activation cycle
        was triggered, None if the change was applied in place or is a no-op.
        """
        _LOGGER.debug("Updating existing configuration for %s", interface.name)
        # Caller only takes this path once it's confirmed `existing_settings.connection`
        # is set (see `apply_changes`).
        assert existing_settings.connection is not None
        settings = get_connection_from_interface(
            interface,
            self.sys_dbus.network,
            name=existing_settings.connection.id,
            uuid=existing_settings.connection.uuid,
        )

        try:
            settings_changed = await existing_settings.update(settings)
            if await self._apply_settings_in_place(
                inet, interface, settings, settings_changed, update_only=update_only
            ):
                return None

            _LOGGER.info("Activating connection for interface %s", interface.name)
            activated = await self.sys_dbus.network.activate_connection(
                existing_settings.object_path, inet.object_path
            )
            _LOGGER.debug("activate_connection returns %s", activated.object_path)
        except DBusError as err:
            _LOGGER.error("Can't update config on %s: %s", interface.name, err)
            raise HostNetworkUpdateConfigError(interface=interface.name) from err

        return activated

    async def _apply_create(
        self, inet: NetworkInterface, interface: Interface
    ) -> NetworkConnection:
        """Create and activate a new connection profile for an interface."""
        _LOGGER.info(
            "Creating and activating connection for interface %s", interface.name
        )
        settings = get_connection_from_interface(interface, self.sys_dbus.network)

        try:
            _, activated = await self.sys_dbus.network.add_and_activate_connection(
                settings, inet.object_path
            )
            _LOGGER.debug(
                "add_and_activate_connection returns %s", activated.object_path
            )
        except DBusError as err:
            _LOGGER.error(
                "Can't create config and activate %s: %s", interface.name, err
            )
            raise HostNetworkCreateConfigError(interface=interface.name) from err

        return activated

    async def _apply_delete(
        self, interface: Interface, existing_settings: NetworkSetting | None
    ) -> None:
        """Delete the stored connection profile for a disabled interface."""
        if not existing_settings:
            _LOGGER.debug("Interface %s is already disabled.", interface.name)
            return

        _LOGGER.info("Deleting configuration for interface %s", interface.name)
        try:
            await existing_settings.delete()
        except DBusError as err:
            _LOGGER.error(
                "Can't delete configuration for interface %s: %s", interface.name, err
            )
            raise HostNetworkDeleteConfigError(interface=interface.name) from err

    async def _apply_deactivate(
        self,
        inet: NetworkInterface,
        interface: Interface,
        existing_settings: NetworkSetting | None,
    ) -> None:
        """Deactivate an interface's connection and clear autoconnect, keeping its profile."""
        if not existing_settings:
            _LOGGER.debug("Interface %s is already disabled.", interface.name)
            return

        _LOGGER.info("Deactivating interface %s", interface.name)
        try:
            if inet.connection:
                await self.sys_dbus.network.deactivate_connection(
                    inet.connection.object_path
                )
            await existing_settings.update(
                {
                    CONF_ATTR_CONNECTION: {
                        CONF_ATTR_CONNECTION_AUTOCONNECT: Variant("b", False)
                    }
                }
            )
        except DBusError as err:
            _LOGGER.error("Can't deactivate interface %s: %s", interface.name, err)
            raise HostNetworkDeactivateConfigError(interface=interface.name) from err

    async def _wait_for_activation(self, con: NetworkConnection) -> None:
        """Wait for a connection to finish activating.

        Raises `HostNetworkActivationFailedError` if the connection
        deactivates instead, or `HostNetworkActivationTimeoutError` if it
        doesn't reach a terminal state within `CONNECTION_ACTIVATION_TIMEOUT`
        seconds (see its definition for why).
        """
        async with con.connected_dbus.signal(
            DBUS_SIGNAL_NM_CONNECTION_ACTIVE_CHANGED
        ) as signal:
            # From this point we monitor signals. However, it might be that
            # the state change before this point. Get the state currently to
            # avoid any race condition.
            await con.update()
            state: ConnectionState = con.state

            try:
                async with asyncio.timeout(CONNECTION_ACTIVATION_TIMEOUT):
                    while state != ConnectionState.ACTIVATED:
                        if state == ConnectionState.DEACTIVATED:
                            raise HostNetworkActivationFailedError

                        msg = await signal.wait_for_signal()
                        state = ConnectionState(msg[0])
                        _LOGGER.debug("Active connection state changed to %s", state)
            except TimeoutError as err:
                raise HostNetworkActivationTimeoutError(_LOGGER.error) from err

    async def apply_changes(
        self,
        interface: Interface,
        *,
        update_only: bool = False,
        resolved_settings: NetworkSetting | None = None,
        destructive_disable: bool = True,
    ) -> None:
        """Apply Interface changes to host.

        `resolved_settings` allows updating an existing stored connection
        profile even when the interface currently has no active connection
        (see `NetworkManager.find_connection_settings()`). When omitted, only
        an active connection (`inet.settings`) is treated as existing
        configuration to update - unchanged v1 behavior.

        `destructive_disable` controls what happens when disabling the
        interface: True (default, v1 behavior) deletes any stored connection
        profile. False deactivates the active connection (if any) and clears
        autoconnect on the stored profile instead of deleting it.
        """
        try:
            inet = self.sys_dbus.network.get(interface.name)
        except NetworkInterfaceNotFound as err:
            # The API layer (or anybody else) should not pass any updates for
            # non-existing interfaces.
            await async_capture_exception(err)
            raise HostNetworkInterfaceUpdateError(_LOGGER.warning) from err

        existing_settings = inet.settings or resolved_settings
        con: NetworkConnection | None = None

        # Update exist configuration
        if (
            existing_settings
            and existing_settings.connection
            and interface.matches_settings(inet, existing_settings)
            and interface.enabled
        ):
            con = await self._apply_update(
                inet, interface, existing_settings, update_only=update_only
            )

        # Stop if only updates are allowed as other paths create/delete interfaces
        elif update_only:
            raise HostNetworkInterfaceUpdateNotFoundError(
                _LOGGER.warning, interface=interface.name
            )

        # Create new configuration and activate interface
        elif interface.enabled:
            con = await self._apply_create(inet, interface)

        # Remove config from interface
        elif not interface.enabled:
            if destructive_disable:
                await self._apply_delete(interface, existing_settings)
            else:
                await self._apply_deactivate(inet, interface, existing_settings)

        else:
            raise HostNetworkInterfaceUpdateError(_LOGGER.warning)

        if con:
            await self._wait_for_activation(con)

        # update_only means not done by user so don't force a check afterwards
        await self.update(force_connectivity_check=not update_only)

    async def apply_changes_v2(self, interface: Interface) -> None:
        """Apply v2 Interface changes, resolving an existing profile independent of activation.

        Thin wrapper around `apply_changes()`: looks up a stored connection
        profile via `NetworkManager.find_connection_settings()` when the
        interface has no active connection, so a PUT can update/reactivate
        that profile instead of creating a duplicate one (R2), then cleans up
        the temporary D-Bus object it created for the lookup (if any). Always
        disables non-destructively (R5) - the v2 API never deletes a stored
        connection profile, unlike v1's default `apply_changes()` behavior.
        """
        try:
            inet = self.sys_dbus.network.get(interface.name)
        except NetworkInterfaceNotFound:
            inet = None

        resolved_settings: NetworkSetting | None = None
        temp_settings: NetworkSetting | None = None
        if inet:
            resolved_settings = inet.settings
            if not resolved_settings:
                resolved_settings = (
                    temp_settings
                ) = await self.sys_dbus.network.find_connection_settings(inet)

        try:
            await self.apply_changes(
                interface,
                resolved_settings=resolved_settings,
                destructive_disable=False,
            )
        finally:
            if temp_settings:
                temp_settings.shutdown()

    async def scan_wifi(self, interface: Interface) -> list[AccessPoint]:
        """Scan on Interface for AccessPoint."""
        inet = self.sys_dbus.network.get(interface.name)

        if inet.type != DeviceType.WIRELESS or not inet.wireless:
            raise HostNotSupportedError(
                f"Can only scan with wireless card - {interface.name}", _LOGGER.error
            )

        # Request Scan
        try:
            await inet.wireless.request_scan()
        except DBusError as err:
            _LOGGER.warning("Can't request a new scan: %s", err)
            raise HostNetworkError from err

        await asyncio.sleep(5)

        # Process AP
        return [
            AccessPoint(
                WifiMode[WirelessMethodType(accesspoint.mode).name],
                accesspoint.ssid,
                accesspoint.mac,
                accesspoint.frequency,
                accesspoint.strength,
            )
            for accesspoint in await inet.wireless.get_all_accesspoints()
            if accesspoint.dbus
        ]
