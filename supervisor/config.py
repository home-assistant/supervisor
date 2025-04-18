"""Bootstrap Supervisor."""

import asyncio
from datetime import UTC, datetime, tzinfo
import logging
import os
from pathlib import Path, PurePath

from awesomeversion import AwesomeVersion

from .const import (
    ATTR_ADDONS_CUSTOM_LIST,
    ATTR_COUNTRY,
    ATTR_DEBUG,
    ATTR_DEBUG_BLOCK,
    ATTR_DETECT_BLOCKING_IO,
    ATTR_DIAGNOSTICS,
    ATTR_IMAGE,
    ATTR_LAST_BOOT,
    ATTR_LOGGING,
    ATTR_TIMEZONE,
    ATTR_VERSION,
    ATTR_WAIT_BOOT,
    ENV_SUPERVISOR_SHARE,
    FILE_HASSIO_CONFIG,
    SUPERVISOR_DATA,
    LogLevel,
)
from .utils.common import FileConfiguration
from .utils.dt import get_time_zone, parse_datetime
from .validate import SCHEMA_SUPERVISOR_CONFIG

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
APPARMOR_CACHE = PurePath("apparmor/cache")
DNS_DATA = PurePath("dns")
AUDIO_DATA = PurePath("audio")
MEDIA_DATA = PurePath("media")
MOUNTS_FOLDER = PurePath("mounts")
MOUNTS_CREDENTIALS = PurePath(".mounts_credentials")
EMERGENCY_DATA = PurePath("emergency")
ADDON_CONFIGS = PurePath("addon_configs")
CORE_BACKUP_DATA = PurePath("core/backup")

DEFAULT_BOOT_TIME = datetime.fromtimestamp(0, UTC).isoformat()

# We filter out UTC because it's the system default fallback
# Core also not respect the cotnainer timezone and reset timezones
# to UTC if the user overflight the onboarding.
_UTC = "UTC"


