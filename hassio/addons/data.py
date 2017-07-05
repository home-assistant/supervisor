"""Init file for HassIO addons."""
import copy
import logging
import json
from pathlib import Path
import re

import voluptuous as vol
from voluptuous.humanize import humanize_error

from .util import extract_hash_from_path
from .validate import (
    SCHEMA_ADDON, SCHEMA_REPOSITORY_CONFIG, MAP_VOLUME)
from ..const import (
    FILE_HASSIO_ADDONS, ATTR_VERSION, ATTR_SLUG, ATTR_REPOSITORY, ATTR_LOCATON,
    REPOSITORY_CORE, REPOSITORY_LOCAL, ATTR_USER, ATTR_SYSTEM)
from ..tools import read_json_file, write_json_file

_LOGGER = logging.getLogger(__name__)

RE_VOLUME = re.compile(MAP_VOLUME)


class Data(object):
    """Hold data for addons inside HassIO."""

    def __init__(self, config):
        """Initialize data holder."""
        self._file = FILE_HASSIO_ADDONS
        self._data = {}
        self.config = config
        self._cache = {}
        self._repositories = {}

        # init or load data
        if self._file.is_file():
            try:
                self._data = read_json_file(self._file)
            except (OSError, json.JSONDecodeError):
                _LOGGER.warning("Can't read %s", self._file)
                self._data = {}

        # init data
        if not self._data:
            self._data[ATTR_USER] = {}
            self._data[ATTR_SYSTEM] = {}

    def save(self):
        """Store data to config file."""
        if not write_json_file(self._file, self._data):
            _LOGGER.error("Can't store config in %s", self._file)
            return False
        return True

    @property
    def user(self):
        """Return local addon user data."""
        return self._data[ATTR_USER]

    @property
    def system(self):
        """Return local addon data."""
        return self._data[ATTR_SYSTEM]

    @property
    def cache(self):
        """Return addon data from cache/repositories."""
        return self._cache

    @property
    def repositories(self):
        """Return addon data from repositories."""
        return self._repositories

    def reload(self):
        """Read data from addons repository."""
        self._cache = {}
        self._repositories = {}

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

        # update local data
        self._merge_config()

    def _read_git_repository(self, path):
        """Process a custom repository folder."""
        slug = extract_hash_from_path(path)

        # exists repository json
        repository_file = Path(path, "repository.json")
        try:
            repository_info = SCHEMA_REPOSITORY_CONFIG(
                read_json_file(repository_file)
            )

        except (OSError, json.JSONDecodeError):
            _LOGGER.warning("Can't read repository information from %s",
                            repository_file)
            return

        except vol.Invalid:
            _LOGGER.warning("Repository parse error %s", repository_file)
            return

        # process data
        self._repositories[slug] = repository_info
        self._read_addons_folder(path, slug)

    def _read_addons_folder(self, path, repository):
        """Read data from addons folder."""
        for addon in path.glob("**/config.json"):
            try:
                addon_config = read_json_file(addon)

                # validate
                addon_config = SCHEMA_ADDON(addon_config)

                # Generate slug
                addon_slug = "{}_{}".format(
                    repository, addon_config[ATTR_SLUG])

                # store
                addon_config[ATTR_REPOSITORY] = repository
                addon_config[ATTR_LOCATON] = str(addon.parent)
                self._cache[addon_slug] = addon_config

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

        # core repository
        self._repositories[REPOSITORY_CORE] = \
            builtin_data[REPOSITORY_CORE]

        # local repository
        self._repositories[REPOSITORY_LOCAL] = \
            builtin_data[REPOSITORY_LOCAL]

    def _merge_config(self):
        """Update local config if they have update.

        It need to be the same version as the local version is for merge.
        """
        have_change = False

        for addon in set(self.system):
            # detached
            if addon not in self._cache:
                continue

            cache = self._cache[addon]
            data = self.system[addon]
            if data[ATTR_VERSION] == cache[ATTR_VERSION]:
                if data != cache:
                    self.system[addon] = copy.deepcopy(cache)
                    have_change = True

        if have_change:
            self.save()
