"""Init file for Supervisor add-on data."""
import logging
from pathlib import Path
from typing import Any, Awaitable, Optional

import voluptuous as vol
from voluptuous.humanize import humanize_error

from ..addons.validate import SCHEMA_ADDON_CONFIG, SCHEMA_ADDON_TRANSLATIONS
from ..const import (
    ATTR_LOCATON,
    ATTR_REPOSITORY,
    ATTR_SLUG,
    ATTR_TRANSLATIONS,
    FILE_SUFFIX_CONFIGURATION,
    REPOSITORY_CORE,
    REPOSITORY_LOCAL,
)
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import ConfigurationFileError
from ..resolution.const import ContextType, IssueType, SuggestionType
from ..utils.common import find_one_filetype, read_json_or_yaml_file
from ..utils.json import read_json_file
from .const import StoreType
from .utils import extract_hash_from_path
from .validate import SCHEMA_REPOSITORY_CONFIG

_LOGGER: logging.Logger = logging.getLogger(__name__)


class StoreData(CoreSysAttributes):
    """Hold data for Add-ons inside Supervisor."""

    def __init__(self, coresys: CoreSys):
        """Initialize data holder."""
        self.coresys: CoreSys = coresys
        self.repositories: dict[str, Any] = {}
        self.addons: dict[str, Any] = {}

    async def update(self) -> Awaitable[None]:
        """Read data from add-on repository."""
        return await self.sys_run_in_executor(self._update)

    def _update(self) -> None:
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

    def _read_git_repository(self, path: Path) -> None:
        """Process a custom repository folder."""
        slug = extract_hash_from_path(path)

        # exists repository json
        try:
            repository_file = find_one_filetype(
                path, "repository", FILE_SUFFIX_CONFIGURATION
            )
        except ConfigurationFileError:
            _LOGGER.warning("No repository information exists at %s", path)
            return

        try:
            repository_info = SCHEMA_REPOSITORY_CONFIG(
                read_json_or_yaml_file(repository_file)
            )
        except ConfigurationFileError:
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

    def _find_addons(self, path: Path, repository: dict) -> Optional[list[Path]]:
        """Find add-ons in the path."""
        try:
            # Generate a list without artefact, safe for corruptions
            addon_list = [
                addon
                for addon in path.glob("**/config.*")
                if not [
                    part
                    for part in addon.parts
                    if part.startswith(".") or part == "rootfs"
                ]
                and addon.suffix in FILE_SUFFIX_CONFIGURATION
            ]
        except OSError as err:
            suggestion = None
            if path.stem != StoreType.LOCAL:
                suggestion = [SuggestionType.EXECUTE_RESET]
            self.sys_resolution.create_issue(
                IssueType.CORRUPT_REPOSITORY,
                ContextType.STORE,
                reference=path.stem,
                suggestions=suggestion,
            )
            _LOGGER.critical(
                "Can't process %s because of Filesystem issues: %s", repository, err
            )
            return None
        return addon_list

    def _read_addons_folder(self, path: Path, repository: dict) -> None:
        """Read data from add-ons folder."""
        if not (addon_list := self._find_addons(path, repository)):
            return

        for addon in addon_list:
            try:
                addon_config = read_json_or_yaml_file(addon)
            except ConfigurationFileError:
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
            addon_config[ATTR_TRANSLATIONS] = self._read_addon_translations(
                addon.parent
            )
            self.addons[addon_slug] = addon_config

    def _set_builtin_repositories(self):
        """Add local built-in repository into dataset."""
        try:
            builtin_file = Path(__file__).parent.joinpath("built-in.json")
            builtin_data = read_json_file(builtin_file)
        except ConfigurationFileError:
            _LOGGER.warning("Can't read built-in json")
            return

        # core repository
        self.repositories[REPOSITORY_CORE] = builtin_data[REPOSITORY_CORE]

        # local repository
        self.repositories[REPOSITORY_LOCAL] = builtin_data[REPOSITORY_LOCAL]

    def _read_addon_translations(self, addon_path: Path) -> dict:
        """Read translations from add-ons folder."""
        translations_dir = addon_path / "translations"
        translations = {}

        if not translations_dir.exists():
            return translations

        translation_files = [
            translation
            for translation in translations_dir.glob("*")
            if translation.suffix in FILE_SUFFIX_CONFIGURATION
        ]

        for translation in translation_files:
            try:
                translations[translation.stem] = SCHEMA_ADDON_TRANSLATIONS(
                    read_json_or_yaml_file(translation)
                )

            except (ConfigurationFileError, vol.Invalid) as err:
                _LOGGER.warning(
                    "Can't read translations from %s - %s", translation, err
                )
                continue

        return translations
