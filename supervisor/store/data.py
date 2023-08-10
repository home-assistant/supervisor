"""Init file for Supervisor add-on data."""
from dataclasses import dataclass
import logging
from pathlib import Path
from typing import Any

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


@dataclass(slots=True)
class ProcessedRepository:
    """Representation of a repository processed from its git folder."""

    slug: str
    path: Path
    config: dict[str, Any]


def _read_addon_translations(addon_path: Path) -> dict:
    """Read translations from add-ons folder.

    Should be run in the executor.
    """
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
            _LOGGER.warning("Can't read translations from %s - %s", translation, err)
            continue

    return translations


def _read_git_repository(path: Path) -> ProcessedRepository | None:
    """Process a custom repository folder."""
    slug = extract_hash_from_path(path)

    # exists repository json
    try:
        repository_file = find_one_filetype(
            path, "repository", FILE_SUFFIX_CONFIGURATION
        )
    except ConfigurationFileError:
        _LOGGER.warning("No repository information exists at %s", path)
        return None

    try:
        return ProcessedRepository(
            slug,
            path,
            SCHEMA_REPOSITORY_CONFIG(read_json_or_yaml_file(repository_file)),
        )
    except ConfigurationFileError:
        _LOGGER.warning("Can't read repository information from %s", repository_file)
        return None
    except vol.Invalid:
        _LOGGER.warning("Repository parse error %s", repository_file)
        return None


class StoreData(CoreSysAttributes):
    """Hold data for Add-ons inside Supervisor."""

    def __init__(self, coresys: CoreSys):
        """Initialize data holder."""
        self.coresys: CoreSys = coresys
        self.repositories: dict[str, Any] = {}
        self.addons: dict[str, Any] = {}

    async def update(self) -> None:
        """Read data from add-on repository."""
        self.repositories.clear()
        self.addons.clear()

        # read core repository
        await self._read_addons_folder(
            self.sys_config.path_addons_core, REPOSITORY_CORE
        )

        # read local repository
        await self._read_addons_folder(
            self.sys_config.path_addons_local, REPOSITORY_LOCAL
        )

        # add built-in repositories information
        await self._set_builtin_repositories()

        # read custom git repositories
        def _read_git_repositories() -> list[ProcessedRepository]:
            return [
                repo
                for repository_element in self.sys_config.path_addons_git.iterdir()
                if repository_element.is_dir()
                and (repo := _read_git_repository(repository_element))
            ]

        for repo in await self.sys_run_in_executor(_read_git_repositories):
            self.repositories[repo.slug] = repo.config
            await self._read_addons_folder(repo.path, repo.slug)

    async def _find_addons(self, path: Path, repository: dict) -> list[Path] | None:
        """Find add-ons in the path."""

        def _get_addons_list() -> list[Path]:
            # Generate a list without artefact, safe for corruptions
            return [
                addon
                for addon in path.glob("**/config.*")
                if not [
                    part
                    for part in addon.parts
                    if part.startswith(".") or part == "rootfs"
                ]
                and addon.suffix in FILE_SUFFIX_CONFIGURATION
            ]

        try:
            addon_list = await self.sys_run_in_executor(_get_addons_list)
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

    async def _read_addons_folder(self, path: Path, repository: str) -> None:
        """Read data from add-ons folder."""
        if not (addon_list := await self._find_addons(path, repository)):
            return

        def _process_addons_config() -> dict[str, dict[str, Any]]:
            addons_config: dict[str, dict[str, Any]] = {}
            for addon in addon_list:
                try:
                    addon_config = read_json_or_yaml_file(addon)
                except ConfigurationFileError:
                    _LOGGER.warning(
                        "Can't read %s from repository %s", addon, repository
                    )
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
                addon_config[ATTR_TRANSLATIONS] = _read_addon_translations(addon.parent)
                addons_config[addon_slug] = addon_config

            return addons_config

        self.addons.update(await self.sys_run_in_executor(_process_addons_config))

    async def _set_builtin_repositories(self):
        """Add local built-in repository into dataset."""

        def _get_builtins() -> dict[str, dict[str, str]] | None:
            try:
                builtin_file = Path(__file__).parent.joinpath("built-in.json")
                return read_json_file(builtin_file)
            except ConfigurationFileError:
                _LOGGER.warning("Can't read built-in json")
                return None

        builtin_data = await self.sys_run_in_executor(_get_builtins)
        if builtin_data:
            # core repository
            self.repositories[REPOSITORY_CORE] = builtin_data[REPOSITORY_CORE]

            # local repository
            self.repositories[REPOSITORY_LOCAL] = builtin_data[REPOSITORY_LOCAL]
