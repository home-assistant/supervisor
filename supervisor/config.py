"""Bootstrap Supervisor."""
from datetime import datetime
import logging
import os
from pathlib import Path, PurePath

from .const import (
    ATTR_ADDONS_CUSTOM_LIST,
    ATTR_DEBUG,
    ATTR_DEBUG_BLOCK,
    ATTR_LAST_BOOT,
    ATTR_LOGGING,
    ATTR_TIMEZONE,
    ATTR_WAIT_BOOT,
    FILE_HASSIO_CONFIG,
    SUPERVISOR_DATA,
)
from .utils.dt import parse_datetime
from .utils.json import JsonConfig
from .validate import SCHEMA_HASSIO_CONFIG

_LOGGER: logging.Logger = logging.getLogger(__name__)

HOMEASSISTANT_CONFIG = PurePath("homeassistant")

HASSIO_SSL = PurePath("ssl")

ADDONS_CORE = PurePath("addons/core")
ADDONS_LOCAL = PurePath("addons/local")
ADDONS_GIT = PurePath("addons/git")
ADDONS_DATA = PurePath("addons/data")

BACKUP_DATA = PurePath("backup")
SHARE_DATA = PurePath("share")
TMP_DATA = PurePath("tmp")
APPARMOR_DATA = PurePath("apparmor")
DNS_DATA = PurePath("dns")
AUDIO_DATA = PurePath("audio")

DEFAULT_BOOT_TIME = datetime.utcfromtimestamp(0).isoformat()


