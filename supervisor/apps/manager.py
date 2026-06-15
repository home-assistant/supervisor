"""Supervisor app manager."""

import asyncio
from collections.abc import Awaitable
from contextlib import suppress
import logging
from typing import Self, Union

from attr import evolve
from securetar import SecureTarFile

from ..const import FILE_HASSIO_ADDONS, FILE_HASSIO_APPS, AppBoot, AppStartup, AppState
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import (
    AppAlreadyInstalledError,
    AppNotFoundError,
    AppNotInstalledError,
    AppNotInStoreError,
    AppNoUpdateAvailableError,
    AppRebuildImageBasedError,
    AppRebuildVersionChangedError,
    AppsError,
    AppsJobError,
    CoreDNSError,
    DockerError,
    HassioError,
)
from ..jobs import ChildJobSyncFilter
from ..jobs.const import JobConcurrency
from ..jobs.decorator import Job, JobCondition
from ..resolution.const import ContextType, IssueType, SuggestionType, UnhealthyReason
from ..store.app import AppStore
from ..utils.sentry import async_capture_exception
from .app import App
from .const import APP_UPDATE_CONDITIONS
from .data import AppsData

_LOGGER: logging.Logger = logging.getLogger(__name__)

AnyApp = Union[App, AppStore]


def _migrate_addons_json() -> None:
    """Rename legacy addons.json to apps.json if needed."""
    if FILE_HASSIO_ADDONS.is_file() and not FILE_HASSIO_APPS.exists():
        _LOGGER.info(
            "Migrating %s to %s", FILE_HASSIO_ADDONS.name, FILE_HASSIO_APPS.name
        )
        FILE_HASSIO_ADDONS.rename(FILE_HASSIO_APPS)


