"""Mock of Network Manager Device service."""

from ctypes import c_uint32
from dataclasses import dataclass

from dbus_fast import Variant
from dbus_fast.service import PropertyAccess, dbus_property, signal

from .base import DBusServiceMock, dbus_method

BUS_NAME = "org.freedesktop.NetworkManager"
ETHERNET_DEVICE_OBJECT_PATH = "/org/freedesktop/NetworkManager/Devices/1"
WIRELESS_DEVICE_OBJECT_PATH = "/org/freedesktop/NetworkManager/Devices/3"
DEFAULT_OBJECT_PATH = ETHERNET_DEVICE_OBJECT_PATH


def setup(object_path: str | None = None) -> DBusServiceMock:
    """Create dbus mock object."""
    return Device(object_path if object_path else DEFAULT_OBJECT_PATH)


@dataclass(slots=True)
class DeviceFixture:
    """Device fixture."""

    Udi: str
    Path: str
    Interface: str
    IpInterface: str
    Driver: str
    DriverVersion: str
    FirmwareVersion: str
    Capabilities: c_uint32
    Ip4Address: c_uint32
    State: c_uint32
    StateReason: list[c_uint32]
    ActiveConnection: str
    Ip4Config: str
    Dhcp4Config: str
    Ip6Config: str
    Dhcp6Config: str
    Managed: bool
    Autoconnect: bool
    FirmwareMissing: bool
    NmPluginMissing: bool
    DeviceType: c_uint32
    AvailableConnections: list[str]
    PhysicalPortId: str
    Mtu: c_uint32
    Metered: c_uint32
    LldpNeighbors: list[dict[str, Variant]]
    Real: bool
    Ip4Connectivity: c_uint32
    Ip6Connectivity: c_uint32
    InterfaceFlags: c_uint32
    HwAddress: str
    Ports: list[str]


