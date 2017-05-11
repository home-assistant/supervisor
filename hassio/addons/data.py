"""Init file for HassIO addons."""
import copy
import logging
import json
from pathlib import Path, PurePath

import voluptuous as vol
from voluptuous.humanize import humanize_error

from .util import extract_hash_from_path
from .validate import (
    validate_options, SCHEMA_ADDON_CONFIG, SCHEMA_REPOSITORY_CONFIG)
from ..const import (
    FILE_HASSIO_ADDONS, ATTR_NAME, ATTR_VERSION, ATTR_SLUG, ATTR_DESCRIPTON,
    ATTR_STARTUP, ATTR_BOOT, ATTR_MAP, ATTR_OPTIONS, ATTR_PORTS, BOOT_AUTO,
    DOCKER_REPO, ATTR_SCHEMA, ATTR_IMAGE, MAP_CONFIG, MAP_SSL, MAP_ADDONS,
    MAP_BACKUP, ATTR_REPOSITORY, ATTR_URL, ATTR_ARCH, ATTR_LOCATON)
from ..config import Config
from ..tools import read_json_file, write_json_file

_LOGGER = logging.getLogger(__name__)

SYSTEM = 'system'
USER = 'user'

REPOSITORY_CORE = 'core'
REPOSITORY_LOCAL = 'local'


