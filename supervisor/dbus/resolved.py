"""D-Bus interface for systemd-resolved."""

from __future__ import annotations

import logging

from dbus_fast.aio.message_bus import MessageBus

from ..exceptions import DBusError, DBusInterfaceError, DBusServiceUnkownError
from .const import (
    DBUS_ATTR_CACHE_STATISTICS,
    DBUS_ATTR_CURRENT_DNS_SERVER,
    DBUS_ATTR_CURRENT_DNS_SERVER_EX,
    DBUS_ATTR_DNS,
    DBUS_ATTR_DNS_EX,
    DBUS_ATTR_DNS_OVER_TLS,
    DBUS_ATTR_DNS_STUB_LISTENER,
    DBUS_ATTR_DNSSEC,
    DBUS_ATTR_DNSSEC_NEGATIVE_TRUST_ANCHORS,
    DBUS_ATTR_DNSSEC_STATISTICS,
    DBUS_ATTR_DNSSEC_SUPPORTED,
    DBUS_ATTR_DOMAINS,
    DBUS_ATTR_FALLBACK_DNS,
    DBUS_ATTR_FALLBACK_DNS_EX,
    DBUS_ATTR_LLMNR,
    DBUS_ATTR_LLMNR_HOSTNAME,
    DBUS_ATTR_MULTICAST_DNS,
    DBUS_ATTR_RESOLV_CONF_MODE,
    DBUS_ATTR_TRANSACTION_STATISTICS,
    DBUS_IFACE_RESOLVED_MANAGER,
    DBUS_NAME_RESOLVED,
    DBUS_OBJECT_RESOLVED,
    DNSAddressFamily,
    DNSOverTLSEnabled,
    DNSSECValidation,
    DNSStubListenerEnabled,
    MulticastProtocolEnabled,
    ResolvConfMode,
)
from .interface import DBusInterfaceProxy, dbus_property

_LOGGER: logging.Logger = logging.getLogger(__name__)


class Resolved(DBusInterfaceProxy):
    """Handle D-Bus interface for systemd-resolved.

    https://www.freedesktop.org/software/systemd/man/org.freedesktop.resolve1.html
    """

    name: str = DBUS_NAME_RESOLVED
    bus_name: str = DBUS_NAME_RESOLVED
    object_path: str = DBUS_OBJECT_RESOLVED
    properties_interface: str = DBUS_IFACE_RESOLVED_MANAGER

    async def connect(self, bus: MessageBus):
        """Connect to D-Bus."""
        _LOGGER.info("Load dbus interface %s", self.name)
        try:
            await super().connect(bus)
        except DBusError:
            _LOGGER.warning("Can't connect to systemd-resolved.")
        except (DBusServiceUnkownError, DBusInterfaceError):
            _LOGGER.warning(
                "Host has no systemd-resolved support. DNS will not work correctly."
            )

    @property
    @dbus_property
    def cache_statistics(self) -> tuple[int, int, int] | None:
        """Return current cache entries and hits and misses since last reset."""
        return self.properties[DBUS_ATTR_CACHE_STATISTICS]

    @property
    @dbus_property
    def current_dns_server(
        self,
    ) -> list[tuple[int, DNSAddressFamily, bytes]] | None:
        """Return current DNS server."""
        return self.properties[DBUS_ATTR_CURRENT_DNS_SERVER]

    @property
    @dbus_property
    def current_dns_server_ex(
        self,
    ) -> list[tuple[int, DNSAddressFamily, bytes, int, str]] | None:
        """Return current DNS server including port and server name."""
        return self.properties[DBUS_ATTR_CURRENT_DNS_SERVER_EX]

    @property
    @dbus_property
    def dns(self) -> list[tuple[int, DNSAddressFamily, bytes]] | None:
        """Return DNS servers in use."""
        return self.properties[DBUS_ATTR_DNS]

    @property
    @dbus_property
    def dns_ex(self) -> list[tuple[int, DNSAddressFamily, bytes, int, str]] | None:
        """Return DNS servers in use including port and server name."""
        return self.properties[DBUS_ATTR_DNS_EX]

    @property
    @dbus_property
    def dns_over_tls(self) -> DNSOverTLSEnabled | None:
        """Return DNS over TLS enabled."""
        return self.properties[DBUS_ATTR_DNS_OVER_TLS]

    @property
    @dbus_property
    def dns_stub_listener(self) -> DNSStubListenerEnabled | None:
        """Return DNS stub listener enabled on port 53."""
        return self.properties[DBUS_ATTR_DNS_STUB_LISTENER]

    @property
    @dbus_property
    def dnssec(self) -> DNSSECValidation | None:
        """Return DNSSEC validation enforced."""
        return self.properties[DBUS_ATTR_DNSSEC]

    @property
    @dbus_property
    def dnssec_negative_trust_anchors(self) -> list[str] | None:
        """Return DNSSEC negative trust anchors."""
        return self.properties[DBUS_ATTR_DNSSEC_NEGATIVE_TRUST_ANCHORS]

    @property
    @dbus_property
    def dnssec_statistics(self) -> tuple[int, int, int, int] | None:
        """Return Secure, insecure, bogus, and indeterminate DNSSEC validations since last reset."""
        return self.properties[DBUS_ATTR_DNSSEC_STATISTICS]

    @property
    @dbus_property
    def dnssec_supported(self) -> bool | None:
        """Return DNSSEC enabled and selected DNS servers support it."""
        return self.properties[DBUS_ATTR_DNSSEC_SUPPORTED]

    @property
    @dbus_property
    def domains(self) -> list[tuple[int, str, bool]] | None:
        """Return search and routing domains in use."""
        return self.properties[DBUS_ATTR_DOMAINS]

    @property
    @dbus_property
    def fallback_dns(self) -> list[tuple[int, DNSAddressFamily, bytes]] | None:
        """Return fallback DNS servers."""
        return self.properties[DBUS_ATTR_FALLBACK_DNS]

    @property
    @dbus_property
    def fallback_dns_ex(
        self,
    ) -> list[tuple[int, DNSAddressFamily, bytes, int, str]] | None:
        """Return fallback DNS servers including port and server name."""
        return self.properties[DBUS_ATTR_FALLBACK_DNS_EX]

    @property
    @dbus_property
    def llmnr(self) -> MulticastProtocolEnabled | None:
        """Return LLMNR enabled."""
        return self.properties[DBUS_ATTR_LLMNR]

    @property
    @dbus_property
    def llmnr_hostname(self) -> str | None:
        """Return LLMNR hostname on network."""
        return self.properties[DBUS_ATTR_LLMNR_HOSTNAME]

    @property
    @dbus_property
    def multicast_dns(self) -> MulticastProtocolEnabled | None:
        """Return MDNS enabled."""
        return self.properties[DBUS_ATTR_MULTICAST_DNS]

    @property
    @dbus_property
    def resolv_conf_mode(self) -> ResolvConfMode | None:
        """Return how /etc/resolv.conf managed on host."""
        return self.properties[DBUS_ATTR_RESOLV_CONF_MODE]

    @property
    @dbus_property
    def transaction_statistics(self) -> tuple[int, int] | None:
        """Return transactions processing and processed since last reset."""
        return self.properties[DBUS_ATTR_TRANSACTION_STATISTICS]
