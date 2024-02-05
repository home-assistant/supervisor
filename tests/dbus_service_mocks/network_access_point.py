"""Mock of Network Manager Access Point service."""

from ctypes import c_byte, c_int32, c_uint32
from dataclasses import dataclass

from dbus_fast.service import PropertyAccess, dbus_property

from .base import DBusServiceMock

BUS_NAME = "org.freedesktop.NetworkManager"
DEFAULT_OBJECT_PATH = "/org/freedesktop/NetworkManager/AccessPoint/43099"


def setup(object_path: str | None = None) -> DBusServiceMock:
    """Create dbus mock object."""
    return AccessPoint(object_path if object_path else DEFAULT_OBJECT_PATH)


@dataclass(slots=True)
class AccessPointFixture:
    """Access Point fixture."""

    Flags: c_uint32
    WpaFlags: c_uint32
    RsnFlags: c_uint32
    Ssid: bytes
    Frequency: c_uint32
    HwAddress: str
    Mode: c_uint32
    MaxBitrate: c_uint32
    Strength: c_byte
    LastSeen: c_int32


FIXTURES: dict[str, AccessPointFixture] = {
    "/org/freedesktop/NetworkManager/AccessPoint/43099": AccessPointFixture(
        Flags=3,
        WpaFlags=0,
        RsnFlags=392,
        Ssid=b"UPC4814466",
        Frequency=2462,
        HwAddress="E4:57:40:A9:D7:DE",
        Mode=2,
        MaxBitrate=195000,
        Strength=47,
        LastSeen=1398776,
    ),
    "/org/freedesktop/NetworkManager/AccessPoint/43100": AccessPointFixture(
        Flags=1,
        WpaFlags=0,
        RsnFlags=392,
        Ssid=b"VQ@35(55720",
        Frequency=5660,
        HwAddress="18:4B:0D:23:A1:9C",
        Mode=2,
        MaxBitrate=540000,
        Strength=63,
        LastSeen=1398839,
    ),
}


class AccessPoint(DBusServiceMock):
    """Access Point mock.

    gdbus introspect --system --dest org.freedesktop.NetworkManager --object-path /org/freedesktop/NetworkManager/AccessPoint/1
    """

    interface = "org.freedesktop.NetworkManager.AccessPoint"

    def __init__(self, object_path: str):
        """Initialize object."""
        super().__init__()
        self.object_path = object_path
        self.fixture: AccessPointFixture = FIXTURES[object_path]

    @dbus_property(access=PropertyAccess.READ)
    def Flags(self) -> "u":
        """Get Flags."""
        return self.fixture.Flags

    @dbus_property(access=PropertyAccess.READ)
    def WpaFlags(self) -> "u":
        """Get WpaFlags."""
        return self.fixture.WpaFlags

    @dbus_property(access=PropertyAccess.READ)
    def RsnFlags(self) -> "u":
        """Get RsnFlags."""
        return self.fixture.RsnFlags

    @dbus_property(access=PropertyAccess.READ)
    def Ssid(self) -> "ay":
        """Get Ssid."""
        return self.fixture.Ssid

    @dbus_property(access=PropertyAccess.READ)
    def Frequency(self) -> "u":
        """Get Frequency."""
        return self.fixture.Frequency

    @dbus_property(access=PropertyAccess.READ)
    def HwAddress(self) -> "s":
        """Get HwAddress."""
        return self.fixture.HwAddress

    @dbus_property(access=PropertyAccess.READ)
    def Mode(self) -> "u":
        """Get Mode."""
        return self.fixture.Mode

    @dbus_property(access=PropertyAccess.READ)
    def MaxBitrate(self) -> "u":
        """Get MaxBitrate."""
        return self.fixture.MaxBitrate

    @dbus_property(access=PropertyAccess.READ)
    def Strength(self) -> "y":
        """Get Strength."""
        return self.fixture.Strength

    @dbus_property(access=PropertyAccess.READ)
    def LastSeen(self) -> "i":
        """Get LastSeen."""
        return self.fixture.LastSeen
