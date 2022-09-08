"""Interface to UDisks2 Block Device over D-Bus."""
from typing import Any, TypedDict
from typing_extensions import Required

from ...utils.dbus import DBus
from ..const import (
    DBUS_ATTR_CONFIGURATION,
    DBUS_ATTR_DEVICE,
    DBUS_ATTR_ID,
    DBUS_ATTR_READ_ONLY,
    DBUS_ATTR_SIZE,
    DBUS_IFACE_BLOCK,
    DBUS_NAME_UDISKS2,
)
from ..interface import DBusInterfaceProxy, dbus_property
from ..utils import dbus_connected


class FstabConfigDetailsDataType(TypedDict):
    """fstab configuration details data type."""

    fsname: bytearray
    dir: bytearray
    type: bytearray
    opts: bytearray
    freq: int
    passno: int


class FstabConfigDetails:
    """fstab configuration details."""

    def __init__(self, data: FstabConfigDetailsDataType) -> None:
        """Initialize FstabConfigurationDetails object."""
        self.data = data

    @property
    def fsname(self) -> str:
        """Return fsname."""
        return bytes(self.data["fsname"]).decode()

    @property
    def dir(self) -> str:
        """Return dir."""
        return bytes(self.data["dir"]).decode()

    @property
    def type(self) -> str:
        """Return type."""
        return bytes(self.data["type"]).decode()

    @property
    def opts(self) -> str:
        """Return opts."""
        return bytes(self.data["opts"]).decode()

    @property
    def freq(self) -> int:
        """Return freq."""
        return self.data["freq"]

    @property
    def passno(self) -> int:
        """Return passno."""
        return self.data["passno"]

    @staticmethod
    def from_fstab_to_dbus(
        fsname: str, dir: str, type_: str, opts: str, freq: int, passno: int
    ) -> dict[str, bytearray | int]:
        """Convert fstab configuration to D-Bus format."""
        return {
            "fsname": bytearray(fsname),
            "dir": bytearray(dir),
            "type": bytearray(type_),
            "opts": bytearray(opts),
            "freq": freq,
            "passno": passno,
        }


CrypttabConfigDetailsDataType = TypedDict(
    "CrypttabConfigurationDetailsDataType",
    {
        "name": Required[
            bytearray,
        ],
        "device": Required[
            bytearray,
        ],
        "passphrase-path": Required[
            bytearray,
        ],
        "passphrase-contents": Required[
            bytearray,
        ],
        "options": Required[
            bytearray,
        ],
    },
)


class CrypttabConfigDetails:
    """crypttab configuration details."""

    def __init__(self, data: CrypttabConfigDetailsDataType) -> None:
        """Initialize CrypttabConfigurationDetails object."""
        self.data = data

    @property
    def name(self) -> str:
        """Return name."""
        return bytes(self.data["name"]).decode()

    @property
    def device(self) -> str:
        """Return device."""
        return bytes(self.data["device"]).decode()

    @property
    def passphrase_path(self) -> str:
        """Return passphrase_path."""
        return bytes(self.data["passphrase-path"]).decode()

    @property
    def passphrase_contents(self) -> str:
        """Return passphrase_contents."""
        return bytes(self.data["passphrase-contents"]).decode()

    @property
    def options(self) -> str:
        """Return options."""
        return bytes(self.data["options"]).decode()

    @staticmethod
    def from_crypttab_to_dbus(
        name: str,
        device: str,
        passphrase_path: str,
        passphrase_contents: str,
        options: str,
    ) -> dict[str, bytearray]:
        """Convert crypttab configuration to D-Bus format."""
        return {
            "name": bytearray(name.encode()),
            "device": bytearray(device.encode()),
            "passphrase-path": (passphrase_path.encode()),
            "passphrase-contents": (passphrase_contents.encode()),
            "options": (options.encode()),
        }


class UDisks2Block(DBusInterfaceProxy):
    """Handle D-Bus interface for UDisks2 block device object.

    http://storaged.org/doc/udisks2-api/latest/gdbus-org.freedesktop.UDisks2.Block.html
    """

    def __init__(self, object_path: str) -> None:
        """Initialize NetworkConnection object."""
        self.object_path = object_path
        self.properties = {}

    async def connect(self):
        """Connect to D-Bus."""
        self.dbus = await DBus.connect(DBUS_NAME_UDISKS2, self.object_path)
        await self.update()

    @property
    @dbus_property
    def device(self) -> str:
        """Return device file."""
        return bytes(self.properties[DBUS_ATTR_DEVICE]).decode()

    @property
    @dbus_property
    def id(self) -> str:
        """Return unique identifer."""
        return self.properties[DBUS_ATTR_ID]

    @property
    @dbus_property
    def read_only(self) -> bool:
        """Return whether device is read only."""
        return self.properties[DBUS_ATTR_READ_ONLY]

    @property
    @dbus_property
    def configuration(
        self,
    ) -> list[tuple[str, FstabConfigDetails | CrypttabConfigDetails]]:
        """Return device configuration."""
        return [
            (
                type_,
                FstabConfigDetails(details)
                if "dir" in details
                else CrypttabConfigDetails(details),
            )
            for type_, details in self.properties[DBUS_ATTR_CONFIGURATION]
        ]

    @property
    @dbus_property
    def size(self) -> int:
        """Return size."""
        return self.properties[DBUS_ATTR_SIZE]

    @dbus_connected
    async def add_configuration_item(
        self,
        item: tuple[
            str,
            FstabConfigDetailsDataType | CrypttabConfigDetailsDataType
        ],
        options: dict[str, Any] = None,
    ):
        """Add new configuration item."""
        if not options:
            options = {}
        await self.dbus.Block.AddConfigurationItem(("sa{sv}", item), ("a{sv}", options))
        await self.update()

    @dbus_connected
    async def remove_configuration_item(
        self,
        item: tuple[
            str,
            FstabConfigDetailsDataType | CrypttabConfigDetailsDataType
        ],
        options: dict[str, Any] = None,
    ):
        """Remove existing configuration item."""
        if not options:
            options = {}
        await self.dbus.Block.RemoveConfigurationItem(
            ("sa{sv}", item), ("a{sv}", options)
        )
        await self.update()

    @dbus_connected
    async def update_configuration_item(
        self,
        old_item: tuple[
            str,
            FstabConfigDetailsDataType | CrypttabConfigDetailsDataType
        ],
        new_item: tuple[
            str,
            FstabConfigDetailsDataType | CrypttabConfigDetailsDataType
        ],
        options: dict[str, Any] = None,
    ):
        """Add new configuration item."""
        if not options:
            options = {}
        await self.dbus.Block.AddConfigurationItem(
            ("sa{sv}", old_item), ("sa{sv}", new_item), ("a{sv}", options)
        )
        await self.update()

    @dbus_connected
    async def update(self):
        """Update Properties."""
        self.properties = await self.dbus.get_properties(DBUS_IFACE_BLOCK)
