"""Mock of Network Manager Active Connection service."""

from dataclasses import dataclass, field

from dbus_fast.service import PropertyAccess, dbus_property, signal

from .base import DBusServiceMock

BUS_NAME = "org.freedesktop.NetworkManager"
DEFAULT_OBJECT_PATH = "/org/freedesktop/NetworkManager/ActiveConnection/1"


def setup(object_path: str | None = None) -> DBusServiceMock:
    """Create dbus mock object."""
    return ActiveConnection(object_path if object_path else DEFAULT_OBJECT_PATH)


@dataclass(slots=True)
class ActiveConnectionFixture:
    """Active Connection fixture."""

    connection: str = "/org/freedesktop/NetworkManager/Settings/1"
    specific_object: str = "/"
    id: str = "Wired connection 1"
    uuid: str = "0c23631e-2118-355c-bbb0-8943229cb0d6"
    type: str = "802-3-ethernet"
    devices: list[str] = field(
        default_factory=lambda: ["/org/freedesktop/NetworkManager/Devices/1"]
    )
    state: int = 2
    state_flags: int = 92
    default: bool = True
    ip4_config: str = "/org/freedesktop/NetworkManager/IP4Config/1"
    dhcp4_config: str = "/org/freedesktop/NetworkManager/DHCP4Config/1"
    default6: bool = False
    ip6_config: str = "/org/freedesktop/NetworkManager/IP6Config/1"
    dhcp6_config: str = "/"
    vpn: bool = False
    master: str = "/"


FIXTURES: dict[str, ActiveConnectionFixture] = {
    DEFAULT_OBJECT_PATH: ActiveConnectionFixture(),
    "/org/freedesktop/NetworkManager/ActiveConnection/2": ActiveConnectionFixture(
        connection="/org/freedesktop/NetworkManager/Settings/2",
        devices=[
            "/org/freedesktop/NetworkManager/Devices/4",
            "/org/freedesktop/NetworkManager/Devices/5",
        ],
    ),
    "/org/freedesktop/NetworkManager/ActiveConnection/3": ActiveConnectionFixture(
        connection="/org/freedesktop/NetworkManager/Settings/3",
        devices=[
            "/org/freedesktop/NetworkManager/Devices/3",
        ],
    ),
}


class ActiveConnection(DBusServiceMock):
    """Active Connection mock.

    gdbus introspect --system --dest org.freedesktop.NetworkManager --object-path /org/freedesktop/NetworkManager/ActiveConnection/1
    """

    interface = "org.freedesktop.NetworkManager.Connection.Active"
    object_path = "/org/freedesktop/NetworkManager/ActiveConnection/1"

    def __init__(self, object_path: str):
        """Initialize object."""
        super().__init__()
        self.object_path = object_path
        self.fixture = FIXTURES[object_path]

    @dbus_property(access=PropertyAccess.READ)
    def Connection(self) -> "o":
        """Get Connection."""
        return self.fixture.connection

    @dbus_property(access=PropertyAccess.READ)
    def SpecificObject(self) -> "o":
        """Get SpecificObject."""
        return self.fixture.specific_object

    @dbus_property(access=PropertyAccess.READ)
    def Id(self) -> "s":
        """Get Id."""
        return self.fixture.id

    @dbus_property(access=PropertyAccess.READ)
    def Uuid(self) -> "s":
        """Get Uuid."""
        return self.fixture.uuid

    @dbus_property(access=PropertyAccess.READ)
    def Type(self) -> "s":
        """Get Type."""
        return self.fixture.type

    @dbus_property(access=PropertyAccess.READ)
    def Devices(self) -> "ao":
        """Get Devices."""
        return self.fixture.devices

    @dbus_property(access=PropertyAccess.READ)
    def State(self) -> "u":
        """Get State."""
        return self.fixture.state

    @dbus_property(access=PropertyAccess.READ)
    def StateFlags(self) -> "u":
        """Get StateFlags."""
        return self.fixture.state_flags

    @dbus_property(access=PropertyAccess.READ)
    def Default(self) -> "b":
        """Get Default."""
        return self.fixture.default

    @dbus_property(access=PropertyAccess.READ)
    def Ip4Config(self) -> "o":
        """Get Ip4Config."""
        return self.fixture.ip4_config

    @dbus_property(access=PropertyAccess.READ)
    def Dhcp4Config(self) -> "o":
        """Get Dhcp4Config."""
        return self.fixture.dhcp4_config

    @dbus_property(access=PropertyAccess.READ)
    def Default6(self) -> "b":
        """Get Default6."""
        return self.fixture.default6

    @dbus_property(access=PropertyAccess.READ)
    def Ip6Config(self) -> "o":
        """Get Ip6Config."""
        return self.fixture.ip6_config

    @dbus_property(access=PropertyAccess.READ)
    def Dhcp6Config(self) -> "o":
        """Get Dhcp6Config."""
        return self.fixture.dhcp6_config

    @dbus_property(access=PropertyAccess.READ)
    def Vpn(self) -> "b":
        """Get Vpn."""
        return self.fixture.vpn

    @dbus_property(access=PropertyAccess.READ)
    def Master(self) -> "o":
        """Get Master."""
        return self.fixture.master

    @signal()
    def StateChanged(self) -> "uu":
        """Signal StateChanged."""
        return [2, 0]
