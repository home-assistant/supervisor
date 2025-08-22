"""Mock of Network Manager Device VLAN service."""

from dbus_fast.service import PropertyAccess, dbus_property

from .base import DBusServiceMock
from .network_device import FIXTURES

BUS_NAME = "org.freedesktop.NetworkManager"
VLAN_DEVICE_OBJECT_PATH = "/org/freedesktop/NetworkManager/Devices/38"
DEFAULT_OBJECT_PATH = VLAN_DEVICE_OBJECT_PATH


def setup(object_path: str | None = None) -> DBusServiceMock:
    """Create dbus mock object."""
    return DeviceVlan(object_path if object_path else DEFAULT_OBJECT_PATH)


class DeviceVlan(DBusServiceMock):
    """Device VLAN mock.

    gdbus introspect --system --dest org.freedesktop.NetworkManager --object-path /org/freedesktop/NetworkManager/Devices/38
    """

    interface = "org.freedesktop.NetworkManager.Device.Vlan"

    def __init__(self, object_path: str):
        """Initialize object."""
        super().__init__()
        self.object_path = object_path
        self.fixture = FIXTURES[object_path]

    @dbus_property(access=PropertyAccess.READ)
    def HwAddress(self) -> "s":
        """Get HwAddress."""
        return self.fixture.HwAddress

    @dbus_property(access=PropertyAccess.READ)
    def Carrier(self) -> "b":
        """Get Carrier."""
        return True

    @dbus_property(access=PropertyAccess.READ)
    def Parent(self) -> "o":
        """Get Parent."""
        return self.fixture.Parent

    @dbus_property(access=PropertyAccess.READ)
    def VlanId(self) -> "u":
        """Get VlanId."""
        return self.fixture.VlanId