class CoreConfig(JsonConfig):
    """Hold all core config data."""

    def __init__(self):
        """Initialize config object."""
        super().__init__(FILE_HASSIO_CONFIG, SCHEMA_HASSIO_CONFIG)

    @property
    def timezone(self):
        """Return system timezone."""
        return self._data[ATTR_TIMEZONE]

    @timezone.setter
    def timezone(self, value):
        """Set system timezone."""
        self._data[ATTR_TIMEZONE] = value

    @property
    def wait_boot(self) -> int:
        """Return wait time for auto boot stages."""
        return self._data[ATTR_WAIT_BOOT]

    @wait_boot.setter
    def wait_boot(self, value: int):
        """Set wait boot time."""
        self._data[ATTR_WAIT_BOOT] = value

    @property
    def debug(self) -> bool:
        """Return True if ptvsd is enabled."""
        return self._data[ATTR_DEBUG]

    @debug.setter
    def debug(self, value: bool):
        """Set debug mode."""
        self._data[ATTR_DEBUG] = value

    @property
    def debug_block(self) -> bool:
        """Return True if ptvsd should waiting."""
        return self._data[ATTR_DEBUG_BLOCK]

    @debug_block.setter
    def debug_block(self, value: bool):
        """Set debug wait mode."""
        self._data[ATTR_DEBUG_BLOCK] = value

    @property
    def logging(self) -> str:
        """Return log level of system."""
        return self._data[ATTR_LOGGING]

    @logging.setter
    def logging(self, value: str):
        """Set system log level."""
        self._data[ATTR_LOGGING] = value
        self.modify_log_level()

    def modify_log_level(self) -> None:
        """Change log level."""
        lvl = getattr(logging, self.logging.upper())
        logging.getLogger("supervisor").setLevel(lvl)

    @property
    def last_boot(self):
        """Return last boot datetime."""
        boot_str = self._data.get(ATTR_LAST_BOOT, DEFAULT_BOOT_TIME)

        boot_time = parse_datetime(boot_str)
        if not boot_time:
            return datetime.utcfromtimestamp(1)
        return boot_time

    @last_boot.setter
    def last_boot(self, value):
        """Set last boot datetime."""
        self._data[ATTR_LAST_BOOT] = value.isoformat()

    @property
    def path_hassio(self):
        """Return Supervisor data path."""
        return SUPERVISOR_DATA

    @property
    def path_extern_hassio(self):
        """Return Supervisor data path external for Docker."""
        return PurePath(os.environ["SUPERVISOR_SHARE"])

    @property
    def path_extern_homeassistant(self):
        """Return config path external for Docker."""
        return str(PurePath(self.path_extern_hassio, HOMEASSISTANT_CONFIG))

    @property
    def path_homeassistant(self):
        """Return config path inside supervisor."""
        return Path(SUPERVISOR_DATA, HOMEASSISTANT_CONFIG)

    @property
    def path_extern_ssl(self):
        """Return SSL path external for Docker."""
        return str(PurePath(self.path_extern_hassio, HASSIO_SSL))

    @property
    def path_ssl(self):
        """Return SSL path inside supervisor."""
        return Path(SUPERVISOR_DATA, HASSIO_SSL)

    @property
    def path_addons_core(self):
        """Return git path for core Add-ons."""
        return Path(SUPERVISOR_DATA, ADDONS_CORE)

    @property
    def path_addons_git(self):
        """Return path for Git Add-on."""
        return Path(SUPERVISOR_DATA, ADDONS_GIT)

    @property
    def path_addons_local(self):
        """Return path for custom Add-ons."""
        return Path(SUPERVISOR_DATA, ADDONS_LOCAL)

    @property
    def path_extern_addons_local(self):
        """Return path for custom Add-ons."""
        return PurePath(self.path_extern_hassio, ADDONS_LOCAL)

    @property
    def path_addons_data(self):
        """Return root Add-on data folder."""
        return Path(SUPERVISOR_DATA, ADDONS_DATA)

    @property
    def path_extern_addons_data(self):
        """Return root add-on data folder external for Docker."""
        return PurePath(self.path_extern_hassio, ADDONS_DATA)

    @property
    def path_audio(self):
        """Return root audio data folder."""
        return Path(SUPERVISOR_DATA, AUDIO_DATA)

    @property
    def path_extern_audio(self):
        """Return root audio data folder external for Docker."""
        return PurePath(self.path_extern_hassio, AUDIO_DATA)

    @property
    def path_tmp(self):
        """Return Supervisor temp folder."""
        return Path(SUPERVISOR_DATA, TMP_DATA)

    @property
    def path_extern_tmp(self):
        """Return Supervisor temp folder for Docker."""
        return PurePath(self.path_extern_hassio, TMP_DATA)

    @property
    def path_backup(self):
        """Return root backup data folder."""
        return Path(SUPERVISOR_DATA, BACKUP_DATA)

    @property
    def path_extern_backup(self):
        """Return root backup data folder external for Docker."""
        return PurePath(self.path_extern_hassio, BACKUP_DATA)

    @property
    def path_share(self):
        """Return root share data folder."""
        return Path(SUPERVISOR_DATA, SHARE_DATA)

    @property
    def path_apparmor(self):
        """Return root Apparmor profile folder."""
        return Path(SUPERVISOR_DATA, APPARMOR_DATA)

    @property
    def path_extern_share(self):
        """Return root share data folder external for Docker."""
        return PurePath(self.path_extern_hassio, SHARE_DATA)

    @property
    def path_extern_dns(self):
        """Return dns path external for Docker."""
        return str(PurePath(self.path_extern_hassio, DNS_DATA))

    @property
    def path_dns(self):
        """Return dns path inside supervisor."""
        return Path(SUPERVISOR_DATA, DNS_DATA)

    @property
    def addons_repositories(self):
        """Return list of custom Add-on repositories."""
        return self._data[ATTR_ADDONS_CUSTOM_LIST]

    def add_addon_repository(self, repo):
        """Add a custom repository to list."""
        if repo in self._data[ATTR_ADDONS_CUSTOM_LIST]:
            return

        self._data[ATTR_ADDONS_CUSTOM_LIST].append(repo)

    def drop_addon_repository(self, repo):
        """Remove a custom repository from list."""
        if repo not in self._data[ATTR_ADDONS_CUSTOM_LIST]:
            return

        self._data[ATTR_ADDONS_CUSTOM_LIST].remove(repo)