class AppManager(CoreSysAttributes):
    """Manage apps inside Supervisor."""

    def __init__(self, coresys: CoreSys):
        """Initialize Docker base wrapper."""
        self.coresys: CoreSys = coresys
        self.data: AppsData = AppsData(coresys)
        self.local: dict[str, App] = {}
        self.store: dict[str, AppStore] = {}

    @property
    def all(self) -> list[AnyApp]:
        """Return a list of all apps."""
        apps: dict[str, AnyApp] = {**self.store, **self.local}
        return list(apps.values())

    @property
    def installed(self) -> list[App]:
        """Return a list of all installed apps."""
        return list(self.local.values())

    def get(self, app_slug: str, local_only: bool = False) -> AnyApp | None:
        """Return an app from slug.

        Prio:
          1 - Local
          2 - Store
        """
        if app_slug in self.local:
            return self.local[app_slug]
        if not local_only:
            return self.store.get(app_slug)
        return None

    def get_local_only(self, app_slug: str) -> App | None:
        """Return an installed app from slug."""
        return self.local.get(app_slug)

    def from_token(self, token: str) -> App | None:
        """Return an app from Supervisor token."""
        for app in self.installed:
            if token == app.supervisor_token:
                return app
        return None

    async def load_config(self) -> Self:
        """Load config in executor."""
        await self.sys_run_in_executor(_migrate_addons_json)
        await self.data.read_data()
        return self

    async def load(self) -> None:
        """Start up app management."""
        # Refresh cache for all store apps
        tasks: list[Awaitable[None]] = [
            store.refresh_path_cache() for store in self.store.values()
        ]

        # Load all installed apps
        for slug in self.data.system:
            app = self.local[slug] = App(self.coresys, slug)
            tasks.append(app.load())

        # Run initial tasks
        _LOGGER.info("Found %d installed apps", len(self.data.system))
        if tasks:
            await asyncio.gather(*tasks)

        # Sync DNS
        await self.sync_dns()

    async def boot(self, stage: AppStartup) -> None:
        """Boot apps with mode auto."""
        tasks: list[App] = []
        for app in self.installed:
            if app.boot != AppBoot.AUTO or app.startup != stage:
                continue
            if (
                app.host_network
                and UnhealthyReason.DOCKER_GATEWAY_UNPROTECTED
                in self.sys_resolution.unhealthy
            ):
                _LOGGER.warning(
                    "Skipping boot of app %s because gateway firewall"
                    " rules are not active",
                    app.slug,
                )
                continue
            tasks.append(app)

        # Evaluate apps which need to be started
        _LOGGER.info("Phase '%s' starting %d apps", stage, len(tasks))
        if not tasks:
            return

        # Start Apps sequential
        # avoid issue on slow IO
        # Config.wait_boot is deprecated. Until apps update with healthchecks,
        # add a sleep task for it to keep the same minimum amount of wait time
        wait_boot: list[Awaitable[None]] = [asyncio.sleep(self.sys_config.wait_boot)]
        for app in tasks:
            try:
                if start_task := await app.start():
                    wait_boot.append(start_task)
            except HassioError:
                self.sys_resolution.add_issue(
                    evolve(app.boot_failed_issue),
                    suggestions=[
                        SuggestionType.EXECUTE_START,
                        SuggestionType.DISABLE_BOOT,
                    ],
                )
            else:
                continue

            _LOGGER.warning("Can't start app %s", app.slug)

        # Ignore exceptions from waiting for app startup, app errors handled elsewhere
        await asyncio.gather(*wait_boot, return_exceptions=True)

        # After waiting for startup, create an issue for boot apps that are error or unknown state
        # Ignore stopped as single shot apps can be run at boot and this is successful exit
        # Timeout waiting for startup is not a failure, app is probably just slow
        for app in tasks:
            if app.state in {AppState.ERROR, AppState.UNKNOWN}:
                self.sys_resolution.add_issue(
                    evolve(app.boot_failed_issue),
                    suggestions=[
                        SuggestionType.EXECUTE_START,
                        SuggestionType.DISABLE_BOOT,
                    ],
                )

    async def shutdown(self, stage: AppStartup) -> None:
        """Shutdown apps."""
        tasks: list[App] = []
        for app in self.installed:
            if app.state != AppState.STARTED or app.startup != stage:
                continue
            tasks.append(app)

        # Evaluate apps which need to be stopped
        _LOGGER.info("Phase '%s' stopping %d apps", stage, len(tasks))
        if not tasks:
            return

        # Stop Apps sequential
        # avoid issue on slow IO
        for app in tasks:
            try:
                await app.stop()
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.warning("Can't stop app %s: %s", app.slug, err)
                await async_capture_exception(err)

    @Job(
        name="addon_manager_install",
        conditions=APP_UPDATE_CONDITIONS,
        on_condition=AppsJobError,
        concurrency=JobConcurrency.QUEUE,
        child_job_syncs=[
            ChildJobSyncFilter("docker_interface_install", progress_allocation=1.0)
        ],
    )
    async def install(
        self, slug: str, *, validation_complete: asyncio.Event | None = None
    ) -> None:
        """Install an app."""
        self.sys_jobs.current.reference = slug

        if slug in self.local:
            raise AppAlreadyInstalledError(_LOGGER.warning, app=self.local[slug])
        store = self.store.get(slug)

        if not store:
            raise AppNotFoundError(_LOGGER.error, slug=slug)

        store.validate_availability()

        # If being run in the background, notify caller that validation has completed
        if validation_complete:
            validation_complete.set()

        await App(self.coresys, slug).install()

        _LOGGER.info("App '%s' successfully installed", slug)

    @Job(name="addon_manager_uninstall")
    async def uninstall(self, slug: str, *, remove_config: bool = False) -> None:
        """Remove an app."""
        if slug not in self.local:
            _LOGGER.warning("App %s is not installed", slug)
            return

        shared_image = any(
            self.local[slug].image == app.image
            and self.local[slug].version == app.version
            for app in self.installed
            if app.slug != slug
        )
        await self.local[slug].uninstall(
            remove_config=remove_config, remove_image=not shared_image
        )

        _LOGGER.info("App '%s' successfully removed", slug)

    @Job(
        name="addon_manager_update",
        conditions=APP_UPDATE_CONDITIONS,
        on_condition=AppsJobError,
        # We assume for now the docker image pull is 100% of this task for progress
        # allocation. But from a user perspective that isn't true. Other steps
        # that take time which is not accounted for in progress include:
        # partial backup, image cleanup, apparmor update, and app restart
        child_job_syncs=[
            ChildJobSyncFilter("docker_interface_install", progress_allocation=1.0)
        ],
    )
    async def update(
        self,
        slug: str,
        backup: bool | None = False,
        *,
        validation_complete: asyncio.Event | None = None,
    ) -> asyncio.Task | None:
        """Update app.

        Returns a Task that completes when app has state 'started' (see app.start)
        if app is started after update. Else nothing is returned.
        """
        self.sys_jobs.current.reference = slug

        if slug not in self.local:
            raise AppNotInstalledError(_LOGGER.error, slug=slug)
        app = self.local[slug]

        if app.is_detached:
            raise AppNotInStoreError(_LOGGER.error, app=app)
        store = self.store[slug]

        if app.version == store.version:
            raise AppNoUpdateAvailableError(_LOGGER.warning, app=app)

        # Check if available, Maybe something have changed
        store.validate_availability()

        # If being run in the background, notify caller that validation has completed
        if validation_complete:
            validation_complete.set()

        if backup:
            await self.sys_backups.do_backup_partial(
                name=f"addon_{app.slug}_{app.version}",
                homeassistant=False,
                apps=[app.slug],
            )

        task = await app.update()

        _LOGGER.info("App '%s' successfully updated", slug)
        return task

    @Job(
        name="addon_manager_rebuild",
        conditions=[
            JobCondition.FREE_SPACE,
            JobCondition.INTERNET_HOST,
            JobCondition.HEALTHY,
        ],
        on_condition=AppsJobError,
    )
    async def rebuild(self, slug: str, *, force: bool = False) -> asyncio.Task | None:
        """Perform a rebuild of local build app.

        Returns a Task that completes when app has state 'started' (see app.start)
        if app is started after rebuild. Else nothing is returned.
        """
        self.sys_jobs.current.reference = slug

        if slug not in self.local:
            raise AppNotInstalledError(_LOGGER.error, slug=slug)
        app = self.local[slug]

        if app.is_detached:
            raise AppNotInStoreError(_LOGGER.error, app=app)
        store = self.store[slug]

        # Check if a rebuild is possible now
        if app.version != store.version:
            raise AppRebuildVersionChangedError(_LOGGER.error, app=app)
        if not force and not app.need_build:
            raise AppRebuildImageBasedError(_LOGGER.error, app=app)

        return await app.rebuild()

    @Job(
        name="addon_manager_restore",
        conditions=[
            JobCondition.FREE_SPACE,
            JobCondition.INTERNET_HOST,
            JobCondition.HEALTHY,
        ],
        on_condition=AppsJobError,
    )
    async def restore(self, slug: str, tar_file: SecureTarFile) -> asyncio.Task | None:
        """Restore state of an app.

        Returns a Task that completes when app has state 'started' (see app.start)
        if app is started after restore. Else nothing is returned.
        """
        self.sys_jobs.current.reference = slug

        if slug not in self.local:
            _LOGGER.debug("App %s is not locally available for restore", slug)
            app = App(self.coresys, slug)
            had_ingress: bool | None = False
        else:
            _LOGGER.debug("App %s is locally available for restore", slug)
            app = self.local[slug]
            had_ingress = app.ingress_panel

        wait_for_start = await app.restore(tar_file)

        # Check if new
        if slug not in self.local:
            _LOGGER.info("Detected new app after restore: %s", slug)
            self.local[slug] = app

        # Update ingress
        if had_ingress != app.ingress_panel:
            await self.sys_ingress.reload()
            await self.sys_ingress.update_hass_panel(app)

        return wait_for_start

    @Job(
        name="addon_manager_repair",
        conditions=[JobCondition.FREE_SPACE, JobCondition.INTERNET_HOST],
    )
    async def repair(self) -> None:
        """Repair local apps."""
        needs_repair: list[App] = []

        # Evaluate Apps to repair
        for app in self.installed:
            if await app.instance.exists():
                continue
            needs_repair.append(app)

        _LOGGER.info("Found %d apps to repair", len(needs_repair))
        if not needs_repair:
            return

        for app in needs_repair:
            _LOGGER.info("Repairing for app: %s", app.slug)
            with suppress(DockerError, KeyError):
                # Need pull a image again
                if not app.need_build:
                    await app.instance.install(app.version, app.image)
                    continue

                # Need local lookup
                if app.need_build and not app.is_detached:
                    store = self.store[app.slug]
                    # If this app is available for rebuild
                    if app.version == store.version:
                        await app.instance.install(app.version, app.image)
                        continue

            _LOGGER.error("Can't repair %s", app.slug)
            with suppress(AppsError):
                await self.uninstall(app.slug)

    async def sync_dns(self) -> None:
        """Sync apps DNS names."""
        # Update hosts
        add_host_coros: list[Awaitable[None]] = []
        for app in self.installed:
            try:
                if not await app.instance.is_running():
                    continue
            except DockerError as err:
                _LOGGER.warning("App %s is corrupt: %s", app.slug, err)
                self.sys_resolution.create_issue(
                    IssueType.CORRUPT_DOCKER,
                    ContextType.ADDON,
                    reference=app.slug,
                    suggestions=[SuggestionType.EXECUTE_REPAIR],
                )
                await async_capture_exception(err)
            else:
                add_host_coros.append(
                    self.sys_plugins.dns.add_host(
                        ipv4=app.ip_address, names=[app.hostname], write=False
                    )
                )

        await asyncio.gather(*add_host_coros)

        # Write hosts files
        with suppress(CoreDNSError):
            await self.sys_plugins.dns.write_hosts()
