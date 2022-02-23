"""Add-on static data."""
from enum import Enum


class AddonBackupMode(str, Enum):
    """Backup mode of an Add-on."""

    HOT = "hot"
    COLD = "cold"


ATTR_BACKUP = "backup"
ATTR_CODENOTARY = "codenotary"
