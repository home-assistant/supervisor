"""Init file for HassIO addons."""
import copy
import logging
from pathlib import Path, PurePath
import re

import voluptuous as vol
from voluptuous.humanize import humanize_error

from .validate import (
    validate_options, SCHEMA_ADDON_CONFIG, MAP_VOLUME)
from ..const import (
    ATTR_NAME, ATTR_VERSION, ATTR_SLUG, ATTR_DESCRIPTON, ATTR_BOOT, ATTR_MAP,
    ATTR_OPTIONS, ATTR_PORTS, BOOT_AUTO, ATTR_SCHEMA, ATTR_IMAGE,
    ATTR_REPOSITORY, ATTR_URL, ATTR_ARCH, ATTR_LOCATON, ATTR_DEVICES,
    ATTR_ENVIRONMENT, ATTR_HOST_NETWORK, ATTR_TMPFS, ATTR_PRIVILEGED)

_LOGGER = logging.getLogger(__name__)

RE_VOLUME = re.compile(MAP_VOLUME)


class Addon(object):
    """Hold data for addon inside HassIO."""

    def __init__(self, config, data, addon_slug):
        """Initialize data holder."""
        self.config = config
        self.data = data
        self._id = addon_slug

    @property
    def _mesh(self):
        """Return addon data from system or cache."""
        return self.data.system.get(self._id, self.data.cache.get(self._id))

    @property
    def is_installed(self):
        """Return True if a addon is installed."""
        return self._id in self.data.system

    @property
    def version_installed(self):
        """Return installed version."""
        return self.data.user.get(self._id, {}).get(ATTR_VERSION)

    def set_install(self, version):
        """Set addon as installed."""
        self.data.system[self._id] = copy.deepcopy(self.data.cache[self._id])
        self.data.user[self._id] = {
            ATTR_OPTIONS: {},
            ATTR_VERSION: version,
        }
        self.data.save()

    def set_uninstall(self):
        """Set addon as uninstalled."""
        self.data.system.pop(self._id, None)
        self.data.user.pop(self._id, None)
        self.data.save()

    def set_update(self, version):
        """Update version of addon."""
        self.data.system[self._id] = copy.deepcopy(self.data.cache[self._id])
        self.data.user[self._id][ATTR_VERSION] = version
        self.data.save()

    @options.setter
    def options(self, value):
        """Store user addon options."""
        self.data.user[self._id][ATTR_OPTIONS] = copy.deepcopy(value)
        self.data.save()

    @property
    def options(self):
        """Return options with local changes."""
        if self.is_installed:
            return {
                **self.data.system[self._id][ATTR_OPTIONS],
                **self.data.user[self._id][ATTR_OPTIONS],
            }

        return self.data.cache[self._id]

    @boot.setter
    def boot(self, value):
        """Store user boot options."""
        self.data.user[self._id][ATTR_BOOT] = value
        self.data.save()

    @property
    def boot(self):
        """Return boot config with prio local settings."""
        if ATTR_BOOT in self.data.user[self._id]:
            return self.data.user[self._id][ATTR_BOOT]
        return self._mesh[ATTR_BOOT]

    @property
    def name(self):
        """Return name of addon."""
        return self._mesh[ATTR_NAME]

    @property
    def description(self):
        """Return description of addon."""
        return self._mesh[ATTR_DESCRIPTON]

    @property
    def repository(self):
        """Return repository of addon."""
        return self._mesh[ATTR_REPOSITORY]

    @property
    def last_version(self):
        """Return version of addon."""
        if self._id in self.data.cache:
            return self.data.cache[self._id][ATTR_VERSION]
        return self.version_installed

    @property
    def ports(self):
        """Return ports of addon."""
        return self._mesh.get(ATTR_PORTS)

    @property
    def network_mode(self):
        """Return network mode of addon."""
        if self._mesh[ATTR_HOST_NETWORK]:
            return 'host'
        return 'bridge'

    @property
    def devices(self):
        """Return devices of addon."""
        return self._mesh.get(ATTR_DEVICES)

    @property
    def tmpfs(self):
        """Return tmpfs of addon."""
        return self._mesh.get(ATTR_TMPFS)

    @property
    def environment(self):
        """Return environment of addon."""
        return self._mesh.get(ATTR_ENVIRONMENT)

    @property
    def privileged(self):
        """Return list of privilege."""
        return self._mesh.get(ATTR_PRIVILEGED)

    @property
    def url(self):
        """Return url of addon."""
        return self._mesh.get(ATTR_URL)

    @property
    def supported_arch(self):
        """Return list of supported arch."""
        return self._mesh[ATTR_ARCH]

    @property
    def image(self):
        """Return image name of addon."""
        addon_data = self._mesh

        # Repository with dockerhub images
        if ATTR_IMAGE in addon_data:
            return addon_data[ATTR_IMAGE].format(arch=self.arch)

        # local build
        return "{}/{}-addon-{}".format(
            addon_data[ATTR_REPOSITORY], self.arch, addon_data[ATTR_SLUG])

    @property
    def need_build(self):
        """Return True if this  addon need a local build."""
        return ATTR_IMAGE not in self._mesh

    @property
    def map_volumes(self):
        """Return a dict of {volume: policy} from addon."""
        volumes = {}
        for volume in self._mesh[ATTR_MAP]:
            result = RE_VOLUME.match(volume)
            volumes[result.group(1)] = result.group(2) or 'ro'

        return volumes

    @property
    def path_data(self):
        """Return addon data path inside supervisor."""
        return Path(self.config.path_addons_data, self._id)

    @property
    def path_extern_data(self):
        """Return addon data path external for docker."""
        return PurePath(self.config.path_extern_addons_data, self._id)

    @property
    def path_addon_options(self):
        """Return path to addons options."""
        return Path(self.path_data, "options.json")

    @property
    def path_addon_location(self):
        """Return path to this addon."""
        return Path(self._mesh[ATTR_LOCATON])

    def write_addon_options(self):
        """Return True if addon options is written to data."""
        schema = self.schema
        options = self.options

        try:
            schema(options)
            return write_json_file(self.path_addon_options, options)
        except vol.Invalid as ex:
            _LOGGER.error("Addon %s have wrong options -> %s", self._id,
                          humanize_error(options, ex))

        return False

    @property
    def schema(self):
        """Create a schema for addon options."""
        raw_schema = self._mesh[ATTR_SCHEMA]

        if isinstance(raw_schema, bool):
            return vol.Schema(dict)
        return vol.Schema(vol.All(dict, validate_options(raw_schema)))
