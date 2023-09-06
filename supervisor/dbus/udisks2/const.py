"""Constants for UDisks2."""

from enum import StrEnum

from dbus_fast import Variant

UDISKS2_DEFAULT_OPTIONS = {"auth.no_user_interaction": Variant("b", True)}


class EncryptType(StrEnum):
    """Encryption type."""

    LUKS1 = "luks1"
    LUKS2 = "luks2"


class EraseMode(StrEnum):
    """Erase mode."""

    ZERO = "zero"
    ATA_SECURE_ERASE = "ata-secure-erase"
    ATA_SECURE_ERASE_ENHANCED = "ata-secure-erase-enhanced"


class FormatType(StrEnum):
    """Format type."""

    EMPTY = "empty"
    SWAP = "swap"
    DOS = "dos"
    GPT = "gpt"


class PartitionTableType(StrEnum):
    """Partition Table type."""

    DOS = "dos"
    GPT = "gpt"
    UNKNOWN = ""
