"""Mock of rauc dbus service."""

from dbus_fast import DBusError, Variant
from dbus_fast.service import PropertyAccess, dbus_property, signal

from .base import DBusServiceMock, dbus_method

BUS_NAME = "de.pengutronix.rauc"

SLOT_STATUS_FIXTURE: list[tuple[str | dict[str, Variant]]] = [
    (
        "kernel.0",
        {
            "activated.count": Variant("u", 9),
            "activated.timestamp": Variant("s", "2022-08-23T21:03:22Z"),
            "boot-status": Variant("s", "good"),
            "bundle.compatible": Variant("s", "haos-odroid-n2"),
            "sha256": Variant(
                "s",
                "c624db648b8401fae37ee5bb1a6ec90bdf4183aef364b33314a73c7198e49d5b",
            ),
            "state": Variant("s", "inactive"),
            "size": Variant("t", 10371072),
            "installed.count": Variant("u", 9),
            "class": Variant("s", "kernel"),
            "device": Variant("s", "/dev/disk/by-partlabel/hassos-kernel0"),
            "type": Variant("s", "raw"),
            "bootname": Variant("s", "A"),
            "bundle.version": Variant("s", "9.0.dev20220818"),
            "installed.timestamp": Variant("s", "2022-08-23T21:03:16Z"),
            "status": Variant("s", "ok"),
        },
    ),
    (
        "boot.0",
        {
            "bundle.compatible": Variant("s", "haos-odroid-n2"),
            "sha256": Variant(
                "s",
                "a5019b335f33be2cf89c96bb2d0695030adb72c1d13d650a5bbe1806dd76d6cc",
            ),
            "state": Variant("s", "inactive"),
            "size": Variant("t", 25165824),
            "installed.count": Variant("u", 19),
            "class": Variant("s", "boot"),
            "device": Variant("s", "/dev/disk/by-partlabel/hassos-boot"),
            "type": Variant("s", "vfat"),
            "status": Variant("s", "ok"),
            "bundle.version": Variant("s", "9.0.dev20220824"),
            "installed.timestamp": Variant("s", "2022-08-25T21:11:46Z"),
        },
    ),
    (
        "rootfs.0",
        {
            "bundle.compatible": Variant("s", "haos-odroid-n2"),
            "parent": Variant("s", "kernel.0"),
            "state": Variant("s", "inactive"),
            "size": Variant("t", 117456896),
            "sha256": Variant(
                "s",
                "7d908b4d578d072b1b0f75de8250fd97b6e119bff09518a96fffd6e4aec61721",
            ),
            "class": Variant("s", "rootfs"),
            "device": Variant("s", "/dev/disk/by-partlabel/hassos-system0"),
            "type": Variant("s", "raw"),
            "status": Variant("s", "ok"),
            "bundle.version": Variant("s", "9.0.dev20220818"),
            "installed.timestamp": Variant("s", "2022-08-23T21:03:21Z"),
            "installed.count": Variant("u", 9),
        },
    ),
    (
        "spl.0",
        {
            "bundle.compatible": Variant("s", "haos-odroid-n2"),
            "sha256": Variant(
                "s",
                "9856a94df1d6abbc672adaf95746ec76abd3a8191f9d08288add6bb39e63ef45",
            ),
            "state": Variant("s", "inactive"),
            "size": Variant("t", 8388608),
            "installed.count": Variant("u", 19),
            "class": Variant("s", "spl"),
            "device": Variant("s", "/dev/disk/by-partlabel/hassos-boot"),
            "type": Variant("s", "raw"),
            "status": Variant("s", "ok"),
            "bundle.version": Variant("s", "9.0.dev20220824"),
            "installed.timestamp": Variant("s", "2022-08-25T21:11:51Z"),
        },
    ),
    (
        "kernel.1",
        {
            "activated.count": Variant("u", 10),
            "activated.timestamp": Variant("s", "2022-08-25T21:11:52Z"),
            "boot-status": Variant("s", "good"),
            "bundle.compatible": Variant("s", "haos-odroid-n2"),
            "sha256": Variant(
                "s",
                "f57e354b8bd518022721e71fafaf278972af966d8f6cbefb4610db13785801c8",
            ),
            "state": Variant("s", "booted"),
            "size": Variant("t", 10371072),
            "installed.count": Variant("u", 10),
            "class": Variant("s", "kernel"),
            "device": Variant("s", "/dev/disk/by-partlabel/hassos-kernel1"),
            "type": Variant("s", "raw"),
            "bootname": Variant("s", "B"),
            "bundle.version": Variant("s", "9.0.dev20220824"),
            "installed.timestamp": Variant("s", "2022-08-25T21:11:46Z"),
            "status": Variant("s", "ok"),
        },
    ),
    (
        "rootfs.1",
        {
            "bundle.compatible": Variant("s", "haos-odroid-n2"),
            "parent": Variant("s", "kernel.1"),
            "state": Variant("s", "active"),
            "size": Variant("t", 117456896),
            "sha256": Variant(
                "s",
                "55936b64d391954ae1aed24dd1460e191e021e78655470051fa7939d12fff68a",
            ),
            "class": Variant("s", "rootfs"),
            "device": Variant("s", "/dev/disk/by-partlabel/hassos-system1"),
            "type": Variant("s", "raw"),
            "status": Variant("s", "ok"),
            "bundle.version": Variant("s", "9.0.dev20220824"),
            "installed.timestamp": Variant("s", "2022-08-25T21:11:51Z"),
            "installed.count": Variant("u", 10),
        },
    ),
]


def setup(object_path: str | None = None) -> DBusServiceMock:
    """Create dbus mock object."""
    return Rauc()


class Rauc(DBusServiceMock):
    """Rauc mock.

    gdbus introspect --system --dest de.pengutronix.rauc --object-path /
    """

    object_path = "/"
    interface = "de.pengutronix.rauc.Installer"
    response_mark: list[str] | DBusError = ["kernel.1", "marked slot kernel.1 as good"]
    response_get_slot_status = SLOT_STATUS_FIXTURE

    @dbus_property(access=PropertyAccess.READ)
    def Operation(self) -> "s":
        """Return operation."""
        return "idle"

    @dbus_property(access=PropertyAccess.READ)
    def LastError(self) -> "s":
        """Return last error."""
        return ""

    @dbus_property(access=PropertyAccess.READ)
    def Progress(self) -> "(isi)":
        """Return progress."""
        return [0, "", 0]

    @dbus_property(access=PropertyAccess.READ)
    def Compatible(self) -> "s":
        """Return compatible."""
        return "haos-odroid-n2"

    @dbus_property(access=PropertyAccess.READ)
    def Variant(self) -> "s":
        """Return variant."""
        return ""

    @dbus_property(access=PropertyAccess.READ)
    def BootSlot(self) -> "s":
        """Return boot slot."""
        return "B"

    @signal()
    def Completed(self) -> "i":
        """Signal completed."""
        return 0

    @dbus_method()
    def Install(self, source: "s"):
        """Install source."""
        self.Completed()

    @dbus_method()
    def InstallBundle(self, source: "s", arg: "a{sv}"):
        """Install source bundle."""
        self.Completed()

    @dbus_method()
    def Mark(self, state: "s", slot_identifier: "s") -> "ss":
        """Mark slot."""
        return self.response_mark

    @dbus_method()
    def GetPrimary(self) -> "s":
        """Get primary slot."""
        return "kernel.0"

    @dbus_method()
    def GetSlotStatus(self) -> "a(sa{sv})":
        """Get slot status."""
        return self.response_get_slot_status
