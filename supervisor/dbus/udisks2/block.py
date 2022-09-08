"""Interface to UDisks2 Block Device over D-Bus."""
from dataclasses import dataclass
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


@dataclass
class FstabConfigDetails:
    """fstab configuration details."""

    fsname: str
    dir: str
    type: str
    opts: str
    freq: int
    passno: int

    @staticmethod
    def from_dict(data: FstabConfigDetailsDataType) -> "FstabConfigDetails":
        """Create FstabConfigDetails from dict."""
        return FstabConfigDetails(
            fsname=bytes(data["fsname"]).decode(),
            dir=bytes(data["dir"]).decode(),
            type=bytes(data["type"]).decode(),
            opts=bytes(data["opts"]).decode(),
            freq=data["freq"],
            passno=data["passno"],
        )

    def to_dict(self) -> FstabConfigDetailsDataType:
        """Return dict representation."""
        return {
            "fsname": bytearray(self.fsname),
            "dir": bytearray(self.dir),
            "type": bytearray(self.type),
            "opts": bytearray(self.opts),
            "freq": self.freq,
            "passno": self.passno,
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


@dataclass
class CrypttabConfigDetails:
    """crypttab configuration details."""

    name: str
    device: str
    passphrase_path: str
    passphrase_contents: str
    options: str

    @staticmethod
    def from_dict(data: CrypttabConfigDetailsDataType) -> "CrypttabConfigDetails":
        """Create CrypttabConfigDetails from dict."""
        return CrypttabConfigDetails(
            name=bytes(data["name"]).decode(),
            device=bytes(data["device"]).decode(),
            passphrase_path=bytes(data["passphrase-path"]).decode(),
            passphrase_contents=bytes(data["passphrase-contents"]).decode(),
            options=bytes(data["options"]).decode(),
        )

    def to_dict(self) -> CrypttabConfigDetailsDataType:
        """Return dict representation."""
        return {
            "name": bytearray(self.name),
            "device": bytearray(self.device),
            "passphrase-path": bytearray(self.passphrase_path),
            "passphrase-contents": bytearray(self.passphrase_contents),
            "options": bytearray(self.options),
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
                FstabConfigDetails.from_dict(details)
                if "dir" in details
                else CrypttabConfigDetails.from_dict(details),
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
        type_: str,
        details: FstabConfigDetails | CrypttabConfigDetails,
        options: dict[str, Any] = None,
    ):
        """Add new configuration item."""
        if not options:
            options = {}
        await self.dbus.Block.AddConfigurationItem(
            ("(sa{sv})", (type_, details.to_dict())), ("a{sv}", options)
        )
        await self.update()

    @dbus_connected
    async def remove_configuration_item(
        self,
        type_: str,
        details: FstabConfigDetails | CrypttabConfigDetails,
        options: dict[str, Any] = None,
    ):
        """Remove existing configuration item."""
        if not options:
            options = {}
        await self.dbus.Block.RemoveConfigurationItem(
            ("(sa{sv})", (type_, details.to_dict())), ("a{sv}", options)
        )
        await self.update()

    @dbus_connected
    async def update_configuration_item(
        self,
        old_type: str,
        old_details: FstabConfigDetails | CrypttabConfigDetails,
        new_type: str,
        new_details: FstabConfigDetails | CrypttabConfigDetails,
        options: dict[str, Any] = None,
    ):
        """Add new configuration item."""
        if not options:
            options = {}
        await self.dbus.Block.AddConfigurationItem(
            ("(sa{sv})", (old_type, old_details.to_dict())),
            ("(sa{sv})", (new_type, new_details.to_dict())),
            ("a{sv}", options),
        )
        await self.update()

    @dbus_connected
    async def update(self):
        """Update Properties."""
        self.properties = await self.dbus.get_properties(DBUS_IFACE_BLOCK)
