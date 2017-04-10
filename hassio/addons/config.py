"""Init file for HassIO addons."""
import logging
import glob
import json

import voluptuous as vol
from voluptuous.humanize import humanize_error

from ..const import (
    FILE_HASSIO_ADDONS, ATTR_NAME, ATTR_VERSION, ATTR_SLUG, ATTR_DESCRIPTON,
    ATTR_STARTUP, ATTR_BOOT, ATTR_MAP_SSL, ATTR_MAP_CONFIG, ATTR_MAP_DATA,
    ATTR_OPTIONS, ATTR_PORTS, STARTUP_ONCE, STARTUP_AFTER, STARTUP_BEFORE,
    BOOT_AUTO, BOOT_MANUAL)

_LOGGER = logging.getLogger(__name__)

ADDONS_REPO_PATTERN = "{}/*/config.json"

# pylint: disable=no-value-for-parameter
SCHEMA_ADDON_CONFIG = vol.Schema({
    vol.Required(ATTR_NAME): vol.Coerce(str),
    vol.Required(ATTR_VERSION): vol.Coerce(str),
    vol.Required(ATTR_SLUG): vol.Coerce(str),
    vol.Required(ATTR_DESCRIPTON): vol.Coerce(str),
    vol.Required(ATTR_STARTUP):
        vol.In([STARTUP_BEFORE, STARTUP_AFTER, STARTUP_ONCE]),
    vol.Required(ATTR_BOOT):
        vol.IN([BOOT_AUTO, BOOT_MANUAL]),
    vol.Optional(ATTR_PORTS): dict,
    vol.Required(ATTR_MAP_CONFIG): vol.Boolean(),
    vol.Required(ATTR_MAP_SSL): vol.Boolean(),
    vol.Required(ATTR_MAP_DATA): vol.Boolean(),
    vol.Required(ATTR_OPTIONS): dict,
})


class AddonsConfig(Config):
    """Config for addons inside HassIO."""

    def __init__(self, config):
        """Initialize docker base wrapper."""
        super().__init__(FILE_HASSIO_ADDONS)
        self.config
        self._addons_data = {}

    def read_addons_repo(self):
        """Read data from addons repository."""
        pattern = ADDONS_REPO_PATTERN.format(self.config.path_addons_repo)

        for addon in glob.iglob(pattern):
            try:
                with open(addon, 'r') as cfile:
                    addon_config = json.loads(cfile.read())

                addon_config = SCHEMA_ADDON_CONFIG(addon_config)
                self._addons_data[addon_config[ATTR_SLUG]] = addon_config

            except (OSError, KeyError):
                _LOGGER.warning("Can't read %s", addon)

            except vol.Invalid as ex:
                _LOGGER.warnign("Can't read %s -> %s.", addon,
                                humanize_error(addon_config, ex))
