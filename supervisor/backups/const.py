"""Backup consts."""

from enum import StrEnum
from typing import Literal

from ..mounts.mount import Mount

BUF_SIZE = 2**20 * 4  # 4MB
DEFAULT_FREEZE_TIMEOUT = 600
LOCATION_CLOUD_BACKUP = ".cloud_backup"

LOCATION_TYPE = Mount | Literal[".cloud_backup"] | None


class BackupType(StrEnum):
    """Backup type enum."""

    FULL = "full"
    PARTIAL = "partial"


class BackupJobStage(StrEnum):
    """Backup job stage enum."""

    ADDON_REPOSITORIES = "addon_repositories"
    ADDONS = "addons"
    FINISHING_FILE = "finishing_file"
    FOLDERS = "folders"
    HOME_ASSISTANT = "home_assistant"
    COPY_ADDITONAL_LOCATIONS = "copy_additional_locations"
    AWAIT_ADDON_RESTARTS = "await_addon_restarts"


class RestoreJobStage(StrEnum):
    """Restore job stage enum."""

    ADDON_REPOSITORIES = "addon_repositories"
    ADDONS = "addons"
    AWAIT_ADDON_RESTARTS = "await_addon_restarts"
    AWAIT_HOME_ASSISTANT_RESTART = "await_home_assistant_restart"
    FOLDERS = "folders"
    HOME_ASSISTANT = "home_assistant"
    REMOVE_DELTA_ADDONS = "remove_delta_addons"
