"""Const for plugins."""

from datetime import timedelta
from pathlib import Path

from ..const import SUPERVISOR_DATA
from ..jobs.const import JobCondition

FILE_HASSIO_AUDIO = Path(SUPERVISOR_DATA, "audio.json")
FILE_HASSIO_CLI = Path(SUPERVISOR_DATA, "cli.json")
FILE_HASSIO_DNS = Path(SUPERVISOR_DATA, "dns.json")
FILE_HASSIO_OBSERVER = Path(SUPERVISOR_DATA, "observer.json")
FILE_HASSIO_MULTICAST = Path(SUPERVISOR_DATA, "multicast.json")

ATTR_FALLBACK = "fallback"
WATCHDOG_RETRY_SECONDS = 10
WATCHDOG_MAX_ATTEMPTS = 5
WATCHDOG_THROTTLE_PERIOD = timedelta(minutes=30)
WATCHDOG_THROTTLE_MAX_CALLS = 10

PLUGIN_UPDATE_CONDITIONS = [
    JobCondition.FREE_SPACE,
    JobCondition.HEALTHY,
    JobCondition.INTERNET_HOST,
    JobCondition.SUPERVISOR_UPDATED,
]
