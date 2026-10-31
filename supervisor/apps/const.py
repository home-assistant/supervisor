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
    LOCAL_APPS = "local_apps"
    BACKUP = "backup"
    SHARE = "share"
    MEDIA = "media"
    HOMEASSISTANT_CONFIG = "homeassistant_config"
    ALL_APP_CONFIGS = "all_app_configs"
    APP_CONFIG = "app_config"

    # Legacy, deprecated as of 2026.07; use app equivalents
    ADDONS = "addons"
    ALL_ADDON_CONFIGS = "all_addon_configs"
    ADDON_CONFIG = "addon_config"


ATTR_BACKUP = "backup"
ATTR_BREAKING_VERSIONS = "breaking_versions"
ATTR_CODENOTARY = "codenotary"
ATTR_LOG_FORMAT = "log_format"
ATTR_READ_ONLY = "read_only"
ATTR_PATH = "path"
# Retry schedule: 30 s base, factor 1.5, 6 h cap (saturates ~attempt 18),
# ~1 week total across 50 attempts. Throttle widened to match so repeated
# deaths during one outage do not trip it before the inner loop acts.
WATCHDOG_RETRY_SECONDS = 30
WATCHDOG_RETRY_BACKOFF_FACTOR = 1.5
WATCHDOG_MAX_RETRY_SECONDS = 6 * 60 * 60
WATCHDOG_MAX_ATTEMPTS = 50
WATCHDOG_THROTTLE_PERIOD = timedelta(days=14)
WATCHDOG_THROTTLE_MAX_CALLS = 50

APP_UPDATE_CONDITIONS = [
    JobCondition.FREE_SPACE,
    JobCondition.HEALTHY,
    JobCondition.INTERNET_HOST,
    JobCondition.PLUGINS_UPDATED,
    JobCondition.SUPERVISOR_UPDATED,
]

RE_SLUG = r"[-_.A-Za-z0-9]+"
