"""Backup consts."""

from enum import StrEnum
import tarfile
from typing import Literal

from awesomeversion import AwesomeVersion

from ..mounts.mount import Mount

BUF_SIZE = 2**20 * 4  # 4MB
# Encrypted tars are read in stream mode, where tarfile decompresses a whole
# buffer at once and copies the remainder on every read. A large buffer makes
# extracting highly compressible data quadratic, so use the tar record size.
STREAM_BUF_SIZE = tarfile.RECORDSIZE
SECURETAR_CREATE_VERSION = 2
SECURETAR_V3_CREATE_VERSION = 3
CORE_SECURETAR_V3_MIN_VERSION: AwesomeVersion = AwesomeVersion("2026.3.0")
DEFAULT_FREEZE_TIMEOUT = 600

JOB_FREEZE_ALL = "backup_manager_freeze_all"
JOB_FULL_BACKUP = "backup_manager_full_backup"
JOB_FULL_RESTORE = "backup_manager_full_restore"
JOB_PARTIAL_BACKUP = "backup_manager_partial_backup"
JOB_PARTIAL_RESTORE = "backup_manager_partial_restore"
JOB_THAW_ALL = "backup_manager_thaw_all"
LOCATION_CLOUD_BACKUP = ".cloud_backup"

LOCATION_TYPE = Mount | Literal[".cloud_backup"] | None


class BackupType(StrEnum):
    """Backup type enum."""

    FULL = "full"
    PARTIAL = "partial"


class BackupJobStage(StrEnum):
    """Backup job stage enum."""

    APP_REPOSITORIES = "app_repositories"
    APPS = "apps"
    FINISHING_FILE = "finishing_file"
    FOLDERS = "folders"
    HOME_ASSISTANT = "home_assistant"
    SUPERVISOR_CONFIG = "supervisor_config"
    COPY_ADDITIONAL_LOCATIONS = "copy_additional_locations"
    AWAIT_APP_RESTARTS = "await_app_restarts"


class RestoreJobStage(StrEnum):
    """Restore job stage enum."""

    APP_REPOSITORIES = "app_repositories"
    APPS = "apps"
    AWAIT_APP_RESTARTS = "await_app_restarts"
    AWAIT_HOME_ASSISTANT_RESTART = "await_home_assistant_restart"
    FOLDERS = "folders"
    HOME_ASSISTANT = "home_assistant"
    SUPERVISOR_CONFIG = "supervisor_config"
    REMOVE_DELTA_APPS = "remove_delta_apps"
