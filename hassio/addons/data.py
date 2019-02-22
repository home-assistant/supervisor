"""Init file for Hass.io add-on data."""
import json
import logging
from pathlib import Path

import voluptuous as vol
from voluptuous.humanize import humanize_error

from ..const import (
    ATTR_LOCATON,
    ATTR_REPOSITORY,
    ATTR_SLUG,
    ATTR_SYSTEM,
    ATTR_USER,
    FILE_HASSIO_ADDONS,
    REPOSITORY_CORE,
    REPOSITORY_LOCAL,
)
from ..coresys import CoreSysAttributes
from ..exceptions import JsonFileError
from ..utils.json import JsonConfig, read_json_file
from .utils import extract_hash_from_path
from .validate import SCHEMA_ADDON_CONFIG, SCHEMA_ADDONS_FILE, SCHEMA_REPOSITORY_CONFIG

_LOGGER = logging.getLogger(__name__)


class AddonsData(JsonConfig, CoreSysAttributes):
    """Hold data for Add-ons inside Hass.io."""

    def __init__(self, coresys):
        """Initialize data holder."""
        super().__init__(FILE_HASSIO_ADDONS, SCHEMA_ADDONS_FILE)
        self.coresys = coresys
        self._repositories = {}
        self._cache = {}

    @property
    def user(self):
        """Return local add-on user data."""
        return self._data[ATTR_USER]

    @property
    def system(self):
        """Return local add-on data."""
        return self._data[ATTR_SYSTEM]

    @property
    def cache(self):
        """Return add-on data from cache/repositories."""
        return self._cache

    @property
    def repositories(self):
        """Return add-on data from repositories."""
        return self._repositories

    def reload(self):
        """Read data from add-on repository."""
        self._cache = {}
        self._repositories = {}

        # read core repository
        self._read_addons_folder(self.sys_config.path_addons_core, REPOSITORY_CORE)

        # read local repository
        self._read_addons_folder(self.sys_config.path_addons_local, REPOSITORY_LOCAL)

        # add built-in repositories information
        self._set_builtin_repositories()

        # read custom git repositories
        for repository_element in self.sys_config.path_addons_git.iterdir():
            if repository_element.is_dir():
                self._read_git_repository(repository_element)

    def _read_git_repository(self, path):
        """Process a custom repository folder."""
        slug = extract_hash_from_path(path)

        # exists repository json
        repository_file = Path(path, "repository.json")
        try:
            repository_info = SCHEMA_REPOSITORY_CONFIG(read_json_file(repository_file))
        except JsonFileError:
            _LOGGER.warning(
                "Can't read repository information from %s", repository_file
            )
            return
        except vol.Invalid:
            _LOGGER.warning("Repository parse error %s", repository_file)
            return

        # process data
        self._repositories[slug] = repository_info
        self._read_addons_folder(path, slug)

    def _read_addons_folder(self, path, repository):
        """Read data from add-ons folder."""
        for addon in path.glob("**/config.json"):
            try:
                addon_config = read_json_file(addon)
            except JsonFileError:
                _LOGGER.warning("Can't read %s from repository %s", addon, repository)
                continue

            # validate
            try:
                addon_config = SCHEMA_ADDON_CONFIG(addon_config)
            except vol.Invalid as ex:
                _LOGGER.warning(
                    "Can't read %s: %s", addon, humanize_error(addon_config, ex)
                )
                continue

            # Generate slug
            addon_slug = "{}_{}".format(repository, addon_config[ATTR_SLUG])

            # store
            addon_config[ATTR_REPOSITORY] = repository
            addon_config[ATTR_LOCATON] = str(addon.parent)
            self._cache[addon_slug] = addon_config

    def _set_builtin_repositories(self):
        """Add local built-in repository into dataset."""
        try:
            builtin_file = Path(__file__).parent.joinpath("built-in.json")
            builtin_data = read_json_file(builtin_file)
        except JsonFileError:
            _LOGGER.warning("Can't read built-in json")
            return

        # core repository
        self._repositories[REPOSITORY_CORE] = builtin_data[REPOSITORY_CORE]

        # local repository
        self._repositories[REPOSITORY_LOCAL] = builtin_data[REPOSITORY_LOCAL]
