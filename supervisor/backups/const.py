"""Backup consts."""
from enum import Enum


class BackupType(str, Enum):
    """Backup type enum."""

    FULL = "full"
    PARTIAL = "partial"
