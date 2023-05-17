"""Add-on static data."""
from datetime import timedelta
from enum import Enum

from ..jobs.const import JobCondition


class AddonBackupMode(str, Enum):
    """Backup mode of an Add-on."""

    HOT = "hot"
    COLD = "cold"


ATTR_BACKUP = "backup"
ATTR_CODENOTARY = "codenotary"
WATCHDOG_RETRY_SECONDS = 10
WATCHDOG_MAX_ATTEMPTS = 5
WATCHDOG_THROTTLE_PERIOD = timedelta(minutes=30)
WATCHDOG_THROTTLE_MAX_CALLS = 10

ADDON_UPDATE_CONDITIONS = [
    JobCondition.FREE_SPACE,
    JobCondition.HEALTHY,
    JobCondition.INTERNET_HOST,
    JobCondition.PLUGINS_UPDATED,
    JobCondition.SUPERVISOR_UPDATED,
]

RE_SLUG = r"[-_.A-Za-z0-9]+"
