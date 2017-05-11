"""Bootstrap HassIO."""
from datetime import datetime
import logging
import json
import os
from pathlib import Path, PurePath

import voluptuous as vol
from voluptuous.humanize import humanize_error

from .const import FILE_HASSIO_CONFIG, HASSIO_SHARE
from .tools import (
    fetch_last_versions, write_json_file, read_json_file)

_LOGGER = logging.getLogger(__name__)

DATETIME_FORMAT = "%Y%m%d %H:%M:%S"

HOMEASSISTANT_CONFIG = PurePath("homeassistant")
HOMEASSISTANT_LAST = 'homeassistant_last'

HASSIO_SSL = PurePath("ssl")
HASSIO_LAST = 'hassio_last'
HASSIO_CLEANUP = 'hassio_cleanup'

ADDONS_CORE = PurePath("addons/core")
ADDONS_LOCAL = PurePath("addons/local")
ADDONS_GIT = PurePath("addons/git")
ADDONS_DATA = PurePath("addons/data")
ADDONS_BUILD = PurePath("addons/build")
ADDONS_CUSTOM_LIST = 'addons_custom_list'

BACKUP_DATA = PurePath("backup")

UPSTREAM_BETA = 'upstream_beta'

API_ENDPOINT = 'api_endpoint'

SECURITY_INITIALIZE = 'security_initialize'
SECURITY_TOTP = 'security_totp'
SECURITY_PASSWORD = 'security_password'
SECURITY_SESSIONS = 'security_sessions'


# pylint: disable=no-value-for-parameter
SCHEMA_CONFIG = vol.Schema({
    vol.Optional(UPSTREAM_BETA, default=False): vol.Boolean(),
    vol.Optional(API_ENDPOINT): vol.Coerce(str),
    vol.Optional(HOMEASSISTANT_LAST): vol.Coerce(str),
    vol.Optional(HASSIO_LAST): vol.Coerce(str),
    vol.Optional(HASSIO_CLEANUP): vol.Coerce(str),
    vol.Optional(ADDONS_CUSTOM_LIST, default=[]): [vol.Url()],
    vol.Optional(SECURITY_INITIALIZE, default=False): vol.Boolean(),
    vol.Optional(SECURITY_TOTP): vol.Coerce(str),
    vol.Optional(SECURITY_PASSWORD): vol.Coerce(str),
    vol.Optional(SECURITY_SESSIONS, default={}):
        {vol.Coerce(str): vol.Coerce(str)},
}, extra=vol.REMOVE_EXTRA)


class Config(object):
    """Hold all config data."""

    def __init__(self, config_file):
        """Initialize config object."""
        self._file = config_file
        self._data = {}

        # init or load data
        if self._file.is_file():
            try:
                self._data = read_json_file(self._file)
            except (OSError, json.JSONDecodeError):
                _LOGGER.warning("Can't read %s", self._file)
                self._data = {}

    def save(self):
        """Store data to config file."""
        if not write_json_file(self._file, self._data):
            _LOGGER.error("Can't store config in %s", self._file)
            return False
        return True


class CoreConfig(Config):
    """Hold all core config data."""

    def __init__(self, websession):
        """Initialize config object."""
        self.websession = websession

        super().__init__(FILE_HASSIO_CONFIG)

        # validate data
        try:
            self._data = SCHEMA_CONFIG(self._data)
            self.save()
        except vol.Invalid as ex:
            _LOGGER.warning(
                "Invalid config %s", humanize_error(self._data, ex))

    async def fetch_update_infos(self):
        """Read current versions from web."""
        last = await fetch_last_versions(
            self.websession, beta=self.upstream_beta)

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

    @property
    def hassio_cleanup(self):
        """Return Version they need to cleanup."""
        return self._data.get(HASSIO_CLEANUP)

    @hassio_cleanup.setter
    def hassio_cleanup(self, version):
        """Set or remove cleanup flag."""
        if version is None:
            self._data.pop(HASSIO_CLEANUP, None)
        else:
            self._data[HASSIO_CLEANUP] = version
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
        return Path(HASSIO_SHARE, HOMEASSISTANT_CONFIG)

    @property
    def path_extern_ssl(self):
        """Return SSL path extern for docker."""
        return str(PurePath(self.path_extern_hassio, HASSIO_SSL))

    @property
    def path_ssl(self):
        """Return SSL path inside supervisor."""
        return Path(HASSIO_SHARE, HASSIO_SSL)

    @property
    def path_addons_core(self):
        """Return git path for core addons."""
        return Path(HASSIO_SHARE, ADDONS_CORE)

    @property
    def path_addons_git(self):
        """Return path for git addons."""
        return Path(HASSIO_SHARE, ADDONS_GIT)

    @property
    def path_addons_local(self):
        """Return path for customs addons."""
        return Path(HASSIO_SHARE, ADDONS_LOCAL)

    @property
    def path_extern_addons_local(self):
        """Return path for customs addons."""
        return PurePath(self.path_extern_hassio, ADDONS_LOCAL)

    @property
    def path_addons_data(self):
        """Return root addon data folder."""
        return Path(HASSIO_SHARE, ADDONS_DATA)

    @property
    def path_extern_addons_data(self):
        """Return root addon data folder extern for docker."""
        return PurePath(self.path_extern_hassio, ADDONS_DATA)

    @property
    def path_addons_build(self):
        """Return root addon build folder."""
        return Path(HASSIO_SHARE, ADDONS_BUILD)

    @property
    def path_extern_addons_build(self):
        """Return root addon build folder extern for docker."""
        return PurePath(self.path_extern_hassio, ADDONS_BUILD)

    @property
    def path_backup(self):
        """Return root backup data folder."""
        return Path(HASSIO_SHARE, BACKUP_DATA)

    @property
    def path_extern_backup(self):
        """Return root backup data folder extern for docker."""
        return PurePath(self.path_extern_hassio, BACKUP_DATA)

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
