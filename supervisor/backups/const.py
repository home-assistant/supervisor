"""Backup consts."""
from enum import Enum

BUF_SIZE = 2**20 * 4  # 4MB


class BackupType(str, Enum):
    """Backup type enum."""

    FULL = "full"
    PARTIAL = "partial"
