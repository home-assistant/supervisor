"""Handle service data for persistent supervisor reboot."""

from .validate import SCHEMA_SERVICES_CONFIG
from ..const import FILE_HASSIO_SERVICES, SERVICE_MQTT
from ..utils.json import JsonConfig


class ServicesData(JsonConfig):
    """Class to handle services data."""

    def __init__(self):
        """Initialize services data."""
        super().__init__(FILE_HASSIO_SERVICES, SCHEMA_SERVICES_CONFIG)

    @property
    def mqtt(self):
        """Return settings for MQTT service."""
        return self._data[SERVICE_MQTT]
