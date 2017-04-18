"""Bootstrap HassIO."""
import logging
import os

from .const import FILE_HASSIO_CONFIG, HASSIO_SHARE
from .tools import (
    fetch_current_versions, write_json_file, read_json_file)

_LOGGER = logging.getLogger(__name__)

HOMEASSISTANT_CONFIG = "{}/homeassistant_config"
HOMEASSISTANT_IMAGE = 'homeassistant_image'
HOMEASSISTANT_CURRENT = 'homeassistant_current'

HASSIO_SSL = "{}/ssl"
HASSIO_CURRENT = 'hassio_current'
HASSIO_CLEANUP = 'hassio_cleanup'

ADDONS_REPO = "{}/addons"
ADDONS_DATA = "{}/addons_data"
ADDONS_CUSTOM = "{}/addons_custom"

UPSTREAM_BETA = 'upstream_beta'


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

        # init data
        if not self._data:
            self._data.update({
                HOMEASSISTANT_IMAGE: os.environ['HOMEASSISTANT_REPOSITORY'],
                UPSTREAM_BETA: False,
            })
            self.save()

    async def fetch_update_infos(self):
        """Read current versions from web."""
        current = await fetch_current_versions(
            self.websession, beta=self.upstream_beta)

        if current:
            self._data.update({
                HOMEASSISTANT_CURRENT: current.get('homeassistant_tag'),
                HASSIO_CURRENT: current.get('hassio_tag'),
            })
            self.save()
            return True

        return False

    @property
    def upstream_beta(self):
        """Return True if we run in beta upstream."""
        return self._data.get(UPSTREAM_BETA, False)

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
    def current_homeassistant(self):
        """Actual version of homeassistant."""
        return self._data.get(HOMEASSISTANT_CURRENT)

    @property
    def current_hassio(self):
        """Actual version of hassio."""
        return self._data.get(HASSIO_CURRENT)

    @property
    def path_config_docker(self):
        """Return config path extern for docker."""
        return HOMEASSISTANT_CONFIG.format(os.environ['SUPERVISOR_SHARE'])

    @property
    def path_config(self):
        """Return config path inside supervisor."""
        return HOMEASSISTANT_CONFIG.format(HASSIO_SHARE)

    @property
    def path_ssl_docker(self):
        """Return SSL path extern for docker."""
        return HASSIO_SSL.format(os.environ['SUPERVISOR_SHARE'])

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
    def path_addons_data(self):
        """Return root addon data folder."""
        return ADDONS_DATA.format(HASSIO_SHARE)

    @property
    def path_addons_data_docker(self):
        """Return root addon data folder extern for docker."""
        return ADDONS_DATA.format(os.environ['SUPERVISOR_SHARE'])
