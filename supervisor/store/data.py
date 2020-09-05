"""Init file for Supervisor add-on data."""
import logging
from pathlib import Path
from typing import Any, Dict

import voluptuous as vol
from voluptuous.humanize import humanize_error

from ..addons.validate import SCHEMA_ADDON_CONFIG
from ..const import (
    ATTR_LOCATON,
    ATTR_REPOSITORY,
    ATTR_SLUG,
    REPOSITORY_CORE,
    REPOSITORY_LOCAL,
)
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import JsonFileError
from ..utils.json import read_json_file
from .utils import extract_hash_from_path
from .validate import SCHEMA_REPOSITORY_CONFIG

_LOGGER: logging.Logger = logging.getLogger(__name__)


class StoreData(CoreSysAttributes):
    """Hold data for Add-ons inside Supervisor."""

    def __init__(self, coresys: CoreSys):
        """Initialize data holder."""
        self.coresys: CoreSys = coresys
        self.repositories: Dict[str, Any] = {}
        self.addons: Dict[str, Any] = {}

    def update(self):
        """Read data from add-on repository."""
        self.repositories.clear()
        self.addons.clear()

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
        self.repositories[slug] = repository_info
        self._read_addons_folder(path, slug)

    def _read_addons_folder(self, path, repository):
        """Read data from add-ons folder."""
        try:
            addon_list = path.glob("**/config.json")
        except OSError as err:
            self.sys_core.healthy = False
            _LOGGER.critical(
                "Can't process %s because of Filesystem issues: %s", repository, err
            )
            self.sys_capture_exception(err)
            return

        for addon in addon_list:
            # Ingore git artefacts
            if ".git" in addon.parts:
                continue

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
            addon_slug = f"{repository}_{addon_config[ATTR_SLUG]}"

            # store
            addon_config[ATTR_REPOSITORY] = repository
            addon_config[ATTR_LOCATON] = str(addon.parent)
            self.addons[addon_slug] = addon_config

    def _set_builtin_repositories(self):
        """Add local built-in repository into dataset."""
        try:
            builtin_file = Path(__file__).parent.joinpath("built-in.json")
            builtin_data = read_json_file(builtin_file)
        except JsonFileError:
            _LOGGER.warning("Can't read built-in json")
            return

        # core repository
        self.repositories[REPOSITORY_CORE] = builtin_data[REPOSITORY_CORE]

        # local repository
        self.repositories[REPOSITORY_LOCAL] = builtin_data[REPOSITORY_LOCAL]