FIXTURES: dict[str, DeviceFixture] = {
    "/org/freedesktop/NetworkManager/Devices/1": DeviceFixture(
        Udi="/sys/devices/pci0000:00/0000:00:1f.6/net/eth0",
        Path="platform-ff3f0000.ethernet",
        Interface="eth0",
        IpInterface="eth0",
        Driver="e1000e",
        DriverVersion="3.2.6-k",
        FirmwareVersion="0.7-4",
        Capabilities=3,
        Ip4Address=2499979456,
        State=100,
        StateReason=[100, 0],
        ActiveConnection="/org/freedesktop/NetworkManager/ActiveConnection/1",
        Ip4Config="/org/freedesktop/NetworkManager/IP4Config/1",
        Dhcp4Config="/org/freedesktop/NetworkManager/DHCP4Config/1",
        Ip6Config="/org/freedesktop/NetworkManager/IP6Config/1",
        Dhcp6Config="/",
        Managed=True,
        Autoconnect=True,
        FirmwareMissing=False,
        NmPluginMissing=False,
        DeviceType=1,
        AvailableConnections=["/org/freedesktop/NetworkManager/Settings/1"],
        PhysicalPortId="",
        Mtu=1500,
        Metered=4,
        LldpNeighbors=[],
        Real=True,
        Ip4Connectivity=4,
        Ip6Connectivity=3,
        InterfaceFlags=65539,
        HwAddress="AA:BB:CC:DD:EE:FF",
        Ports=[],
    ),
    "/org/freedesktop/NetworkManager/Devices/3": DeviceFixture(
        Udi="/sys/devices/platform/soc/fe300000.mmcnr/mmc_host/mmc1/mmc1:0001/mmc1:0001:1/net/wlan0",
        Path="platform.fe300000.mmcnr",
        Interface="wlan0",
        IpInterface="",
        Driver="brcmfmac",
        DriverVersion="7.45.154",
        FirmwareVersion="01-4fbe0b04",
        Capabilities=1,
        Ip4Address=0,
        State=30,
        StateReason=[30, 42],
        ActiveConnection="/",
        Ip4Config="/",
        Dhcp4Config="/",
        Ip6Config="/",
        Dhcp6Config="/",
        Managed=True,
        Autoconnect=True,
        FirmwareMissing=False,
        NmPluginMissing=False,
        DeviceType=2,
        AvailableConnections=["/org/freedesktop/NetworkManager/Settings/3"],
        PhysicalPortId="",
        Mtu=1500,
        Metered=0,
        LldpNeighbors=[],
        Real=True,
        Ip4Connectivity=1,
        Ip6Connectivity=1,
        InterfaceFlags=65539,
        HwAddress="FF:EE:DD:CC:BB:AA",
        Ports=[],
    ),
    "/org/freedesktop/NetworkManager/Devices/4": DeviceFixture(
        Udi="/sys/devices/pci0000:00/0000:00:1f.6/net/eth0",
        Path="platform-ff3f0000.ethernet",
        Interface="eth0",
        IpInterface="eth0",
        Driver="e1000e",
        DriverVersion="3.2.6-k",
        FirmwareVersion="0.7-4",
        Capabilities=3,
        Ip4Address=2499979456,
        State=100,
        StateReason=[100, 0],
        ActiveConnection="/org/freedesktop/NetworkManager/ActiveConnection/2",
        Ip4Config="/org/freedesktop/NetworkManager/IP4Config/1",
        Dhcp4Config="/org/freedesktop/NetworkManager/DHCP4Config/1",
        Ip6Config="/org/freedesktop/NetworkManager/IP6Config/1",
        Dhcp6Config="/",
        Managed=True,
        Autoconnect=True,
        FirmwareMissing=False,
        NmPluginMissing=False,
        DeviceType=1,
        AvailableConnections=["/org/freedesktop/NetworkManager/Settings/2"],
        PhysicalPortId="",
        Mtu=1500,
        Metered=4,
        LldpNeighbors=[],
        Real=True,
        Ip4Connectivity=4,
        Ip6Connectivity=3,
        InterfaceFlags=65539,
        HwAddress="A1:B2:C3:D4:E5:F6",
        Ports=[],
    ),
    "/org/freedesktop/NetworkManager/Devices/5": DeviceFixture(
        Udi="/sys/devices/pci0000:00/0000:00:1f.6/net/en0",
        Path="platform-ff3f0000.ethernet",
        Interface="en0",
        IpInterface="en0",
        Driver="e1000e",
        DriverVersion="3.2.6-k",
        FirmwareVersion="0.7-4",
        Capabilities=3,
        Ip4Address=2499979456,
        State=100,
        StateReason=[100, 0],
        ActiveConnection="/org/freedesktop/NetworkManager/ActiveConnection/2",
        Ip4Config="/org/freedesktop/NetworkManager/IP4Config/1",
        Dhcp4Config="/org/freedesktop/NetworkManager/DHCP4Config/1",
        Ip6Config="/org/freedesktop/NetworkManager/IP6Config/1",
        Dhcp6Config="/",
        Managed=True,
        Autoconnect=True,
        FirmwareMissing=False,
        NmPluginMissing=False,
        DeviceType=1,
        AvailableConnections=["/org/freedesktop/NetworkManager/Settings/2"],
        PhysicalPortId="",
        Mtu=1500,
        Metered=4,
        LldpNeighbors=[],
        Real=True,
        Ip4Connectivity=4,
        Ip6Connectivity=3,
        InterfaceFlags=65539,
        HwAddress="AA:BB:CC:DD:EE:FF",
        Ports=[],
    ),
    "/org/freedesktop/NetworkManager/Devices/35": DeviceFixture(
        Udi="/sys/devices/virtual/net/veth87bd238'",
        Path="",
        Interface="veth87bd238",
        IpInterface="veth87bd238",
        Driver="veth",
        DriverVersion="1.0",
        FirmwareVersion="",
        Capabilities=7,
        Ip4Address=0,
        State=10,
        StateReason=[10, 0],
        ActiveConnection="/",
        Ip4Config="/",
        Dhcp4Config="/",
        Ip6Config="/",
        Dhcp6Config="/",
        Managed=False,
        Autoconnect=True,
        FirmwareMissing=False,
        NmPluginMissing=False,
        DeviceType=20,
        AvailableConnections=[],
        PhysicalPortId="",
        Mtu=1500,
        Metered=0,
        LldpNeighbors=[],
        Real=True,
        Ip4Connectivity=0,
        Ip6Connectivity=0,
        InterfaceFlags=65539,
        HwAddress="9A:4B:E3:9A:F8:D3",
        Ports=[],
    ),
}


