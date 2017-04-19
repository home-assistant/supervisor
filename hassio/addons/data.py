"""Init file for HassIO addons."""
import logging
import glob

import voluptuous as vol
from voluptuous.humanize import humanize_error

from .validate import validate_options
from ..const import (
    FILE_HASSIO_ADDONS, ATTR_NAME, ATTR_VERSION, ATTR_SLUG, ATTR_DESCRIPTON,
    ATTR_STARTUP, ATTR_BOOT, ATTR_MAP_SSL, ATTR_MAP_CONFIG, ATTR_OPTIONS,
    ATTR_PORTS, STARTUP_ONCE, STARTUP_AFTER, STARTUP_BEFORE, BOOT_AUTO,
    BOOT_MANUAL, DOCKER_REPO, ATTR_INSTALLED, ATTR_SCHEMA, ATTR_IMAGE,
    ATTR_MAP_ROOT)
from ..config import Config
from ..tools import read_json_file, write_json_file

_LOGGER = logging.getLogger(__name__)

ADDONS_REPO_PATTERN = "{}/*/config.json"

V_STR = 'str'
V_INT = 'int'
V_FLOAT = 'float'
V_BOOL = 'bool'

ADDON_ELEMENT = vol.In([V_STR, V_INT, V_FLOAT, V_BOOL]

# pylint: disable=no-value-for-parameter
SCHEMA_ADDON_CONFIG = vol.Schema({
    vol.Required(ATTR_NAME): vol.Coerce(str),
    vol.Required(ATTR_VERSION): vol.Coerce(str),
    vol.Required(ATTR_SLUG): vol.Coerce(str),
    vol.Required(ATTR_DESCRIPTON): vol.Coerce(str),
    vol.Required(ATTR_STARTUP):
        vol.In([STARTUP_BEFORE, STARTUP_AFTER, STARTUP_ONCE]),
    vol.Required(ATTR_BOOT):
        vol.In([BOOT_AUTO, BOOT_MANUAL]),
    vol.Optional(ATTR_PORTS): dict,
    vol.Optional(ATTR_MAP_CONFIG, default=False): vol.Boolean(),
    vol.Optional(ATTR_MAP_SSL, default=False): vol.Boolean(),
    vol.Optional(ATTR_MAP_ROOT, default=False): vol.Boolean(),
    vol.Required(ATTR_OPTIONS): dict,
    vol.Required(ATTR_SCHEMA): {
        vol.Coerce(str): vol.Any(ADDON_ELEMENT, [
            vol.Any(ADDON_ELEMENT, {vol.Coerce(str): ADDON_ELEMENT}
        ])
    },
    vol.Optional(ATTR_IMAGE): vol.Match(r"\w*/\w*"),
})


class AddonsData(Config):
    """Hold data for addons inside HassIO."""

    def __init__(self, config):
        """Initialize data holder."""
        super().__init__(FILE_HASSIO_ADDONS)
        self.config = config
        self._addons_data = {}
        self.arch = None

    def read_addons_repo(self):
        """Read data from addons repository."""
        self._addons_data = {}

        self._read_addons_folder(self.config.path_addons_repo)
        self._read_addons_folder(self.config.path_addons_custom)

    def _read_addons_folder(self, folder):
        """Read data from addons folder."""
        pattern = ADDONS_REPO_PATTERN.format(folder)

        for addon in glob.iglob(pattern):
            try:
                addon_config = read_json_file(addon)

                addon_config = SCHEMA_ADDON_CONFIG(addon_config)
                self._addons_data[addon_config[ATTR_SLUG]] = addon_config

            except (OSError, KeyError):
                _LOGGER.warning("Can't read %s", addon)

            except vol.Invalid as ex:
                _LOGGER.warning("Can't read %s -> %s", addon,
                                humanize_error(addon_config, ex))

    @property
    def list_installed(self):
        """Return a list of installed addons."""
        return set(self._data.keys())

    @property
    def list_all(self):
        """Return a list of available addons."""
        return set(self._addons_data.keys())

    @property
    def list(self):
        """Return a list of available addons."""
        data = []
        for addon, values in self._addons_data.items():
            data.append({
                ATTR_NAME: values[ATTR_NAME],
                ATTR_SLUG: values[ATTR_SLUG],
                ATTR_DESCRIPTON: values[ATTR_DESCRIPTON],
                ATTR_VERSION: values[ATTR_VERSION],
                ATTR_INSTALLED: self._data.get(addon, {}).get(ATTR_VERSION),
            })

        return data

    def list_startup(self, start_type):
        """Get list of installed addon with need start by type."""
        addon_list = set()
        for addon in self._data.keys():
            if self.get_boot(addon) != BOOT_AUTO:
                continue

            try:
                if self._addons_data[addon][ATTR_STARTUP] == start_type:
                    addon_list.add(addon)
            except KeyError:
                _LOGGER.warning("Orphaned addon detect %s", addon)
                continue

        return addon_list

    @property
    def list_removed(self):
        """Return local addons they not support from repo."""
        addon_list = set()
        for addon in self._data.keys():
            if addon not in self._addons_data:
                addon_list.add(addon)

        return addon_list

    def exists_addon(self, addon):
        """Return True if a addon exists."""
        return addon in self._addons_data

    def is_installed(self, addon):
        """Return True if a addon is installed."""
        return addon in self._data

    def version_installed(self, addon):
        """Return installed version."""
        return self._data[addon][ATTR_VERSION]

    def set_install_addon(self, addon, version):
        """Set addon as installed."""
        self._data[addon] = {
            ATTR_VERSION: version,
            ATTR_OPTIONS: {}
        }
        self.save()

    def set_uninstall_addon(self, addon):
        """Set addon as uninstalled."""
        self._data.pop(addon, None)
        self.save()

    def set_options(self, addon, options):
        """Store user addon options."""
        self._data[addon][ATTR_OPTIONS] = options
        self.save()

    def set_version(self, addon, version):
        """Update version of addon."""
        self._data[addon][ATTR_VERSION] = version
        self.save()

    def get_options(self, addon):
        """Return options with local changes."""
        opt = self._addons_data[addon][ATTR_OPTIONS]
        if addon in self._data:
            opt.update(self._data[addon][ATTR_OPTIONS])
        return opt

    def get_boot(self, addon):
        """Return boot config with prio local settings."""
        if ATTR_BOOT in self._data[addon]:
            return self._data[addon][ATTR_BOOT]

        return self._addons_data[addon][ATTR_BOOT]

    def get_name(self, addon):
        """Return name of addon."""
        return self._addons_data[addon][ATTR_NAME]

    def get_description(self, addon):
        """Return description of addon."""
        return self._addons_data[addon][ATTR_DESCRIPTON]

    def get_version(self, addon):
        """Return version of addon."""
        return self._addons_data[addon][ATTR_VERSION]

    def get_slug(self, addon):
        """Return slug of addon."""
        return self._addons_data[addon][ATTR_SLUG]

    def get_ports(self, addon):
        """Return ports of addon."""
        return self._addons_data[addon].get(ATTR_PORTS)

    def get_image(self, addon):
        """Return image name of addon."""
        if ATTR_IMAGE not in self._addons_data[addon]:
            return "{}/{}-addon-{}".format(
                DOCKER_REPO, self.arch, self.get_slug(addon))

        return self._addons_data[addon][ATTR_IMAGE]

    def need_config(self, addon):
        """Return True if config map is needed."""
        return self._addons_data[addon][ATTR_MAP_CONFIG]

    def need_ssl(self, addon):
        """Return True if ssl map is needed."""
        return self._addons_data[addon][ATTR_MAP_SSL]

    def need_root(self, addon):
        """Return True if root map is needed."""
        return self._addons_data[addon][ATTR_MAP_ROOT]

    def path_data(self, addon):
        """Return addon data path inside supervisor."""
        return "{}/{}".format(
            self.config.path_addons_data, self._addons_data[addon][ATTR_SLUG])

    def path_data_docker(self, addon):
        """Return addon data path external for docker."""
        return "{}/{}".format(self.config.path_addons_data_docker,
                              self._addons_data[addon][ATTR_SLUG])

    def path_addon_options(self, addon):
        """Return path to addons options."""
        return "{}/options.json".format(self.path_data(addon))

    def write_addon_options(self, addon):
        """Return True if addon options is written to data."""
        return write_json_file(
            self.path_addon_options(addon), self.get_options(addon))

    def get_schema(self, addon):
        """Create a schema for addon options."""
        raw_schema = self._addons_data[addon][ATTR_SCHEMA]

        # pylint: disable=no-value-for-parameter
        schema = vol.Schema(vol.All(dict(), validate_options(raw_schema)))
        return schema
