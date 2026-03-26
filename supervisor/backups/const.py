"""Backup consts."""

from enum import StrEnum
from typing import Literal

from awesomeversion import AwesomeVersion

from ..mounts.mount import Mount

BUF_SIZE = 2**20 * 4  # 4MB
SECURETAR_CREATE_VERSION = 2
SECURETAR_V3_CREATE_VERSION = 3
CORE_SECURETAR_V3_MIN_VERSION: AwesomeVersion = AwesomeVersion("2026.3.0")
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
    SUPERVISOR_CONFIG = "supervisor_config"
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
    SUPERVISOR_CONFIG = "supervisor_config"
    REMOVE_DELTA_ADDONS = "remove_delta_addons"
