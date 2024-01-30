"""Mock of UDisks2 Drive service."""

from ctypes import c_int32, c_uint32, c_uint64
from dataclasses import dataclass

from dbus_fast import Variant
from dbus_fast.service import PropertyAccess, dbus_property

from .base import DBusServiceMock, dbus_method

BUS_NAME = "org.freedesktop.UDisks2"
DEFAULT_OBJECT_PATH = "/org/freedesktop/UDisks2/drives/SSK_SSK_Storage_DF56419883D56"


def setup(object_path: str | None = None) -> DBusServiceMock:
    """Create dbus mock object."""
    return Drive(object_path if object_path else DEFAULT_OBJECT_PATH)


@dataclass(slots=True)
class DriveFixture:
    """Drive fixture."""

    Vendor: str
    Model: str
    Revision: str
    Serial: str
    WWN: str
    Id: str
    Configuration: dict[str, Variant]
    Media: str
    MediaCompatibility: list[str]
    MediaRemovable: bool
    MediaAvailable: bool
    MediaChangeDetected: bool
    Size: c_uint64
    TimeDetected: c_uint64
    TimeMediaDetected: c_uint64
    Optical: bool
    OpticalBlank: bool
    OpticalNumTracks: c_uint32
    OpticalNumAudioTracks: c_uint32
    OpticalNumDataTracks: c_uint32
    OpticalNumSessions: c_uint32
    RotationRate: c_int32
    ConnectionBus: str
    Seat: str
    Removable: bool
    Ejectable: bool
    SortKey: str
    CanPowerOff: bool
    SiblingId: str


FIXTURES: dict[str, DriveFixture] = {
    "/org/freedesktop/UDisks2/drives/BJTD4R_0x97cde291": DriveFixture(
        Vendor="",
        Model="BJTD4R",
        Revision="",
        Serial="0x97cde291",
        WWN="",
        Id="BJTD4R-0x97cde291",
        Configuration={},
        Media="flash_mmc",
        MediaCompatibility=["flash_mmc"],
        MediaRemovable=False,
        MediaAvailable=True,
        MediaChangeDetected=True,
        Size=31268536320,
        TimeDetected=1673981760067475,
        TimeMediaDetected=1673981760067475,
        Optical=False,
        OpticalBlank=False,
        OpticalNumTracks=0,
        OpticalNumAudioTracks=0,
        OpticalNumDataTracks=0,
        OpticalNumSessions=0,
        RotationRate=0,
        ConnectionBus="sdio",
        Seat="seat0",
        Removable=False,
        Ejectable=False,
        SortKey="00coldplug/00fixed/mmcblk1",
        CanPowerOff=False,
        SiblingId="",
    ),
    "/org/freedesktop/UDisks2/drives/Generic_Flash_Disk_61BCDDB6": DriveFixture(
        Vendor="Generic",
        Model="Flash Disk",
        Revision="8.07",
        Serial="61BCDDB6",
        WWN="",
        Id="Generic-Flash-Disk-61BCDDB6",
        Configuration={},
        Media="",
        MediaCompatibility=[],
        MediaRemovable=True,
        MediaAvailable=True,
        MediaChangeDetected=True,
        Size=8054112256,
        TimeDetected=1675972756688073,
        TimeMediaDetected=1675972756688073,
        Optical=False,
        OpticalBlank=False,
        OpticalNumTracks=0,
        OpticalNumAudioTracks=0,
        OpticalNumDataTracks=0,
        OpticalNumSessions=0,
        RotationRate=-1,
        ConnectionBus="usb",
        Seat="seat0",
        Removable=True,
        Ejectable=True,
        SortKey="01hotplug/1675972756688073",
        CanPowerOff=True,
        SiblingId="/sys/devices/platform/soc/ffe09000.usb/ff500000.usb/xhci-hcd.1.auto/usb1/1-1/1-1.2/1-1.2:1.0",
    ),
    "/org/freedesktop/UDisks2/drives/SSK_SSK_Storage_DF56419883D56": DriveFixture(
        Vendor="SSK",
        Model="SSK Storage",
        Revision="0206",
        Serial="DF56419883D56",
        WWN="",
        Id="SSK-SSK-Storage-DF56419883D56",
        Configuration={},
        Media="",
        MediaCompatibility=[],
        MediaRemovable=False,
        MediaAvailable=True,
        MediaChangeDetected=True,
        Size=250059350016,
        TimeDetected=1675897304240492,
        TimeMediaDetected=1675897304240492,
        Optical=False,
        OpticalBlank=False,
        OpticalNumTracks=0,
        OpticalNumAudioTracks=0,
        OpticalNumDataTracks=0,
        OpticalNumSessions=0,
        RotationRate=0,
        ConnectionBus="usb",
        Seat="seat0",
        Removable=True,
        Ejectable=False,
        SortKey="01hotplug/1675897304240492",
        CanPowerOff=True,
        SiblingId="/sys/devices/platform/soc/ffe09000.usb/ff500000.usb/xhci-hcd.1.auto/usb2/2-1/2-1.4/2-1.4:1.0",
    ),
    "/org/freedesktop/UDisks2/drives/Test_Multiple_Partition_Tables_123456789": DriveFixture(
        Vendor="Test",
        Model="Multiple Partition Tables",
        Revision="",
        Serial="123456789",
        WWN="",
        Id="Test-Multiple-Partition-Tables-123456789",
        Configuration={},
        Media="",
        MediaCompatibility=[],
        MediaRemovable=False,
        MediaAvailable=True,
        MediaChangeDetected=True,
        Size=0,
        TimeDetected=0,
        TimeMediaDetected=0,
        Optical=False,
        OpticalBlank=False,
        OpticalNumTracks=0,
        OpticalNumAudioTracks=0,
        OpticalNumDataTracks=0,
        OpticalNumSessions=0,
        RotationRate=0,
        ConnectionBus="usb",
        Seat="seat0",
        Removable=True,
        Ejectable=False,
        SortKey="",
        CanPowerOff=True,
        SiblingId="",
    ),
}


