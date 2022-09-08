"""Interface to UDisks2 Block Device over D-Bus."""
from typing import TYPE_CHECKING, Any, TypedDict

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

if TYPE_CHECKING:
    from typing_extensions import Required


class FstabConfigurationDetailsDataType(TypedDict):
    """fstab configuration details data type."""

    fsname: bytes
    dir: bytes
    type: bytes
    opts: bytes
    freq: int
    passno: int


CrypttabConfigurationDetailsDataType = TypedDict(
    "CrypttabConfigurationDetailsDataType",
    {
        "name": Required[
            bytes,
        ],
        "device": Required[
            bytes,
        ],
        "passphrase-path": Required[
            bytes,
        ],
        "passphrase-contents": Required[
            bytes,
        ],
        "options": Required[
            bytes,
        ],
    },
)


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
    ) -> list[
        tuple[
            str,
            FstabConfigurationDetailsDataType | CrypttabConfigurationDetailsDataType,
        ]
    ]:
        """Return device configuration."""
        return self.properties[DBUS_ATTR_CONFIGURATION]

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
            FstabConfigurationDetailsDataType | CrypttabConfigurationDetailsDataType,
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
            FstabConfigurationDetailsDataType | CrypttabConfigurationDetailsDataType,
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
            FstabConfigurationDetailsDataType | CrypttabConfigurationDetailsDataType,
        ],
        new_item: tuple[
            str,
            FstabConfigurationDetailsDataType | CrypttabConfigurationDetailsDataType,
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
