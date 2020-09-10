"""Const for plugins."""
from pathlib import Path

from ..const import SUPERVISOR_DATA

FILE_HASSIO_AUDIO = Path(SUPERVISOR_DATA, "audio.json")
FILE_HASSIO_CLI = Path(SUPERVISOR_DATA, "cli.json")
FILE_HASSIO_DNS = Path(SUPERVISOR_DATA, "dns.json")
FILE_HASSIO_OBSERVER = Path(SUPERVISOR_DATA, "observer.json")
FILE_HASSIO_MULTICAST = Path(SUPERVISOR_DATA, "multicast.json")
