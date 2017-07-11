"""HomeAssistant control object."""
import logging
import os

from .const import FILE_HASSIO_HOMEASSISTANT, ATTR_DEVICES, ATTR_IMAGE
from .dock.homeassistant import DockerHomeAssistant
from .tools import JsonConfig
from .validate import SCHEMA_HASS_CONFIG


class HomeAssistant(JsonConfig):
    """Hass core object for handle it."""

    def __init__(self, config, loop, dock):
        """Initialize hass object."""
        super().__init__(FILE_HASSIO_HOMEASSISTANT, SCHEMA_HASS_CONFIG)
        self.config = config
        self.loop = loop

    async def prepare(self):
        """Prepare HomeAssistant object."""

    @property
    def version(self):
        """Return version of running homeassistant."""
        return self.docker.version

    @property
    def last_version(self):
        """Return last available version of homeassistant."""
        return self.config.last_homeassistant

    @property
    def image(self):
        """Return image name of hass containter."""
        if ATTR_IMAGE in self._data:
            return self._data[ATTR_IMAGE]
        return os.environ['HOMEASSISTANT_REPOSITORY']

    @image.setter
    def image(self, value):
        """Set image name of hass containter."""
        if value is None:
            self._data.pop(ATTR_IMAGE, None)
        else:
            self._data[ATTR_IMAGE] = value
        self.save()

    @property
    def devices(self):
        """Return extend device mapping."""
        return self._data[ATTR_DEVICES]

    @devices.setter
    def devices(self, value):
        """Set extend device mapping."""
        self._data[ATTR_DEVICES] = value
        self.save()
