"""Mock of Network Manager IP6Config service."""

from dbus_fast import Variant
from dbus_fast.service import PropertyAccess, dbus_property

from .base import DBusServiceMock

BUS_NAME = "org.freedesktop.NetworkManager"


def setup(object_path: str | None = None) -> DBusServiceMock:
    """Create dbus mock object."""
    return IP6Config()


class IP6Config(DBusServiceMock):
    """IP6Config mock.

    gdbus introspect --system --dest org.freedesktop.NetworkManager --object-path /org/freedesktop/NetworkManager/IP6Config/1
    """

    interface = "org.freedesktop.NetworkManager.IP6Config"
    object_path = "/org/freedesktop/NetworkManager/IP6Config/1"

    @dbus_property(access=PropertyAccess.READ)
    def Addresses(self) -> "a(ayuay)":
        """Get Addresses."""
        return [
            [
                bytes(
                    [
                        0x2A,
                        0x3,
                        0x1,
                        0x69,
                        0x3D,
                        0xF5,
                        0x0,
                        0x0,
                        0x6B,
                        0xE9,
                        0x25,
                        0x88,
                        0xB2,
                        0x6A,
                        0xA6,
                        0x79,
                    ]
                ),
                64,
                bytes(
                    [
                        0xFE,
                        0x80,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0xDA,
                        0x58,
                        0xD7,
                        0xFF,
                        0xFE,
                        0x0,
                        0x9C,
                        0x69,
                    ]
                ),
            ],
            [
                bytes(
                    [
                        0x2A,
                        0x3,
                        0x1,
                        0x69,
                        0x3D,
                        0xF5,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x2,
                        0xF1,
                    ]
                ),
                128,
                bytes(
                    [
                        0xFE,
                        0x80,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0xDA,
                        0x58,
                        0xD7,
                        0xFF,
                        0xFE,
                        0x0,
                        0x9C,
                        0x69,
                    ]
                ),
            ],
        ]

    @dbus_property(access=PropertyAccess.READ)
    def AddressData(self) -> "aa{sv}":
        """Get AddressData."""
        return [
            {
                "address": Variant("s", "2a03:169:3df5:0:6be9:2588:b26a:a679"),
                "prefix": Variant("u", 64),
            },
            {
                "address": Variant("s", "2a03:169:3df5::2f1"),
                "prefix": Variant("u", 128),
            },
        ]

    @dbus_property(access=PropertyAccess.READ)
    def Gateway(self) -> "s":
        """Get Gateway."""
        return "fe80::da58:d7ff:fe00:9c69"

    @dbus_property(access=PropertyAccess.READ)
    def Routes(self) -> "a(ayuayu)":
        """Get Routes."""
        return [
            [
                bytes(
                    [
                        0xFD,
                        0x14,
                        0x94,
                        0x9B,
                        0xC9,
                        0xCC,
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
                    ]
                ),
                48,
                bytes(
                    [
                        0xFE,
                        0x80,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0xDA,
                        0x58,
                        0xD7,
                        0xFF,
                        0xFE,
                        0x0,
                        0x9C,
                        0x69,
                    ]
                ),
                100,
            ],
            [
                bytes(
                    [
                        0x2A,
                        0x3,
                        0x1,
                        0x69,
                        0x3D,
                        0xF5,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x0,
                        0x2,
                        0xF1,
                    ]
                ),
                128,
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
                        0x0,
                    ]
                ),
                100,
            ],
            [
                bytes(
                    [
                        0xFE,
                        0x80,
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
                    ]
                ),
                64,
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
                        0x0,
                    ]
                ),
                100,
            ],
        ]

    @dbus_property(access=PropertyAccess.READ)
    def RouteData(self) -> "aa{sv}":
        """Get RouteData."""
        return [
            {
                "dest": Variant("s", "fd14:949b:c9cc::"),
                "prefix": Variant("u", 48),
                "next-hop": Variant("s", "fe80::da58:d7ff:fe00:9c69"),
                "metric": Variant("u", 100),
            },
            {
                "dest": Variant("s", "2a03:169:3df5::2f1"),
                "prefix": Variant("u", 128),
                "metric": Variant("u", 100),
            },
            {
                "dest": Variant("s", "fe80::"),
                "prefix": Variant("u", 64),
                "metric": Variant("u", 100),
            },
            {
                "dest": Variant("s", "ff00::"),
                "prefix": Variant("u", 8),
                "metric": Variant("u", 256),
                "table": Variant("u", 255),
            },
        ]

    @dbus_property(access=PropertyAccess.READ)
    def Nameservers(self) -> "aay":
        """Get Nameservers."""
        return [
            bytes(
                [
                    0x20,
                    0x1,
                    0x16,
                    0x20,
                    0x27,
                    0x77,
                    0x0,
                    0x1,
                    0x0,
                    0x0,
                    0x0,
                    0x0,
                    0x0,
                    0x0,
                    0x0,
                    0x10,
                ]
            ),
            bytes(
                [
                    0x20,
                    0x1,
                    0x16,
                    0x20,
                    0x27,
                    0x77,
                    0x0,
                    0x2,
                    0x0,
                    0x0,
                    0x0,
                    0x0,
                    0x0,
                    0x0,
                    0x0,
                    0x20,
                ]
            ),
        ]

    @dbus_property(access=PropertyAccess.READ)
    def Domains(self) -> "as":
        """Get Domains."""
        return []

    @dbus_property(access=PropertyAccess.READ)
    def Searches(self) -> "as":
        """Get Searches."""
        return []

    @dbus_property(access=PropertyAccess.READ)
    def DnsOptions(self) -> "as":
        """Get DnsOptions."""
        return []

    @dbus_property(access=PropertyAccess.READ)
    def DnsPriority(self) -> "i":
        """Get DnsPriority."""
        return 100
