"""Handle service data for persistent supervisor reboot."""

from .validate import SCHEMA_SERVICES_FILE
from ..const import FILE_HASSIO_SERVICES, ATTR_DISCOVERY, SERVICE_MQTT
from ..utils.json import JsonConfig


class ServicesData(JsonConfig):
    """Class to handle services data."""

    def __init__(self):
        """Initialize services data."""
        super().__init__(FILE_HASSIO_SERVICES, SCHEMA_SERVICES_FILE)

    @property
    def discovery(self):
        """Return discovery data for home-assistant."""
        return self._data[ATTR_DISCOVERY]

    @property
    def mqtt(self):
        """Return settings for mqtt service."""
        return self._data[SERVICE_MQTT]
