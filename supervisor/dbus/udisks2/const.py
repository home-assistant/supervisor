"""Constants for UDisks2."""

from enum import Enum

from dbus_fast import Variant

UDISKS2_DEFAULT_OPTIONS = {"auth.no_user_interaction": Variant("b", True)}


class EncryptType(str, Enum):
    """Encryption type."""

    LUKS1 = "luks1"
    LUKS2 = "luks2"


class EraseMode(str, Enum):
    """Erase mode."""

    ZERO = "zero"
    ATA_SECURE_ERASE = "ata-secure-erase"
    ATA_SECURE_ERASE_ENHANCED = "ata-secure-erase-enhanced"


class FormatType(str, Enum):
    """Format type."""

    EMPTY = "empty"
    SWAP = "swap"
    DOS = "dos"
    GPT = "gpt"


class PartitionTableType(str, Enum):
    """Partition Table type."""

    DOS = "dos"
    GPT = "gpt"
    UNKNOWN = ""
