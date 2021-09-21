"""Handle service data for persistent supervisor reboot."""
from typing import Any

from ..const import FILE_HASSIO_SERVICES
from ..utils.common import FileConfiguration
from .const import SERVICE_MQTT, SERVICE_MYSQL
from .validate import SCHEMA_SERVICES_CONFIG


class ServicesData(FileConfiguration):
    """Class to handle services data."""

    def __init__(self):
        """Initialize services data."""
        super().__init__(FILE_HASSIO_SERVICES, SCHEMA_SERVICES_CONFIG)

    @property
    def mqtt(self) -> dict[str, Any]:
        """Return settings for MQTT service."""
        return self._data[SERVICE_MQTT]

    @property
    def mysql(self) -> dict[str, Any]:
        """Return settings for MySQL service."""
        return self._data[SERVICE_MYSQL]
