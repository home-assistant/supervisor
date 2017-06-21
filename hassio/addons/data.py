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
    SCHEMA_ADDON_CONFIG, SCHEMA_REPOSITORY_CONFIG, MAP_VOLUME)
from ..const import (
    FILE_HASSIO_ADDONS, ATTR_NAME, ATTR_VERSION, ATTR_SLUG, ATTR_DESCRIPTON,
    ATTR_REPOSITORY, ATTR_URL, ATTR_LOCATON, REPOSITORY_CORE, REPOSITORY_LOCAL)
from ..config import Config
from ..tools import read_json_file

_LOGGER = logging.getLogger(__name__)

SYSTEM = 'system'
USER = 'user'

RE_VOLUME = re.compile(MAP_VOLUME)


class Data(Config):
    """Hold data for addons inside HassIO."""

    def __init__(self, config):
        """Initialize data holder."""
        super().__init__(FILE_HASSIO_ADDONS)
        self.config = config
        self._system_data = self._data.get(SYSTEM, {})
        self._user_data = self._data.get(USER, {})
        self._cache_data = {}
        self._repositories_data = {}

    def save(self):
        """Store data to config file."""
        self._data = {
            USER: self._user_data,
            SYSTEM: self._system_data,
        }
        super().save()

    @property
    def user(self):
        """Return local addon user data."""
        return self._user_data

    @property
    def system(self):
        """Return local addon data."""
        return self._system_data

    @property
    def cache(self):
        """Return addon data from cache/repositories."""
        return self._cache_data

    @property
    def repositories(self):
        """Return addon data from repositories."""
        return self._repositories_data

    def reload(self):
        """Read data from addons repository."""
        self._cache_data = {}
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

        # update local data
        self._merge_config()

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
                self._cache_data[addon_slug] = addon_config

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
        self._repositories_data[REPOSITORY_CORE] = \
            builtin_data[REPOSITORY_CORE]

        # local repository
        self._repositories_data[REPOSITORY_LOCAL] = \
            builtin_data[REPOSITORY_LOCAL]

    def _merge_config(self):
        """Update local config if they have update.

        It need to be the same version as the local version is for merge.
        """
        have_change = False

        for addon in set(self._system_data):
            # detached
            if addon not in self._cache_data:
                continue

            cache = self._cache_data[addon]
            data = self._system_data[addon]
            if data[ATTR_VERSION] == cache[ATTR_VERSION]:
                if data != cache:
                    self._system_data[addon] = copy.deepcopy(cache)
                    have_change = True

        if have_change:
            self.save()