class AddonsData(Config):
    """Hold data for addons inside HassIO."""

    def __init__(self, config):
        """Initialize data holder."""
        super().__init__(FILE_HASSIO_ADDONS)
        self.config = config
        self._system_data = self._data.get(SYSTEM, {})
        self._user_data = self._data.get(USER, {})
        self._addons_cache = {}
        self._repositories_data = {}
        self.arch = None

    def save(self):
        """Store data to config file."""
        self._data = {
            USER: self._user_data,
            SYSTEM: self._system_data,
        }
        super().save()

    def read_data_from_repositories(self):
        """Read data from addons repository."""
        self._addons_cache = {}
        self._repositories_data = {}

        # read core repository
        self._read_addons_folder(
            self.config.path_addons_core, REPOSITORY_CORE)

        # read local repository
        self._read_addons_folder(
            self.config.path_addons_local, REPOSITORY_LOCAL)

        # add built-in repositories information
        self._set_builtin_repositories()

        # read custom git repositories
        for repository_element in self.config.path_addons_git.iterdir():
            if repository_element.is_dir():
                self._read_git_repository(repository_element)

    def _read_git_repository(self, path):
        """Process a custom repository folder."""
        slug = extract_hash_from_path(path)
        repository_info = {ATTR_SLUG: slug}

        # exists repository json
        repository_file = Path(path, "repository.json")
        try:
            repository_info.update(SCHEMA_REPOSITORY_CONFIG(
                read_json_file(repository_file)
            ))

        except OSError:
            _LOGGER.warning("Can't read repository information from %s",
                            repository_file)
            return

        except vol.Invalid:
            _LOGGER.warning("Repository parse error %s", repository_file)
            return

        # process data
        self._repositories_data[slug] = repository_info
        self._read_addons_folder(path, slug)

    def _read_addons_folder(self, path, repository):
        """Read data from addons folder."""
        for addon in path.glob("**/config.json"):
            try:
                addon_config = read_json_file(addon)

                # validate
                addon_config = SCHEMA_ADDON_CONFIG(addon_config)

                # Generate slug
                addon_slug = "{}_{}".format(
                    repository, addon_config[ATTR_SLUG])

                # store
                addon_config[ATTR_REPOSITORY] = repository
                addon_config[ATTR_LOCATON] = str(addon.parent)
                self._addons_cache[addon_slug] = addon_config

            except OSError:
                _LOGGER.warning("Can't read %s", addon)

            except vol.Invalid as ex:
                _LOGGER.warning("Can't read %s -> %s", addon,
                                humanize_error(addon_config, ex))

    def _set_builtin_repositories(self):
        """Add local built-in repository into dataset."""
        try:
            builtin_file = Path(__file__).parent.joinpath('built-in.json')
            builtin_data = read_json_file(builtin_file)
        except (OSError, json.JSONDecodeError) as err:
            _LOGGER.warning("Can't read built-in.json -> %s", err)
            return

        # if core addons are available
        for data in self._addons_cache.values():
            if data[ATTR_REPOSITORY] == REPOSITORY_CORE:
                self._repositories_data[REPOSITORY_CORE] = \
                    builtin_data[REPOSITORY_CORE]
                break

        # if local addons are available
        for data in self._addons_cache.values():
            if data[ATTR_REPOSITORY] == REPOSITORY_LOCAL:
                self._repositories_data[REPOSITORY_LOCAL] = \
                    builtin_data[REPOSITORY_LOCAL]
                break

    def merge_update_config(self):
        """Update local config if they have update.

        It need to be the same version as the local version is.
        """
        have_change = False

        for addon, data in self._system_data.items():
            # detached
            if addon not in self._addons_cache:
                continue

            cache = self._addons_cache[addon]
            if data[ATTR_VERSION] == cache[ATTR_VERSION]:
                if data != cache:
                    self._system_data[addon] = copy.deepcopy(cache)
                    have_change = True

        if have_change:
            self.save()

    @property
    def list_installed(self):
        """Return a list of installed addons."""
        return set(self._system_data.keys())

    @property
    def data_all(self):
        """Return a dict of all addons."""
        return {
            **self._system_data,
            **self._addons_cache
        }

    @property
    def data_installed(self):
        """Return a dict of installed addons."""
        return self._system_data.copy()

    def list_startup(self, start_type):
        """Get list of installed addon with need start by type."""
        addon_list = set()
        for addon in self._system_data.keys():
            if self.get_boot(addon) != BOOT_AUTO:
                continue

            try:
                if self._system_data[addon][ATTR_STARTUP] == start_type:
                    addon_list.add(addon)
            except KeyError:
                _LOGGER.warning("Orphaned addon detect %s", addon)
                continue

        return addon_list

    @property
    def list_detached(self):
        """Return local addons they not support from repo."""
        addon_list = set()
        for addon in self._system_data.keys():
            if addon not in self._addons_cache:
                addon_list.add(addon)

        return addon_list

    @property
    def list_repositories(self):
        """Return list of addon repositories."""
        return list(self._repositories_data.values())

    def exists_addon(self, addon):
        """Return True if a addon exists."""
        return addon in self._addons_cache or addon in self._system_data

    def is_installed(self, addon):
        """Return True if a addon is installed."""
        return addon in self._system_data

    def version_installed(self, addon):
        """Return installed version."""
        return self._user_data.get(addon, {}).get(ATTR_VERSION)

    def set_addon_install(self, addon, version):
        """Set addon as installed."""
        self._system_data[addon] = copy.deepcopy(self._addons_cache[addon])
        self._user_data[addon] = {
            ATTR_OPTIONS: {},
            ATTR_VERSION: version,
        }
        self.save()

    def set_addon_uninstall(self, addon):
        """Set addon as uninstalled."""
        self._system_data.pop(addon, None)
        self._user_data.pop(addon, None)
        self.save()

    def set_addon_update(self, addon, version):
        """Update version of addon."""
        self._system_data[addon] = copy.deepcopy(self._addons_cache[addon])
        self._user_data[addon][ATTR_VERSION] = version
        self.save()

    def set_options(self, addon, options):
        """Store user addon options."""
        self._user_data[addon][ATTR_OPTIONS] = copy.deepcopy(options)
        self.save()

    def set_boot(self, addon, boot):
        """Store user boot options."""
        self._user_data[addon][ATTR_BOOT] = boot
        self.save()

    def get_options(self, addon):
        """Return options with local changes."""
        return {
            **self._system_data[addon][ATTR_OPTIONS],
            **self._user_data[addon][ATTR_OPTIONS],
        }

    def get_boot(self, addon):
        """Return boot config with prio local settings."""
        if ATTR_BOOT in self._user_data[addon]:
            return self._user_data[addon][ATTR_BOOT]

        return self._system_data[addon][ATTR_BOOT]

    def get_name(self, addon):
        """Return name of addon."""
        return self._system_data[addon][ATTR_NAME]

    def get_description(self, addon):
        """Return description of addon."""
        return self._system_data[addon][ATTR_DESCRIPTON]

    def get_repository(self, addon):
        """Return repository of addon."""
        return self._system_data[addon][ATTR_REPOSITORY]

    def get_last_version(self, addon):
        """Return version of addon."""
        if addon not in self._addons_cache:
            return self.version_installed(addon)
        return self._addons_cache[addon][ATTR_VERSION]

    def get_ports(self, addon):
        """Return ports of addon."""
        return self._system_data[addon].get(ATTR_PORTS)

    def get_url(self, addon):
        """Return url of addon."""
        return self._system_data[addon].get(ATTR_URL)

    def get_arch(self, addon):
        """Return list of supported arch."""
        if addon not in self._addons_cache:
            return self._system_data[addon][ATTR_ARCH]
        return self._addons_cache[addon][ATTR_ARCH]

    def get_image(self, addon):
        """Return image name of addon."""
        addon_data = self._system_data.get(
            addon, self._addons_cache.get(addon)
        )

        # core repository
        if addon_data[ATTR_REPOSITORY] == REPOSITORY_CORE:
            return "{}/{}-addon-{}".format(
                DOCKER_REPO, self.arch, addon_data[ATTR_SLUG])

        # Repository with dockerhub images
        if ATTR_IMAGE in addon_data:
            return addon_data[ATTR_IMAGE].format(arch=self.arch)

        # Local build addon
        if addon_data[ATTR_REPOSITORY] == REPOSITORY_LOCAL:
            return "local/{}-addon-{}".format(self.arch, addon_data[ATTR_SLUG])

        _LOGGER.error("No image for %s", addon)

    def need_build(self, addon):
        """Return True if this addon need a local build."""
        addon_data = self._system_data.get(
            addon, self._addons_cache.get(addon)
        )
        return addon_data[ATTR_REPOSITORY] == REPOSITORY_LOCAL \
            and not addon_data.get(ATTR_IMAGE)

    def map_config(self, addon):
        """Return True if config map is needed."""
        return MAP_CONFIG in self._system_data[addon][ATTR_MAP]

    def map_ssl(self, addon):
        """Return True if ssl map is needed."""
        return MAP_SSL in self._system_data[addon][ATTR_MAP]

    def map_addons(self, addon):
        """Return True if addons map is needed."""
        return MAP_ADDONS in self._system_data[addon][ATTR_MAP]

    def map_backup(self, addon):
        """Return True if backup map is needed."""
        return MAP_BACKUP in self._system_data[addon][ATTR_MAP]

    def path_data(self, addon):
        """Return addon data path inside supervisor."""
        return Path(self.config.path_addons_data, addon)

    def path_extern_data(self, addon):
        """Return addon data path external for docker."""
        return PurePath(self.config.path_extern_addons_data, addon)

    def path_addon_options(self, addon):
        """Return path to addons options."""
        return Path(self.path_data(addon), "options.json")

    def path_addon_location(self, addon):
        """Return path to this addon."""
        return Path(self._addons_cache[addon][ATTR_LOCATON])

    def write_addon_options(self, addon):
        """Return True if addon options is written to data."""
        schema = self.get_schema(addon)
        options = self.get_options(addon)

        try:
            schema(options)
            return write_json_file(self.path_addon_options(addon), options)
        except vol.Invalid as ex:
            _LOGGER.error("Addon %s have wrong options -> %s", addon,
                          humanize_error(options, ex))

        return False

    def get_schema(self, addon):
        """Create a schema for addon options."""
        raw_schema = self._system_data[addon][ATTR_SCHEMA]

        schema = vol.Schema(vol.All(dict, validate_options(raw_schema)))
        return schema