class Device(DBusServiceMock):
    """Device mock.

    gdbus introspect --system --dest org.freedesktop.NetworkManager --object-path /org/freedesktop/NetworkManager/Devices/1
    """

    interface = "org.freedesktop.NetworkManager.Device"

    def __init__(self, object_path: str):
        """Initialize object."""
        super().__init__()
        self.object_path = object_path
        self.fixture: DeviceFixture = FIXTURES[object_path]

    @dbus_property(access=PropertyAccess.READ)
    def Udi(self) -> "s":
        """Get Udi."""
        return self.fixture.Udi

    @dbus_property(access=PropertyAccess.READ)
    def Path(self) -> "s":
        """Get Path."""
        return self.fixture.Path

    @dbus_property(access=PropertyAccess.READ)
    def Interface(self) -> "s":
        """Get Interface."""
        return self.fixture.Interface

    @dbus_property(access=PropertyAccess.READ)
    def IpInterface(self) -> "s":
        """Get IpInterface."""
        return self.fixture.IpInterface

    @dbus_property(access=PropertyAccess.READ)
    def Driver(self) -> "s":
        """Get Driver."""
        return self.fixture.Driver

    @dbus_property(access=PropertyAccess.READ)
    def DriverVersion(self) -> "s":
        """Get DriverVersion."""
        return self.fixture.DriverVersion

    @dbus_property(access=PropertyAccess.READ)
    def FirmwareVersion(self) -> "s":
        """Get FirmwareVersion."""
        return self.fixture.FirmwareVersion

    @dbus_property(access=PropertyAccess.READ)
    def Capabilities(self) -> "u":
        """Get Capabilities."""
        return self.fixture.Capabilities

    @dbus_property(access=PropertyAccess.READ)
    def Ip4Address(self) -> "u":
        """Get Ip4Address."""
        return self.fixture.Ip4Address

    @dbus_property(access=PropertyAccess.READ)
    def State(self) -> "u":
        """Get State."""
        return self.fixture.State

    @dbus_property(access=PropertyAccess.READ)
    def StateReason(self) -> "(uu)":
        """Get StateReason."""
        return self.fixture.StateReason

    @dbus_property(access=PropertyAccess.READ)
    def ActiveConnection(self) -> "o":
        """Get ActiveConnection."""
        return self.fixture.ActiveConnection

    @dbus_property(access=PropertyAccess.READ)
    def Ip4Config(self) -> "o":
        """Get Ip4Config."""
        return self.fixture.Ip4Config

    @dbus_property(access=PropertyAccess.READ)
    def Dhcp4Config(self) -> "o":
        """Get Dhcp4Config."""
        return self.fixture.Dhcp4Config

    @dbus_property(access=PropertyAccess.READ)
    def Ip6Config(self) -> "o":
        """Get Ip6Config."""
        return self.fixture.Ip6Config

    @dbus_property(access=PropertyAccess.READ)
    def Dhcp6Config(self) -> "o":
        """Get Dhcp6Config."""
        return self.fixture.Dhcp6Config

    @dbus_property()
    def Managed(self) -> "b":
        """Get Managed."""
        return self.fixture.Managed

    @Managed.setter
    def Managed(self, value: "b"):
        """Set Managed."""
        self.emit_properties_changed({"Managed": value})

    @dbus_property()
    def Autoconnect(self) -> "b":
        """Get Autoconnect."""
        return self.fixture.Autoconnect

    @Autoconnect.setter
    def Autoconnect(self, value: "b"):
        """Set Autoconnect."""
        self.emit_properties_changed({"Autoconnect": value})

    @dbus_property(access=PropertyAccess.READ)
    def FirmwareMissing(self) -> "b":
        """Get FirmwareMissing."""
        return self.fixture.FirmwareMissing

    @dbus_property(access=PropertyAccess.READ)
    def NmPluginMissing(self) -> "b":
        """Get NmPluginMissing."""
        return self.fixture.NmPluginMissing

    @dbus_property(access=PropertyAccess.READ)
    def DeviceType(self) -> "u":
        """Get DeviceType."""
        return self.fixture.DeviceType

    @dbus_property(access=PropertyAccess.READ)
    def AvailableConnections(self) -> "ao":
        """Get AvailableConnections."""
        return self.fixture.AvailableConnections

    @dbus_property(access=PropertyAccess.READ)
    def PhysicalPortId(self) -> "s":
        """Get PhysicalPortId."""
        return self.fixture.PhysicalPortId

    @dbus_property(access=PropertyAccess.READ)
    def Mtu(self) -> "u":
        """Get Mtu."""
        return self.fixture.Mtu

    @dbus_property(access=PropertyAccess.READ)
    def Metered(self) -> "u":
        """Get Metered."""
        return self.fixture.Metered

    @dbus_property(access=PropertyAccess.READ)
    def LldpNeighbors(self) -> "aa{sv}":
        """Get LldpNeighbors."""
        return self.fixture.LldpNeighbors

    @dbus_property(access=PropertyAccess.READ)
    def Real(self) -> "b":
        """Get Real."""
        return self.fixture.Real

    @dbus_property(access=PropertyAccess.READ)
    def Ip4Connectivity(self) -> "u":
        """Get Ip4Connectivity."""
        return self.fixture.Ip4Connectivity

    @dbus_property(access=PropertyAccess.READ)
    def Ip6Connectivity(self) -> "u":
        """Get Ip6Connectivity."""
        return self.fixture.Ip6Connectivity

    @dbus_property(access=PropertyAccess.READ)
    def InterfaceFlags(self) -> "u":
        """Get InterfaceFlags."""
        return self.fixture.InterfaceFlags

    @dbus_property(access=PropertyAccess.READ)
    def HwAddress(self) -> "s":
        """Get HwAddress."""
        return self.fixture.HwAddress

    @dbus_property(access=PropertyAccess.READ)
    def Ports(self) -> "ao":
        """Get Ports."""
        return self.fixture.Ports

    @signal()
    def StateChanged(self) -> "uuu":
        """Signal StateChanged."""
        return [120, 100, 1]

    @dbus_method()
    def Reapply(self, connection: "a{sa{sv}}", version_id: "t", flags: "u") -> None:
        """Do Reapply method."""

    @dbus_method()
    def GetAppliedConnection(self, flags: "u") -> "a{sa{sv}}t":
        """Do GetAppliedConnection method."""
        return [{}, 0]

    @dbus_method()
    def Disconnect(self) -> None:
        """Do Disconnect method."""

    @dbus_method()
    def Delete(self) -> None:
        """Do Delete method."""
