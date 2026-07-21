"""Init file for Supervisor app data."""

from dataclasses import dataclass
import errno
import logging
from pathlib import Path
from typing import Any

import voluptuous as vol
from voluptuous.humanize import humanize_error

from ..apps.validate import (
    SCHEMA_APP_CONFIG,
    SCHEMA_APP_CONFIG_QUIET,
    SCHEMA_APP_TRANSLATIONS,
)
from ..const import (
    ATTR_LOCATION,
    ATTR_REPOSITORY,
    ATTR_SLUG,
    ATTR_TRANSLATIONS,
    ATTR_VERSION_TIMESTAMP,
    FILE_SUFFIX_CONFIGURATION,
    REPOSITORY_CORE,
    REPOSITORY_LOCAL,
    UpdateChannel,
)
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import ConfigurationFileError
from ..resolution.const import ContextType, IssueType, SuggestionType
from ..utils.common import find_one_filetype, read_json_or_yaml_file
from ..utils.json import read_json_file
from .utils import extract_hash_from_path
from .validate import SCHEMA_REPOSITORY_CONFIG

_LOGGER: logging.Logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ProcessedRepository:
    """Representation of a repository processed from its git folder."""

    slug: str
    path: Path
    config: dict[str, Any]


def _read_app_translations(app_path: Path) -> dict:
    """Read translations from apps folder.

    Should be run in the executor.
    """
    translations_dir = app_path / "translations"
    translations: dict[str, Any] = {}

    if not translations_dir.exists():
        return translations

    translation_files = [
        translation
        for translation in translations_dir.glob("*")
        if translation.suffix in FILE_SUFFIX_CONFIGURATION
    ]

    for translation in translation_files:
        try:
            translations[translation.stem] = SCHEMA_APP_TRANSLATIONS(
                read_json_or_yaml_file(translation)
            )

        except (ConfigurationFileError, vol.Invalid) as err:
            _LOGGER.warning("Can't read translations from %s - %s", translation, err)
            continue

    return translations


def _read_git_repository(path: Path) -> ProcessedRepository | None:
    """Process a custom repository folder.

    Must be run in executor.
    """
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
    """Hold data for Apps inside Supervisor."""

    def __init__(self, coresys: CoreSys):
        """Initialize data holder."""
        self.coresys: CoreSys = coresys
        self.repositories: dict[str, Any] = {}
        self.apps: dict[str, dict[str, Any]] = {}

    async def update(self) -> None:
        """Read data from app repository."""
        # read core repository
        apps = await self._read_apps_folder(
            self.sys_config.path_apps_core, REPOSITORY_CORE
        )

        # read local repository
        apps.update(
            await self._read_apps_folder(
                self.sys_config.path_apps_local, REPOSITORY_LOCAL
            )
        )

        # add built-in repositories information
        repositories = await self.sys_run_in_executor(self._get_builtin_repositories)

        # read custom git repositories
        def _read_git_repositories() -> list[ProcessedRepository]:
            return [
                repo
                for repository_element in self.sys_config.path_apps_git.iterdir()
                if repository_element.is_dir()
                and (repo := _read_git_repository(repository_element))
            ]

        for repo in await self.sys_run_in_executor(_read_git_repositories):
            repositories[repo.slug] = repo.config
            apps.update(await self._read_apps_folder(repo.path, repo.slug))

        self.repositories = repositories
        self.apps = apps

    async def _find_app_configs(self, path: Path, repository: str) -> list[Path] | None:
        """Find apps in the path."""

        def _get_apps_list() -> list[Path]:
            # Generate a list without artefact, safe for corruptions
            return [
                app
                for app in path.glob("**/config.*")
                if not [
                    part
                    for part in app.parts
                    if part.startswith(".") or part == "rootfs"
                ]
                and app.suffix in FILE_SUFFIX_CONFIGURATION
            ]

        try:
            app_list = await self.sys_run_in_executor(_get_apps_list)
        except OSError as err:
            suggestion = None
            self.sys_resolution.check_oserror(err)
            if err.errno != errno.EBADMSG and repository != REPOSITORY_LOCAL:
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
        return app_list

    async def _read_apps_folder(
        self, path: Path, repository: str
    ) -> dict[str, dict[str, Any]]:
        """Read data from apps folder."""
        if not (app_config_list := await self._find_app_configs(path, repository)):
            return {}

        # App config deprecation/misconfiguration advisories are only actionable
        # for someone who can fix the app, so only those cases log at warning
        # level; everything else stays at debug so regular users don't see
        # warnings for apps they cannot fix. Warn for the local repository
        # (authored by the user), on the dev channel (a developer testing store
        # apps), and for installed apps from custom repositories - the latter
        # are often thin wrappers whose maintainer may have moved on, where the
        # warning is the user's only heads-up before it breaks. Uninstalled apps
        # and apps from the curated built-in stores (which get fixed via PRs)
        # stay quiet.
        repository_obj = self.sys_store.repositories.get(repository)
        repository_is_builtin = bool(repository_obj and repository_obj.is_builtin)
        always_verbose = (
            repository == REPOSITORY_LOCAL
            or self.sys_updater.channel == UpdateChannel.DEV
        )
        installed_slugs = {app.slug for app in self.sys_apps.installed}

        def _process_apps_config() -> dict[str, dict[str, Any]]:
            apps: dict[str, dict[str, Any]] = {}
            for app_config in app_config_list:
                try:
                    app = read_json_or_yaml_file(app_config)
                except ConfigurationFileError:
                    _LOGGER.warning(
                        "Can't read %s from repository %s", app_config, repository
                    )
                    continue

                # Pick the advisory log level based on who can act on it (see
                # above). The slug is available in the raw config before
                # validation.
                verbose = always_verbose or (
                    not repository_is_builtin
                    and f"{repository}_{app.get(ATTR_SLUG)}" in installed_slugs
                )
                schema = SCHEMA_APP_CONFIG if verbose else SCHEMA_APP_CONFIG_QUIET

                # validate
                try:
                    app = schema(app)
                except vol.Invalid as ex:
                    _LOGGER.warning(
                        "Can't read %s: %s", app_config, humanize_error(app, ex)
                    )
                    continue

                # Generate slug
                app_slug = f"{repository}_{app[ATTR_SLUG]}"

                # store
                app[ATTR_REPOSITORY] = repository
                app[ATTR_LOCATION] = str(app_config.parent)
                app[ATTR_TRANSLATIONS] = _read_app_translations(app_config.parent)
                app[ATTR_VERSION_TIMESTAMP] = app_config.stat().st_mtime
                apps[app_slug] = app

            return apps

        return await self.sys_run_in_executor(_process_apps_config)

    def _get_builtin_repositories(self) -> dict[str, dict[str, str]]:
        """Get local built-in repositories into dataset.

        Need to run inside executor.
        """
        try:
            builtin_file = Path(__file__).parent.joinpath("built-in.json")
            return read_json_file(builtin_file)
        except ConfigurationFileError:
            _LOGGER.warning("Can't read built-in json")
            return {}