class CoreConfig(FileConfiguration):
    """Hold all core config data."""

    def __init__(self):
        """Initialize config object."""
        super().__init__(FILE_HASSIO_CONFIG, SCHEMA_SUPERVISOR_CONFIG)
        self._timezone_tzinfo: tzinfo | None = None

    @property
    def timezone(self) -> str | None:
        """Return system timezone."""
        timezone = self._data.get(ATTR_TIMEZONE)
        if timezone != _UTC:
            return timezone
        self._data.pop(ATTR_TIMEZONE, None)
        return None

    @property
    def timezone_tzinfo(self) -> tzinfo | None:
        """Return system timezone as tzinfo object."""
        return self._timezone_tzinfo

    async def set_timezone(self, value: str) -> None:
        """Set system timezone."""
        if value == _UTC:
            return
        self._data[ATTR_TIMEZONE] = value
        self._timezone_tzinfo = await asyncio.get_running_loop().run_in_executor(
            None, get_time_zone, value
        )

    @property
    def country(self) -> str | None:
        """Return supervisor country.

        The format follows what Home Assistant Core provides, which today is
        ISO 3166-1 alpha-2.
        """
        return self._data.get(ATTR_COUNTRY)

    @country.setter
    def country(self, value: str | None) -> None:
        """Set supervisor country."""
        self._data[ATTR_COUNTRY] = value

    @property
    def version(self) -> AwesomeVersion:
        """Return supervisor version."""
        return self._data[ATTR_VERSION]

    @version.setter
    def version(self, value: AwesomeVersion) -> None:
        """Set supervisor version."""
        self._data[ATTR_VERSION] = value

    @property
    def image(self) -> str | None:
        """Return supervisor image."""
        return self._data.get(ATTR_IMAGE)

    @image.setter
    def image(self, value: str) -> None:
        """Set supervisor image."""
        self._data[ATTR_IMAGE] = value

    @property
    def wait_boot(self) -> int:
        """Return wait time for auto boot stages."""
        return self._data[ATTR_WAIT_BOOT]

    @wait_boot.setter
    def wait_boot(self, value: int) -> None:
        """Set wait boot time."""
        self._data[ATTR_WAIT_BOOT] = value

    @property
    def debug(self) -> bool:
        """Return True if ptvsd is enabled."""
        return self._data[ATTR_DEBUG]

    @debug.setter
    def debug(self, value: bool) -> None:
        """Set debug mode."""
        self._data[ATTR_DEBUG] = value

    @property
    def debug_block(self) -> bool:
        """Return True if ptvsd should waiting."""
        return self._data[ATTR_DEBUG_BLOCK]

    @debug_block.setter
    def debug_block(self, value: bool) -> None:
        """Set debug wait mode."""
        self._data[ATTR_DEBUG_BLOCK] = value

    @property
    def detect_blocking_io(self) -> bool:
        """Return True if blocking I/O in event loop detection enabled at startup."""
        return self._data[ATTR_DETECT_BLOCKING_IO]

    @detect_blocking_io.setter
    def detect_blocking_io(self, value: bool) -> None:
        """Enable/Disable blocking I/O in event loop detection at startup."""
        self._data[ATTR_DETECT_BLOCKING_IO] = value

    @property
    def diagnostics(self) -> bool | None:
        """Return bool if diagnostics is set otherwise None."""
        return self._data[ATTR_DIAGNOSTICS]

    @diagnostics.setter
    def diagnostics(self, value: bool) -> None:
        """Set diagnostics settings."""
        self._data[ATTR_DIAGNOSTICS] = value

    @property
    def logging(self) -> LogLevel:
        """Return log level of system."""
        return self._data[ATTR_LOGGING]

    @logging.setter
    def logging(self, value: LogLevel) -> None:
        """Set system log level."""
        self._data[ATTR_LOGGING] = value
        self.modify_log_level()

    def modify_log_level(self) -> None:
        """Change log level."""
        lvl = getattr(logging, self.logging.value.upper())
        logging.getLogger("supervisor").setLevel(lvl)

    @property
    def last_boot(self) -> datetime:
        """Return last boot datetime."""
        boot_str = self._data.get(ATTR_LAST_BOOT, DEFAULT_BOOT_TIME)

        boot_time = parse_datetime(boot_str)
        if not boot_time:
            return datetime.fromtimestamp(1, UTC)
        return boot_time

    @last_boot.setter
    def last_boot(self, value: datetime) -> None:
        """Set last boot datetime."""
        self._data[ATTR_LAST_BOOT] = value.isoformat()

    @property
    def path_supervisor(self) -> Path:
        """Return Supervisor data path."""
        return SUPERVISOR_DATA

    @property
    def path_extern_supervisor(self) -> PurePath:
        """Return Supervisor data path external for Docker."""
        return PurePath(os.environ[ENV_SUPERVISOR_SHARE])

    @property
    def path_extern_homeassistant(self) -> PurePath:
        """Return config path external for Docker."""
        return PurePath(self.path_extern_supervisor, HOMEASSISTANT_CONFIG)

    @property
    def path_homeassistant(self) -> Path:
        """Return config path inside supervisor."""
        return self.path_supervisor / HOMEASSISTANT_CONFIG

    @property
    def path_extern_ssl(self) -> PurePath:
        """Return SSL path external for Docker."""
        return PurePath(self.path_extern_supervisor, HASSIO_SSL)

    @property
    def path_ssl(self) -> Path:
        """Return SSL path inside supervisor."""
        return self.path_supervisor / HASSIO_SSL

    @property
    def path_addons_core(self) -> Path:
        """Return git path for core Add-ons."""
        return self.path_supervisor / ADDONS_CORE

    @property
    def path_addons_git(self) -> Path:
        """Return path for Git Add-on."""
        return self.path_supervisor / ADDONS_GIT

    @property
    def path_addons_local(self) -> Path:
        """Return path for custom Add-ons."""
        return self.path_supervisor / ADDONS_LOCAL

    @property
    def path_extern_addons_local(self) -> PurePath:
        """Return path for custom Add-ons."""
        return PurePath(self.path_extern_supervisor, ADDONS_LOCAL)

    @property
    def path_addons_data(self) -> Path:
        """Return root Add-on data folder."""
        return self.path_supervisor / ADDONS_DATA

    @property
    def path_extern_addons_data(self) -> PurePath:
        """Return root add-on data folder external for Docker."""
        return PurePath(self.path_extern_supervisor, ADDONS_DATA)

    @property
    def path_addon_configs(self) -> Path:
        """Return root Add-on configs folder."""
        return self.path_supervisor / ADDON_CONFIGS

    @property
    def path_extern_addon_configs(self) -> PurePath:
        """Return root Add-on configs folder external for Docker."""
        return PurePath(self.path_extern_supervisor, ADDON_CONFIGS)

    @property
    def path_audio(self) -> Path:
        """Return root audio data folder."""
        return self.path_supervisor / AUDIO_DATA

    @property
    def path_extern_audio(self) -> PurePath:
        """Return root audio data folder external for Docker."""
        return PurePath(self.path_extern_supervisor, AUDIO_DATA)

    @property
    def path_tmp(self) -> Path:
        """Return Supervisor temp folder."""
        return self.path_supervisor / TMP_DATA

    @property
    def path_extern_tmp(self) -> PurePath:
        """Return Supervisor temp folder for Docker."""
        return PurePath(self.path_extern_supervisor, TMP_DATA)

    @property
    def path_backup(self) -> Path:
        """Return root backup data folder."""
        return self.path_supervisor / BACKUP_DATA

    @property
    def path_extern_backup(self) -> PurePath:
        """Return root backup data folder external for Docker."""
        return PurePath(self.path_extern_supervisor, BACKUP_DATA)

    @property
    def path_core_backup(self) -> Path:
        """Return core specific backup folder (cloud backup)."""
        return self.path_supervisor / CORE_BACKUP_DATA

    @property
    def path_extern_core_backup(self) -> PurePath:
        """Return core specific backup folder (cloud backup) external for Docker."""
        return PurePath(self.path_extern_supervisor, CORE_BACKUP_DATA)

    @property
    def path_share(self) -> Path:
        """Return root share data folder."""
        return self.path_supervisor / SHARE_DATA

    @property
    def path_apparmor(self) -> Path:
        """Return root Apparmor profile folder."""
        return self.path_supervisor / APPARMOR_DATA

    @property
    def path_apparmor_cache(self) -> Path:
        """Return root Apparmor cache folder."""
        return self.path_supervisor / APPARMOR_CACHE

    @property
    def path_extern_apparmor(self) -> Path:
        """Return root Apparmor profile folder external."""
        return Path(self.path_extern_supervisor, APPARMOR_DATA)

    @property
    def path_extern_apparmor_cache(self) -> Path:
        """Return root Apparmor cache folder external."""
        return Path(self.path_extern_supervisor, APPARMOR_CACHE)

    @property
    def path_extern_share(self) -> PurePath:
        """Return root share data folder external for Docker."""
        return PurePath(self.path_extern_supervisor, SHARE_DATA)

    @property
    def path_extern_dns(self) -> PurePath:
        """Return dns path external for Docker."""
        return PurePath(self.path_extern_supervisor, DNS_DATA)

    @property
    def path_dns(self) -> Path:
        """Return dns path inside supervisor."""
        return self.path_supervisor / DNS_DATA

    @property
    def path_media(self) -> Path:
        """Return root media data folder."""
        return self.path_supervisor / MEDIA_DATA

    @property
    def path_mounts(self) -> Path:
        """Return root mounts folder."""
        return self.path_supervisor / MOUNTS_FOLDER

    @property
    def path_extern_mounts(self) -> PurePath:
        """Return mounts path external for Docker."""
        return self.path_extern_supervisor / MOUNTS_FOLDER

    @property
    def path_mounts_credentials(self) -> Path:
        """Return mounts credentials folder."""
        return self.path_supervisor / MOUNTS_CREDENTIALS

    @property
    def path_extern_mounts_credentials(self) -> PurePath:
        """Return mounts credentials path external for Docker."""
        return self.path_extern_supervisor / MOUNTS_CREDENTIALS

    @property
    def path_emergency(self) -> Path:
        """Return emergency data folder."""
        return self.path_supervisor / EMERGENCY_DATA

    @property
    def path_extern_emergency(self) -> PurePath:
        """Return emergency path external for Docker."""
        return self.path_extern_supervisor / EMERGENCY_DATA

    @property
    def path_extern_media(self) -> PurePath:
        """Return root media data folder external for Docker."""
        return PurePath(self.path_extern_supervisor, MEDIA_DATA)

    @property
    def addons_repositories(self) -> list[str]:
        """Return list of custom Add-on repositories."""
        return self._data[ATTR_ADDONS_CUSTOM_LIST]

    def add_addon_repository(self, repo: str) -> None:
        """Add a custom repository to list."""
        if repo in self._data[ATTR_ADDONS_CUSTOM_LIST]:
            return

        self._data[ATTR_ADDONS_CUSTOM_LIST].append(repo)

    def drop_addon_repository(self, repo: str) -> None:
        """Remove a custom repository from list."""
        if repo not in self._data[ATTR_ADDONS_CUSTOM_LIST]:
            return

        self._data[ATTR_ADDONS_CUSTOM_LIST].remove(repo)

    def local_to_extern_path(self, path: PurePath) -> PurePath:
        """Translate a path relative to supervisor data in the container to its extern path."""
        return self.path_extern_supervisor / path.relative_to(self.path_supervisor)

    def extern_to_local_path(self, path: PurePath) -> Path:
        """Translate a path relative to extern supervisor data to its path in the container."""
        return self.path_supervisor / path.relative_to(self.path_extern_supervisor)

    async def read_data(self) -> None:
        """Read configuration file."""
        timezone = self.timezone
        await super().read_data()

        if not self.timezone:
            self._timezone_tzinfo = None
        elif timezone != self.timezone:
            self._timezone_tzinfo = await asyncio.get_running_loop().run_in_executor(
                None, get_time_zone, self.timezone
            )
