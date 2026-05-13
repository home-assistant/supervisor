"""App static data."""

from datetime import timedelta
from enum import StrEnum

from ..jobs.const import JobCondition


class AppBackupMode(StrEnum):
    """Backup mode of an App."""

    HOT = "hot"
    COLD = "cold"


class MappingType(StrEnum):
    """Mapping type of an App Folder."""

    DATA = "data"
    CONFIG = "config"
    SSL = "ssl"
    ADDONS = "addons"
    BACKUP = "backup"
    SHARE = "share"
    MEDIA = "media"
    HOMEASSISTANT_CONFIG = "homeassistant_config"
    ALL_ADDON_CONFIGS = "all_addon_configs"
    ADDON_CONFIG = "addon_config"


ATTR_BACKUP = "backup"
ATTR_BREAKING_VERSIONS = "breaking_versions"
ATTR_CODENOTARY = "codenotary"
ATTR_READ_ONLY = "read_only"
ATTR_PATH = "path"
WATCHDOG_RETRY_SECONDS = 10
WATCHDOG_MAX_ATTEMPTS = 5
WATCHDOG_THROTTLE_PERIOD = timedelta(minutes=30)
WATCHDOG_THROTTLE_MAX_CALLS = 10

APP_UPDATE_CONDITIONS = [
    JobCondition.FREE_SPACE,
    JobCondition.HEALTHY,
    JobCondition.INTERNET_HOST,
    JobCondition.PLUGINS_UPDATED,
    JobCondition.SUPERVISOR_UPDATED,
]

RE_SLUG = r"[-_.A-Za-z0-9]+"
