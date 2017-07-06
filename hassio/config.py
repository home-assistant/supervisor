"""Bootstrap HassIO."""
from datetime import datetime
import logging
import json
import os
from pathlib import Path, PurePath

import voluptuous as vol
from voluptuous.humanize import humanize_error

from .const import FILE_HASSIO_CONFIG, HASSIO_DATA
from .tools import (
    fetch_last_versions, write_json_file, read_json_file, validate_timezone)
from .validate import hass_devices

_LOGGER = logging.getLogger(__name__)

DATETIME_FORMAT = "%Y%m%d %H:%M:%S"

HOMEASSISTANT_CONFIG = PurePath("homeassistant")
HOMEASSISTANT_LAST = 'homeassistant_last'
HOMEASSISTANT_DEVICES = 'homeassistant_devices'

HASSIO_SSL = PurePath("ssl")
HASSIO_LAST = 'hassio_last'

ADDONS_CORE = PurePath("addons/core")
ADDONS_LOCAL = PurePath("addons/local")
ADDONS_GIT = PurePath("addons/git")
ADDONS_DATA = PurePath("addons/data")
ADDONS_CUSTOM_LIST = 'addons_custom_list'

BACKUP_DATA = PurePath("backup")
SHARE_DATA = PurePath("share")
TMP_DATA = PurePath("tmp")

UPSTREAM_BETA = 'upstream_beta'
API_ENDPOINT = 'api_endpoint'
TIMEZONE = 'timezone'

SECURITY_INITIALIZE = 'security_initialize'
SECURITY_TOTP = 'security_totp'
SECURITY_PASSWORD = 'security_password'
SECURITY_SESSIONS = 'security_sessions'


# pylint: disable=no-value-for-parameter
SCHEMA_CONFIG = vol.Schema({
    vol.Optional(UPSTREAM_BETA, default=False): vol.Boolean(),
    vol.Optional(API_ENDPOINT): vol.Coerce(str),
    vol.Optional(TIMEZONE, default='UTC'): validate_timezone,
    vol.Optional(HOMEASSISTANT_LAST): vol.Coerce(str),
    vol.Optional(HOMEASSISTANT_DEVICES, default=[]): hass_devices,
    vol.Optional(HASSIO_LAST): vol.Coerce(str),
    vol.Optional(ADDONS_CUSTOM_LIST, default=[]): [vol.Url()],
    vol.Optional(SECURITY_INITIALIZE, default=False): vol.Boolean(),
    vol.Optional(SECURITY_TOTP): vol.Coerce(str),
    vol.Optional(SECURITY_PASSWORD): vol.Coerce(str),
    vol.Optional(SECURITY_SESSIONS, default={}):
        {vol.Coerce(str): vol.Coerce(str)},
}, extra=vol.REMOVE_EXTRA)


class CoreConfig(object):
    """Hold all core config data."""

    def __init__(self):
        """Initialize config object."""
        self.arch = None
        self._file = FILE_HASSIO_CONFIG
        self._data = {}

        # init or load data
        if self._file.is_file():
            try:
                self._data = read_json_file(self._file)
            except (OSError, json.JSONDecodeError):
                _LOGGER.warning("Can't read %s", self._file)
                self._data = {}

        # validate data
        if not self._validate_config():
            self._data = SCHEMA_CONFIG({})

    def _validate_config(self):
        """Validate config and return True or False."""
        # validate data
        try:
            self._data = SCHEMA_CONFIG(self._data)
        except vol.Invalid as ex:
            _LOGGER.warning(
                "Invalid config %s", humanize_error(self._data, ex))
            return False

        return True

    def save(self):
        """Store data to config file."""
        if not self._validate_config():
            return False

        if not write_json_file(self._file, self._data):
            _LOGGER.error("Can't store config in %s", self._file)
            return False
        return True

    async def fetch_update_infos(self, websession):
        """Read current versions from web."""
        last = await fetch_last_versions(websession, beta=self.upstream_beta)

        if last:
            self._data.update({
                HOMEASSISTANT_LAST: last.get('homeassistant'),
                HASSIO_LAST: last.get('hassio'),
            })
            self.save()
            return True

        return False

    @property
    def api_endpoint(self):
        """Return IP address of api endpoint."""
        return self._data[API_ENDPOINT]

    @api_endpoint.setter
    def api_endpoint(self, value):
        """Store IP address of api endpoint."""
        self._data[API_ENDPOINT] = value

    @property
    def upstream_beta(self):
        """Return True if we run in beta upstream."""
        return self._data[UPSTREAM_BETA]

    @upstream_beta.setter
    def upstream_beta(self, value):
        """Set beta upstream mode."""
        self._data[UPSTREAM_BETA] = bool(value)
        self.save()

    @property
    def timezone(self):
        """Return system timezone."""
        return self._data[TIMEZONE]

    @timezone.setter
    def timezone(self, value):
        """Set system timezone."""
        self._data[TIMEZONE] = value
        self.save()

    @property
    def homeassistant_devices(self):
        """Return list of special device to map into homeassistant."""
        return self._data[HOMEASSISTANT_DEVICES]

    @homeassistant_devices.setter
    def homeassistant_devices(self, value):
        """Set list of special device."""
        self._data[HOMEASSISTANT_DEVICES] = value
        self.save()

    @property
    def homeassistant_image(self):
        """Return docker homeassistant repository."""
        return os.environ['HOMEASSISTANT_REPOSITORY']

    @property
    def last_homeassistant(self):
        """Actual version of homeassistant."""
        return self._data.get(HOMEASSISTANT_LAST)

    @property
    def last_hassio(self):
        """Actual version of hassio."""
        return self._data.get(HASSIO_LAST)

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
        return self._data[ADDONS_CUSTOM_LIST]

    @addons_repositories.setter
    def addons_repositories(self, repo):
        """Add a custom repository to list."""
        if repo in self._data[ADDONS_CUSTOM_LIST]:
            return

        self._data[ADDONS_CUSTOM_LIST].append(repo)
        self.save()

    def drop_addon_repository(self, repo):
        """Remove a custom repository from list."""
        if repo not in self._data[ADDONS_CUSTOM_LIST]:
            return

        self._data[ADDONS_CUSTOM_LIST].remove(repo)
        self.save()

    @property
    def security_initialize(self):
        """Return is security was initialize."""
        return self._data[SECURITY_INITIALIZE]

    @security_initialize.setter
    def security_initialize(self, value):
        """Set is security initialize."""
        self._data[SECURITY_INITIALIZE] = value
        self.save()

    @property
    def security_totp(self):
        """Return the TOTP key."""
        return self._data.get(SECURITY_TOTP)

    @security_totp.setter
    def security_totp(self, value):
        """Set the TOTP key."""
        self._data[SECURITY_TOTP] = value
        self.save()

    @property
    def security_password(self):
        """Return the password key."""
        return self._data.get(SECURITY_PASSWORD)

    @security_password.setter
    def security_password(self, value):
        """Set the password key."""
        self._data[SECURITY_PASSWORD] = value
        self.save()

    @property
    def security_sessions(self):
        """Return api sessions."""
        return {session: datetime.strptime(until, DATETIME_FORMAT) for
                session, until in self._data[SECURITY_SESSIONS].items()}

    @security_sessions.setter
    def security_sessions(self, value):
        """Set the a new session."""
        session, valid = value
        if valid is None:
            self._data[SECURITY_SESSIONS].pop(session, None)
        else:
            self._data[SECURITY_SESSIONS].update(
                {session: valid.strftime(DATETIME_FORMAT)}
            )

        self.save()
