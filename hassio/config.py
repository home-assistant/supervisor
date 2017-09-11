"""Bootstrap HassIO."""
from datetime import datetime
import logging
import os
from pathlib import Path, PurePath

from .const import (
    FILE_HASSIO_CONFIG, HASSIO_DATA, ATTR_SECURITY, ATTR_SESSIONS,
    ATTR_PASSWORD, ATTR_TOTP, ATTR_TIMEZONE, ATTR_ADDONS_CUSTOM_LIST,
    ATTR_AUDIO_INPUT, ATTR_AUDIO_OUTPUT, ATTR_LAST_BOOT)
from .tools import JsonConfig, parse_datetime
from .validate import SCHEMA_HASSIO_CONFIG

_LOGGER = logging.getLogger(__name__)

DATETIME_FORMAT = "%Y%m%d %H:%M:%S"

HOMEASSISTANT_CONFIG = PurePath("homeassistant")

HASSIO_SSL = PurePath("ssl")

ADDONS_CORE = PurePath("addons/core")
ADDONS_LOCAL = PurePath("addons/local")
ADDONS_GIT = PurePath("addons/git")
ADDONS_DATA = PurePath("addons/data")

BACKUP_DATA = PurePath("backup")
SHARE_DATA = PurePath("share")
TMP_DATA = PurePath("tmp")


class CoreConfig(JsonConfig):
    """Hold all core config data."""

    def __init__(self):
        """Initialize config object."""
        super().__init__(FILE_HASSIO_CONFIG, SCHEMA_HASSIO_CONFIG)
        self.arch = None

    @property
    def timezone(self):
        """Return system timezone."""
        return self._data[ATTR_TIMEZONE]

    @timezone.setter
    def timezone(self, value):
        """Set system timezone."""
        self._data[ATTR_TIMEZONE] = value
        self.save()

    @property
    def last_boot(self):
        """Return last boot datetime."""
        boot_str = self._data.get(ATTR_LAST_BOOT, "")

        boot_time = parse_datetime(boot_str)
        if not boot_time:
            return datetime.utcfromtimestamp(1)
        return boot_time

    @last_boot.setter
    def last_boot(self, value):
        """Set last boot datetime."""
        self._data[ATTR_LAST_BOOT] = value.isoformat()
        self.save()

    @property
    def path_hassio(self):
        """Return hassio data path."""
        return HASSIO_DATA

    @property
    def path_extern_hassio(self):
        """Return hassio data path extern for docker."""
        return PurePath(os.environ['SUPERVISOR_SHARE'])

    @property
    def path_extern_config(self):
        """Return config path extern for docker."""
        return str(PurePath(self.path_extern_hassio, HOMEASSISTANT_CONFIG))

    @property
    def path_config(self):
        """Return config path inside supervisor."""
        return Path(HASSIO_DATA, HOMEASSISTANT_CONFIG)

    @property
    def path_extern_ssl(self):
        """Return SSL path extern for docker."""
        return str(PurePath(self.path_extern_hassio, HASSIO_SSL))

    @property
    def path_ssl(self):
        """Return SSL path inside supervisor."""
        return Path(HASSIO_DATA, HASSIO_SSL)

    @property
    def path_addons_core(self):
        """Return git path for core addons."""
        return Path(HASSIO_DATA, ADDONS_CORE)

    @property
    def path_addons_git(self):
        """Return path for git addons."""
        return Path(HASSIO_DATA, ADDONS_GIT)

    @property
    def path_addons_local(self):
        """Return path for customs addons."""
        return Path(HASSIO_DATA, ADDONS_LOCAL)

    @property
    def path_extern_addons_local(self):
        """Return path for customs addons."""
        return PurePath(self.path_extern_hassio, ADDONS_LOCAL)

    @property
    def path_addons_data(self):
        """Return root addon data folder."""
        return Path(HASSIO_DATA, ADDONS_DATA)

    @property
    def path_extern_addons_data(self):
        """Return root addon data folder extern for docker."""
        return PurePath(self.path_extern_hassio, ADDONS_DATA)

    @property
    def path_tmp(self):
        """Return hass.io temp folder."""
        return Path(HASSIO_DATA, TMP_DATA)

    @property
    def path_backup(self):
        """Return root backup data folder."""
        return Path(HASSIO_DATA, BACKUP_DATA)

    @property
    def path_extern_backup(self):
        """Return root backup data folder extern for docker."""
        return PurePath(self.path_extern_hassio, BACKUP_DATA)

    @property
    def path_share(self):
        """Return root share data folder."""
        return Path(HASSIO_DATA, SHARE_DATA)

    @property
    def path_extern_share(self):
        """Return root share data folder extern for docker."""
        return PurePath(self.path_extern_hassio, SHARE_DATA)

    @property
    def addons_repositories(self):
        """Return list of addons custom repositories."""
        return self._data[ATTR_ADDONS_CUSTOM_LIST]

    def add_addon_repository(self, repo):
        """Add a custom repository to list."""
        if repo in self._data[ATTR_ADDONS_CUSTOM_LIST]:
            return

        self._data[ATTR_ADDONS_CUSTOM_LIST].append(repo)
        self.save()

    def drop_addon_repository(self, repo):
        """Remove a custom repository from list."""
        if repo not in self._data[ATTR_ADDONS_CUSTOM_LIST]:
            return

        self._data[ATTR_ADDONS_CUSTOM_LIST].remove(repo)
        self.save()

    @property
    def security_initialize(self):
        """Return is security was initialize."""
        return self._data[ATTR_SECURITY]

    @security_initialize.setter
    def security_initialize(self, value):
        """Set is security initialize."""
        self._data[ATTR_SECURITY] = value
        self.save()

    @property
    def security_totp(self):
        """Return the TOTP key."""
        return self._data.get(ATTR_TOTP)

    @security_totp.setter
    def security_totp(self, value):
        """Set the TOTP key."""
        self._data[ATTR_TOTP] = value
        self.save()

    @property
    def security_password(self):
        """Return the password key."""
        return self._data.get(ATTR_PASSWORD)

    @security_password.setter
    def security_password(self, value):
        """Set the password key."""
        self._data[ATTR_PASSWORD] = value
        self.save()

    @property
    def security_sessions(self):
        """Return api sessions."""
        return {
            session: datetime.strptime(until, DATETIME_FORMAT) for
            session, until in self._data[ATTR_SESSIONS].items()
        }

    def add_security_session(self, session, valid):
        """Set the a new session."""
        self._data[ATTR_SESSIONS].update(
            {session: valid.strftime(DATETIME_FORMAT)}
        )
        self.save()

    def drop_security_session(self, session):
        """Delete the a session."""
        self._data[ATTR_SESSIONS].pop(session, None)
        self.save()

    @property
    def audio_output(self):
        """Return ALSA audio output card,dev."""
        return self._data.get(ATTR_AUDIO_OUTPUT)

    @audio_output.setter
    def audio_output(self, value):
        """Set ALSA audio output card,dev."""
        self._data[ATTR_AUDIO_OUTPUT] = value
        self.save()

    @property
    def audio_input(self):
        """Return ALSA audio input card,dev."""
        return self._data.get(ATTR_AUDIO_INPUT)

    @audio_input.setter
    def audio_input(self, value):
        """Set ALSA audio input card,dev."""
        self._data[ATTR_AUDIO_INPUT] = value
        self.save()
