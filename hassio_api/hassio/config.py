"""Bootstrap HassIO."""
import json
import logging
import os

from .const import (
    FILE_HASSIO_CONFIG, HOMEASSISTANT_TAG, HOMEASSISTANT_IMAGE,
    HOMEASSISTANT_SSL, HOMEASSISTANT_CONFIG, HASSIO_SHARE_EXT,
    HASSIO_SHARE_INT)

_LOGGER = logging.getLogger(__name__)


class CoreConfig(object):
    """Hold all config data."""

    def __init__(self, config_file=FILE_HASSIO_CONFIG):
        """Initialize config object."""
        self._data = {}
        self._filename = config_file

        # init or load data
        if os.path.isfile(self._filename):
            try:
                with open(self._filename, 'r') as cfile:
                    self._data = json.loads(cfile.read())
            except OSError:
                _LOGGER.warning("Can't read %s", self._filename)

        if not self._data:
            self._data.update({
                HOMEASSISTANT_IMAGE: os.environ['HOMEASSISTANT_REPOSITORY'],
                HOMEASSISTANT_TAG: None,
            })

    def save(self):
        """Store data to config file."""
        try:
            with open(self._filename, 'w') as conf_file:
                conf_file.write(json.dumps(self._data))
        except OSError:
            _LOGGER.exception("Can't store config in %s", self._filename)

    @property
    def homeassistant_image(self):
        """Return docker homeassistant repository."""
        return self._data.get(HOMEASSISTANT_IMAGE)

    @property
    def homeassistant_tag(self):
        """Return docker homeassistant tag."""
        return self._data.get(HOMEASSISTANT_TAG)

    @homeassistant_tag.setter
    def homeassistant_tag(self, value):
        """Set docker homeassistant tag."""
        self._data[HOMEASSISTANT_TAG] = value
        self.save()

    @property
    def path_config_docker(self):
        """Return config path extern for docker."""
        return HOMEASSISTANT_CONFIG.format(HASSIO_SHARE_EXT)

    @property
    def path_config(self):
        """Return config path inside supervisor."""
        return HOMEASSISTANT_CONFIG.format(HASSIO_SHARE_INT)

    @property
    def path_ssl_docker(self):
        """Return SSL path extern for docker."""
        return HOMEASSISTANT_SSL.format(HASSIO_SHARE_EXT)

    @property
    def path_ssl(self):
        """Return SSL path inside supervisor."""
        return HOMEASSISTANT_SSL.format(HASSIO_SHARE_INT)