class Drive(DBusServiceMock):
    """Drive mock.

    gdbus introspect --system --dest org.freedesktop.UDisks2 --object-path /org/freedesktop/UDisks2/drives/id
    """

    interface = "org.freedesktop.UDisks2.Drive"

    def __init__(self, object_path: str):
        """Initialize object."""
        super().__init__()
        self.object_path = object_path
        self.fixture: DriveFixture = FIXTURES[object_path]

    @dbus_property(access=PropertyAccess.READ)
    def Vendor(self) -> "s":
        """Get Vendor."""
        return self.fixture.Vendor

    @dbus_property(access=PropertyAccess.READ)
    def Model(self) -> "s":
        """Get Model."""
        return self.fixture.Model

    @dbus_property(access=PropertyAccess.READ)
    def Revision(self) -> "s":
        """Get Revision."""
        return self.fixture.Revision

    @dbus_property(access=PropertyAccess.READ)
    def Serial(self) -> "s":
        """Get Serial."""
        return self.fixture.Serial

    @dbus_property(access=PropertyAccess.READ)
    def WWN(self) -> "s":
        """Get WWN."""
        return self.fixture.WWN

    @dbus_property(access=PropertyAccess.READ)
    def Id(self) -> "s":
        """Get Id."""
        return self.fixture.Id

    @dbus_property(access=PropertyAccess.READ)
    def Configuration(self) -> "a{sv}":
        """Get Configuration."""
        return self.fixture.Configuration

    @dbus_property(access=PropertyAccess.READ)
    def Media(self) -> "s":
        """Get Media."""
        return self.fixture.Media

    @dbus_property(access=PropertyAccess.READ)
    def MediaCompatibility(self) -> "as":
        """Get MediaCompatibility."""
        return self.fixture.MediaCompatibility

    @dbus_property(access=PropertyAccess.READ)
    def MediaRemovable(self) -> "b":
        """Get MediaRemovable."""
        return self.fixture.MediaRemovable

    @dbus_property(access=PropertyAccess.READ)
    def MediaAvailable(self) -> "b":
        """Get MediaAvailable."""
        return self.fixture.MediaAvailable

    @dbus_property(access=PropertyAccess.READ)
    def MediaChangeDetected(self) -> "b":
        """Get MediaChangeDetected."""
        return self.fixture.MediaChangeDetected

    @dbus_property(access=PropertyAccess.READ)
    def Size(self) -> "t":
        """Get Size."""
        return self.fixture.Size

    @dbus_property(access=PropertyAccess.READ)
    def TimeDetected(self) -> "t":
        """Get TimeDetected."""
        return self.fixture.TimeDetected

    @dbus_property(access=PropertyAccess.READ)
    def TimeMediaDetected(self) -> "t":
        """Get TimeMediaDetected."""
        return self.fixture.TimeMediaDetected

    @dbus_property(access=PropertyAccess.READ)
    def Optical(self) -> "b":
        """Get Optical."""
        return self.fixture.Optical

    @dbus_property(access=PropertyAccess.READ)
    def OpticalBlank(self) -> "b":
        """Get OpticalBlank."""
        return self.fixture.OpticalBlank

    @dbus_property(access=PropertyAccess.READ)
    def OpticalNumTracks(self) -> "u":
        """Get OpticalNumTracks."""
        return self.fixture.OpticalNumTracks

    @dbus_property(access=PropertyAccess.READ)
    def OpticalNumAudioTracks(self) -> "u":
        """Get OpticalNumAudioTracks."""
        return self.fixture.OpticalNumAudioTracks

    @dbus_property(access=PropertyAccess.READ)
    def OpticalNumDataTracks(self) -> "u":
        """Get OpticalNumDataTracks."""
        return self.fixture.OpticalNumDataTracks

    @dbus_property(access=PropertyAccess.READ)
    def OpticalNumSessions(self) -> "u":
        """Get OpticalNumSessions."""
        return self.fixture.OpticalNumSessions

    @dbus_property(access=PropertyAccess.READ)
    def RotationRate(self) -> "i":
        """Get RotationRate."""
        return self.fixture.RotationRate

    @dbus_property(access=PropertyAccess.READ)
    def ConnectionBus(self) -> "s":
        """Get ConnectionBus."""
        return self.fixture.ConnectionBus

    @dbus_property(access=PropertyAccess.READ)
    def Seat(self) -> "s":
        """Get Seat."""
        return self.fixture.Seat

    @dbus_property(access=PropertyAccess.READ)
    def Removable(self) -> "b":
        """Get Removable."""
        return self.fixture.Removable

    @dbus_property(access=PropertyAccess.READ)
    def Ejectable(self) -> "b":
        """Get Ejectable."""
        return self.fixture.Ejectable

    @dbus_property(access=PropertyAccess.READ)
    def SortKey(self) -> "s":
        """Get SortKey."""
        return self.fixture.SortKey

    @dbus_property(access=PropertyAccess.READ)
    def CanPowerOff(self) -> "b":
        """Get CanPowerOff."""
        return self.fixture.CanPowerOff

    @dbus_property(access=PropertyAccess.READ)
    def SiblingId(self) -> "s":
        """Get SiblingId."""
        return self.fixture.SiblingId

    @dbus_method()
    def Eject(self, options: "a{sv}") -> None:
        """Do Eject method."""

    @dbus_method()
    def SetConfiguration(self, value: "a{sv}", options: "a{sv}") -> None:
        """Do SetConfiguration method."""

    @dbus_method()
    def PowerOff(self, options: "a{sv}") -> None:
        """Do PowerOff method."""
