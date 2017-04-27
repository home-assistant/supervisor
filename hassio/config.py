"""Bootstrap HassIO."""
import logging
import os

import voluptuous as vol
from voluptuous.humanize import humanize_error

from .const import FILE_HASSIO_CONFIG, HASSIO_SHARE
from .tools import (
    fetch_current_versions, write_json_file, read_json_file)

_LOGGER = logging.getLogger(__name__)

HOMEASSISTANT_CONFIG = "{}/homeassistant"
HOMEASSISTANT_IMAGE = 'homeassistant_image'
HOMEASSISTANT_LAST = 'homeassistant_last'

HASSIO_SSL = "{}/ssl"
HASSIO_LAST = 'hassio_last'
HASSIO_CLEANUP = 'hassio_cleanup'

ADDONS_REPO = "{}/addons"
ADDONS_DATA = "{}/addons_data"
ADDONS_CUSTOM = "{}/addons_custom"
ADDONS_CUSTOM_LIST = 'addons_custom_list'

BACKUP_DATA = "{}/backup"

UPSTREAM_BETA = 'upstream_beta'

API_ENDPOINT = 'api_endpoint'


SCHEMA_CONFIG = vol.Schema({
    vol.Optional(
        HOMEASSISTANT_IMAGE,
        default=os.environ.get('HOMEASSISTANT_REPOSITORY'):
            vol.Coerce(str),
    vol.Optional(UPSTREAM_BETA, default=False): vol.Boolean(),
    vol.Optional(API_ENDPOINT): vol.Coerce(str),
    vol.Optional(HOMEASSISTANT_LAST): vol.Coerce(str),
    vol.Optional(HASSIO_LAST): vol.Coerce(str),
    vol.Optional(HASSIO_CLEANUP): vol.Coerce(str),
    vol.Optional(ADDONS_CUSTOM_LIST, default={}): {
        vol.Url(): vol.Coerce(str),
    }
}, extra=vol.REMOVE_EXTRA)


class Config(object):
    """Hold all config data."""

    def __init__(self, config_file):
        """Initialize config object."""
        self._filename = config_file
        self._data = {}

        # init or load data
        if os.path.isfile(self._filename):
            try:
                self._data = read_json_file(self._filename)
            except OSError:
                _LOGGER.warning("Can't read %s", self._filename)

    def save(self):
        """Store data to config file."""
        if not write_json_file(self._filename, self._data):
            _LOGGER.exception("Can't store config in %s", self._filename)
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
        last = await fetch_current_versions(
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
        return self._data.get(HOMEASSISTANT_IMAGE)

    @property
    def last_homeassistant(self):
        """Actual version of homeassistant."""
        return self._data.get(HOMEASSISTANT_LAST)

    @property
    def last_hassio(self):
        """Actual version of hassio."""
        return self._data.get(HASSIO_LAST)

    @property
    def path_hassio_docker(self):
        """Return hassio data path extern for docker."""
        return os.environ['SUPERVISOR_SHARE']

    @property
    def path_config_docker(self):
        """Return config path extern for docker."""
        return HOMEASSISTANT_CONFIG.format(self.path_hassio_docker)

    @property
    def path_config(self):
        """Return config path inside supervisor."""
        return HOMEASSISTANT_CONFIG.format(HASSIO_SHARE)

    @property
    def path_ssl_docker(self):
        """Return SSL path extern for docker."""
        return HASSIO_SSL.format(self.path_hassio_docker)

    @property
    def path_ssl(self):
        """Return SSL path inside supervisor."""
        return HASSIO_SSL.format(HASSIO_SHARE)

    @property
    def path_addons_repo(self):
        """Return git repo path for addons."""
        return ADDONS_REPO.format(HASSIO_SHARE)

    @property
    def path_addons_custom(self):
        """Return path for customs addons."""
        return ADDONS_CUSTOM.format(HASSIO_SHARE)

    @property
    def path_addons_custom_docker(self):
        """Return path for customs addons."""
        return ADDONS_CUSTOM.format(self.path_hassio_docker)

    @property
    def path_addons_data(self):
        """Return root addon data folder."""
        return ADDONS_DATA.format(HASSIO_SHARE)

    @property
    def path_addons_data_docker(self):
        """Return root addon data folder extern for docker."""
        return ADDONS_DATA.format(self.path_hassio_docker)

    @property
    def path_backup(self):
        """Return root backup data folder."""
        return BACKUP_DATA.format(HASSIO_SHARE)

    @property
    def path_backup_docker(self):
        """Return root backup data folder extern for docker."""
        return BACKUP_DATA.format(self.path_hassio_docker)

    def add_addons_repository(self, repo, slug):
        """Add a custom repository to list."""
        self._data[ADDONS_CUSTOM_LIST][repo][slug]
        self.save()

    def drop_addons_repository(self, repo):
        """Remove a custom repository from list."""
        if self._data[ADDONS_CUSTOM_LIST].pop(repo, None):
            self.save()

    @property
    def addons_repositories(self):
        """Return list of addons custom repositories."""
        return self._data[ADDONS_CUSTOM_LIST]
