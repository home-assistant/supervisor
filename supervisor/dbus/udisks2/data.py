"""Data for UDisks2."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, NotRequired, TypedDict

from dbus_fast import Variant

from .const import EncryptType, EraseMode


def udisks2_bytes_to_path(path_bytes: bytearray) -> Path:
    """Convert bytes to path object without null character on end."""
    if path_bytes and path_bytes[-1] == 0:
        return Path(path_bytes[:-1].decode())

    return Path(path_bytes.decode())


def _optional_variant(signature: str, value: Any | None) -> Variant | None:
    """Output variant if value is not none."""
    return Variant(signature, value) if value is not None else None


class DeviceSpecificationDataType(TypedDict, total=False):
    """Device specification data type."""

    path: str
    label: str
    uuid: str


@dataclass(slots=True)
class DeviceSpecification:
    """Device specification.

    http://storaged.org/doc/udisks2-api/latest/gdbus-org.freedesktop.UDisks2.Manager.html#gdbus-method-org-freedesktop-UDisks2-Manager.ResolveDevice
    """

    path: Path | None = None
    label: str | None = None
    uuid: str | None = None

    @staticmethod
    def from_dict(data: DeviceSpecificationDataType) -> "DeviceSpecification":
        """Create DeviceSpecification from dict."""
        return DeviceSpecification(
            path=Path(data["path"]) if "path" in data else None,
            label=data.get("label"),
            uuid=data.get("uuid"),
        )

    def to_dict(self) -> dict[str, Variant]:
        """Return dict representation."""
        data = {
            "path": Variant("s", self.path.as_posix()) if self.path else None,
            "label": _optional_variant("s", self.label),
            "uuid": _optional_variant("s", self.uuid),
        }
        return {k: v for k, v in data.items() if v}


FormatOptionsDataType = TypedDict(
    "FormatOptionsDataType",
    {
        "label": NotRequired[str],
        "take-ownership": NotRequired[bool],
        "encrypt.passphrase": NotRequired[bytearray],
        "encrypt.type": NotRequired[str],
        "erase": NotRequired[str],
        "update-partition-type": NotRequired[bool],
        "no-block": NotRequired[bool],
        "dry-run-first": NotRequired[bool],
        "no-discard": NotRequired[bool],
        "tear-down": NotRequired[bool],
        # UDisks2 standard options
        "auth.no_user_interaction": NotRequired[bool],
    },
)


@dataclass(slots=True)
class FormatOptions:
    """Options for formatting a block device.

    http://storaged.org/doc/udisks2-api/latest/gdbus-org.freedesktop.UDisks2.Block.html#gdbus-method-org-freedesktop-UDisks2-Block.Format
    """

    label: str | None = None
    take_ownership: bool | None = None
    encrypt_passpharase: str | None = None
    encrypt_type: EncryptType | None = None
    erase: EraseMode | None = None
    update_partition_type: bool | None = None
    no_block: bool | None = None
    dry_run_first: bool | None = None
    no_discard: bool | None = None
    tear_down: bool | None = None
    # UDisks2 standard options
    auth_no_user_interaction: bool | None = None

    @staticmethod
    def from_dict(data: FormatOptionsDataType) -> "FormatOptions":
        """Create FormatOptions from dict."""
        return FormatOptions(
            label=data.get("label"),
            take_ownership=data.get("take-ownership"),
            encrypt_passpharase=bytes(data["encrypt.passphrase"]).decode(
                encoding="utf-8"
            )
            if "encrypt.passphrase" in data
            else None,
            encrypt_type=EncryptType(data["encrypt.type"])
            if "encrypt.type" in data
            else None,
            erase=EraseMode(data["erase"]) if "erase" in data else None,
            update_partition_type=data.get("update-partition-type"),
            no_block=data.get("no-block"),
            dry_run_first=data.get("dry-run-first"),
            no_discard=data.get("no-discard"),
            tear_down=data.get("tear-down"),
            # UDisks2 standard options
            auth_no_user_interaction=data.get("auth.no_user_interaction"),
        )

    def to_dict(self) -> dict[str, Variant]:
        """Return dict representation."""
        data = {
            "label": _optional_variant("s", self.label),
            "take-ownership": _optional_variant("b", self.take_ownership),
            "encrypt.passphrase": Variant(
                "ay", bytearray(self.encrypt_passpharase, encoding="utf-8")
            )
            if self.encrypt_passpharase
            else None,
            "encrypt.type": Variant("s", self.encrypt_type)
            if self.encrypt_type
            else None,
            "erase": Variant("s", self.erase) if self.erase else None,
            "update-partition-type": _optional_variant("b", self.update_partition_type),
            "no-block": _optional_variant("b", self.no_block),
            "dry-run-first": _optional_variant("b", self.dry_run_first),
            "no-discard": _optional_variant("b", self.no_discard),
            "tear-down": _optional_variant("b", self.tear_down),
            # UDisks2 standard options
            "auth.no_user_interaction": _optional_variant(
                "b", self.auth_no_user_interaction
            ),
        }
        return {k: v for k, v in data.items() if v}


MountOptionsDataType = TypedDict(
    "MountOptionsDataType",
    {
        "fstype": NotRequired[str],
        "options": NotRequired[str],
        # UDisks2 standard options
        "auth.no_user_interaction": NotRequired[bool],
    },
)


@dataclass(slots=True)
class MountOptions:
    """Filesystem mount options.

    http://storaged.org/doc/udisks2-api/latest/gdbus-org.freedesktop.UDisks2.Filesystem.html#gdbus-method-org-freedesktop-UDisks2-Filesystem.Mount
    """

    fstype: str | None = None
    options: list[str] | None = None
    # UDisks2 standard options
    auth_no_user_interaction: bool | None = None

    @staticmethod
    def from_dict(data: MountOptionsDataType) -> "MountOptions":
        """Create MountOptions from dict."""
        return MountOptions(
            fstype=data.get("fstype"),
            options=data["options"].split(",") if "options" in data else None,
            # UDisks2 standard options
            auth_no_user_interaction=data.get("auth.no_user_interaction"),
        )

    def to_dict(self) -> dict[str, Variant]:
        """Return dict representation."""
        data = {
            "fstype": _optional_variant("s", self.fstype),
            "options": Variant("s", ",".join(self.options)) if self.options else None,
            # UDisks2 standard options
            "auth.no_user_interaction": _optional_variant(
                "b", self.auth_no_user_interaction
            ),
        }
        return {k: v for k, v in data.items() if v is not None}


UnmountOptionsDataType = TypedDict(
    "UnmountOptionsDataType",
    {
        "force": NotRequired[bool],
        # UDisks2 standard options
        "auth.no_user_interaction": NotRequired[bool],
    },
)


@dataclass(slots=True)
class UnmountOptions:
    """Filesystem unmount options.

    http://storaged.org/doc/udisks2-api/latest/gdbus-org.freedesktop.UDisks2.Filesystem.html#gdbus-method-org-freedesktop-UDisks2-Filesystem.Unmount
    """

    force: bool | None = None
    # UDisks2 standard options
    auth_no_user_interaction: bool | None = None

    @staticmethod
    def from_dict(data: UnmountOptionsDataType) -> "UnmountOptions":
        """Create MountOptions from dict."""
        return UnmountOptions(
            force=data.get("force"),
            # UDisks2 standard options
            auth_no_user_interaction=data.get("auth.no_user_interaction"),
        )

    def to_dict(self) -> dict[str, Variant]:
        """Return dict representation."""
        data = {
            "force": _optional_variant("b", self.force),
            # UDisks2 standard options
            "auth.no_user_interaction": _optional_variant(
                "b", self.auth_no_user_interaction
            ),
        }
        return {k: v for k, v in data.items() if v}


CreatePartitionOptionsDataType = TypedDict(
    "CreatePartitionOptionsDataType",
    {
        "partition-type": NotRequired[str],
        # UDisks2 standard options
        "auth.no_user_interaction": NotRequired[bool],
    },
)


@dataclass(slots=True)
class CreatePartitionOptions:
    """Create partition options.

    http://storaged.org/doc/udisks2-api/latest/gdbus-org.freedesktop.UDisks2.PartitionTable.html#gdbus-method-org-freedesktop-UDisks2-PartitionTable.CreatePartition
    """

    partition_type: str | None = None
    # UDisks2 standard options
    auth_no_user_interaction: bool | None = None

    @staticmethod
    def from_dict(data: CreatePartitionOptionsDataType) -> "CreatePartitionOptions":
        """Create CreatePartitionOptions from dict."""
        return CreatePartitionOptions(
            partition_type=data.get("partition-type"),
            # UDisks2 standard options
            auth_no_user_interaction=data.get("auth.no_user_interaction"),
        )

    def to_dict(self) -> dict[str, Variant]:
        """Return dict representation."""
        data = {
            "partition-type": _optional_variant("s", self.partition_type),
            # UDisks2 standard options
            "auth.no_user_interaction": _optional_variant(
                "b", self.auth_no_user_interaction
            ),
        }
        return {k: v for k, v in data.items() if v}


DeletePartitionOptionsDataType = TypedDict(
    "DeletePartitionOptionsDataType",
    {
        "tear-down": NotRequired[bool],
        # UDisks2 standard options
        "auth.no_user_interaction": NotRequired[bool],
    },
)


@dataclass(slots=True)
class DeletePartitionOptions:
    """Delete partition options.

    http://storaged.org/doc/udisks2-api/latest/gdbus-org.freedesktop.UDisks2.Partition.html#gdbus-method-org-freedesktop-UDisks2-Partition.Delete
    """

    tear_down: bool | None = None
    # UDisks2 standard options
    auth_no_user_interaction: bool | None = None

    @staticmethod
    def from_dict(data: DeletePartitionOptionsDataType) -> "DeletePartitionOptions":
        """Create DeletePartitionOptions from dict."""
        return DeletePartitionOptions(
            tear_down=data.get("tear-down"),
            # UDisks2 standard options
            auth_no_user_interaction=data.get("auth.no_user_interaction"),
        )

    def to_dict(self) -> dict[str, Variant]:
        """Return dict representation."""
        data = {
            "tear-down": _optional_variant("b", self.tear_down),
            # UDisks2 standard options
            "auth.no_user_interaction": _optional_variant(
                "b", self.auth_no_user_interaction
            ),
        }
        return {k: v for k, v in data.items() if v}
