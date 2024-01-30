"""Mock of resolved dbus service."""

from dbus_fast.service import PropertyAccess, dbus_property

from .base import DBusServiceMock

BUS_NAME = "org.freedesktop.resolve1"


def setup(object_path: str | None = None) -> DBusServiceMock:
    """Create dbus mock object."""
    return Resolved()


class Resolved(DBusServiceMock):
    """Resolved mock.

    gdbus introspect --system --dest org.freedesktop.resolve1 --object-path /org/freedesktop/resolve1
    """

    object_path = "/org/freedesktop/resolve1"
    interface = "org.freedesktop.resolve1.Manager"

    @dbus_property(access=PropertyAccess.READ)
    def LLMNRHostname(self) -> "s":
        """Get LLMNRHostname."""
        return "homeassistant"

    @dbus_property(access=PropertyAccess.READ)
    def LLMNR(self) -> "s":
        """Get LLMNR."""
        return "yes"

    @dbus_property(access=PropertyAccess.READ)
    def MulticastDNS(self) -> "s":
        """Get MulticastDNS."""
        return "resolve"

    @dbus_property(access=PropertyAccess.READ)
    def DNSOverTLS(self) -> "s":
        """Get DNSOverTLS."""
        return "no"

    @dbus_property(access=PropertyAccess.READ)
    def DNS(self) -> "a(iiay)":
        """Get DNS."""
        return [
            [0, 2, bytes([127, 0, 0, 1])],
            [
                0,
                10,
                bytes(
                    [
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x1,
                    ]
                ),
            ],
        ]

    @dbus_property(access=PropertyAccess.READ)
    def DNSEx(self) -> "a(iiayqs)":
        """Get DNSEx."""
        return [
            [0, 2, bytes([127, 0, 0, 1]), 0, ""],
            [
                0,
                10,
                bytes(
                    [
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x1,
                    ]
                ),
                0,
                "",
            ],
        ]

    @dbus_property(access=PropertyAccess.READ)
    def FallbackDNS(self) -> "a(iiay)":
        """Get FallbackDNS."""
        return [
            [0, 2, bytes([1, 1, 1, 1])],
            [
                0,
                10,
                bytes(
                    [
                        0x26,
                        0x6,
                        0x47,
                        0x0,
                        0x47,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x11,
                        0x11,
                    ]
                ),
            ],
        ]

    @dbus_property(access=PropertyAccess.READ)
    def FallbackDNSEx(self) -> "a(iiayqs)":
        """Get FallbackDNSEx."""
        return [
            [0, 2, bytes([1, 1, 1, 1]), 0, "cloudflare-dns.com"],
            [
                0,
                10,
                bytes(
                    [
                        0x26,
                        0x6,
                        0x47,
                        0x0,
                        0x47,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x11,
                        0x11,
                    ]
                ),
                0,
                "cloudflare-dns.com",
            ],
        ]

    @dbus_property(access=PropertyAccess.READ)
    def CurrentDNSServer(self) -> "(iiay)":
        """Get CurrentDNSServer."""
        return [0, 2, bytes([127, 0, 0, 1])]

    @dbus_property(access=PropertyAccess.READ)
    def CurrentDNSServerEx(self) -> "(iiayqs)":
        """Get CurrentDNSServerEx."""
        return [0, 2, bytes([127, 0, 0, 1]), 0, ""]

    @dbus_property(access=PropertyAccess.READ)
    def Domains(self) -> "a(isb)":
        """Get Domains."""
        return [[0, "local.hass.io", False]]

    @dbus_property(access=PropertyAccess.READ)
    def TransactionStatistics(self) -> "(tt)":
        """Get TransactionStatistics."""
        return [0, 100000]

    @dbus_property(access=PropertyAccess.READ)
    def CacheStatistics(self) -> "(ttt)":
        """Get CacheStatistics."""
        return [10, 50000, 10000]

    @dbus_property(access=PropertyAccess.READ)
    def DNSSEC(self) -> "s":
        """Get DNSSEC."""
        return "no"

    @dbus_property(access=PropertyAccess.READ)
    def DNSSECStatistics(self) -> "(tttt)":
        """Get DNSSECStatistics."""
        return [0, 0, 0, 0]

    @dbus_property(access=PropertyAccess.READ)
    def DNSSECSupported(self) -> "b":
        """Get DNSSECSupported."""
        return False

    @dbus_property(access=PropertyAccess.READ)
    def DNSSECNegativeTrustAnchors(self) -> "as":
        """Get DNSSECNegativeTrustAnchors."""
        return ["168.192.in-addr.arpa", "local"]

    @dbus_property(access=PropertyAccess.READ)
    def DNSStubListener(self) -> "s":
        """Get DNSStubListener."""
        return "no"

    @dbus_property(access=PropertyAccess.READ)
    def ResolvConfMode(self) -> "s":
        """Get ResolvConfMode."""
        return "foreign"
