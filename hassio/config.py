"""Bootstrap HassIO."""
import json
import logging
import os

from .const import FILE_HASSIO_CONFIG, HASSIO_SHARE
from .tools import fetch_current_versions

_LOGGER = logging.getLogger(__name__)

HOMEASSISTANT_CONFIG = "{}/homeassistant_config"
HOMEASSISTANT_IMAGE = 'homeassistant_image'
HOMEASSISTANT_CURRENT = 'homeassistant_current'

HASSIO_SSL = "{}/ssl"
HASSIO_CURRENT = 'hassio_current'

ADDONS_REPO = "{}/addons"
ADDONS_DATA = "{}/addons_data"

UPSTREAM_BETA = 'upstream_beta'


class CoreConfig(object):
    """Hold all config data."""

    def __init__(self, websession, config_file=FILE_HASSIO_CONFIG):
        """Initialize config object."""
        self.websession = websession
        self._filename = config_file
        self._data = {}

        # init or load data
        if os.path.isfile(self._filename):
            try:
                with open(self._filename, 'r') as cfile:
                    self._data = json.loads(cfile.read())
            except OSError:
                _LOGGER.warning("Can't read %s", self._filename)

        # init data
        if not self._data:
            self._data.update({
                HOMEASSISTANT_IMAGE: os.environ['HOMEASSISTANT_REPOSITORY'],
                UPSTREAM_BETA: False,
            })
            self.save()

    def save(self):
        """Store data to config file."""
        try:
            with open(self._filename, 'w') as conf_file:
                conf_file.write(json.dumps(self._data))
        except OSError:
            _LOGGER.exception("Can't store config in %s", self._filename)
            return False

        return True

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
    def path_addons_data(self):
        """Return root addon data folder."""
        return ADDONS_DATA.format(HASSIO_SHARE)

    @property
    def path_addons_data_docker(self):
        """Return root addon data folder extern for docker."""
        return ADDONS_DATA.format(os.environ['SUPERVISOR_SHARE'])
