"""Supervisor add-on manager."""

import asyncio
from collections.abc import Awaitable
from contextlib import suppress
import logging
import tarfile
from typing import Self, Union

from attr import evolve

from ..const import AddonBoot, AddonStartup, AddonState
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import (
    AddonsError,
    AddonsJobError,
    AddonsNotSupportedError,
    CoreDNSError,
    DockerError,
    HassioError,
    HomeAssistantAPIError,
)
from ..jobs.decorator import Job, JobCondition
from ..resolution.const import ContextType, IssueType, SuggestionType
from ..store.addon import AddonStore
from ..utils.sentry import async_capture_exception
from .addon import Addon
from .const import ADDON_UPDATE_CONDITIONS
from .data import AddonsData

_LOGGER: logging.Logger = logging.getLogger(__name__)

AnyAddon = Union[Addon, AddonStore]


class AddonManager(CoreSysAttributes):
    """Manage add-ons inside Supervisor."""

    def __init__(self, coresys: CoreSys):
        """Initialize Docker base wrapper."""
        self.coresys: CoreSys = coresys
        self.data: AddonsData = AddonsData(coresys)
        self.local: dict[str, Addon] = {}
        self.store: dict[str, AddonStore] = {}

    @property
    def all(self) -> list[AnyAddon]:
        """Return a list of all add-ons."""
        addons: dict[str, AnyAddon] = {**self.store, **self.local}
        return list(addons.values())

    @property
    def installed(self) -> list[Addon]:
        """Return a list of all installed add-ons."""
        return list(self.local.values())

    def get(self, addon_slug: str, local_only: bool = False) -> AnyAddon | None:
        """Return an add-on from slug.

        Prio:
          1 - Local
          2 - Store
        """
        if addon_slug in self.local:
            return self.local[addon_slug]
        if not local_only:
            return self.store.get(addon_slug)
        return None

    def from_token(self, token: str) -> Addon | None:
        """Return an add-on from Supervisor token."""
        for addon in self.installed:
            if token == addon.supervisor_token:
                return addon
        return None

    async def load_config(self) -> Self:
        """Load config in executor."""
        await self.data.read_data()
        return self

    async def load(self) -> None:
        """Start up add-on management."""
        # Refresh cache for all store addons
        tasks: list[Awaitable[None]] = [
            store.refresh_path_cache() for store in self.store.values()
        ]

        # Load all installed addons
        for slug in self.data.system:
            addon = self.local[slug] = Addon(self.coresys, slug)
            tasks.append(addon.load())

        # Run initial tasks
        _LOGGER.info("Found %d installed add-ons", len(self.data.system))
        if tasks:
            await asyncio.gather(*tasks)

        # Sync DNS
        await self.sync_dns()

    async def boot(self, stage: AddonStartup) -> None:
        """Boot add-ons with mode auto."""
        tasks: list[Addon] = []
        for addon in self.installed:
            if addon.boot != AddonBoot.AUTO or addon.startup != stage:
                continue
            tasks.append(addon)

        # Evaluate add-ons which need to be started
        _LOGGER.info("Phase '%s' starting %d add-ons", stage, len(tasks))
        if not tasks:
            return

        # Start Add-ons sequential
        # avoid issue on slow IO
        # Config.wait_boot is deprecated. Until addons update with healthchecks,
        # add a sleep task for it to keep the same minimum amount of wait time
        wait_boot: list[Awaitable[None]] = [asyncio.sleep(self.sys_config.wait_boot)]
        for addon in tasks:
            try:
                if start_task := await addon.start():
                    wait_boot.append(start_task)
            except HassioError:
                self.sys_resolution.add_issue(
                    evolve(addon.boot_failed_issue),
                    suggestions=[
                        SuggestionType.EXECUTE_START,
                        SuggestionType.DISABLE_BOOT,
                    ],
                )
            else:
                continue

            _LOGGER.warning("Can't start Add-on %s", addon.slug)

        # Ignore exceptions from waiting for addon startup, addon errors handled elsewhere
        await asyncio.gather(*wait_boot, return_exceptions=True)

        # After waiting for startup, create an issue for boot addons that are error or unknown state
        # Ignore stopped as single shot addons can be run at boot and this is successful exit
        # Timeout waiting for startup is not a failure, addon is probably just slow
        for addon in tasks:
            if addon.state in {AddonState.ERROR, AddonState.UNKNOWN}:
                self.sys_resolution.add_issue(
                    evolve(addon.boot_failed_issue),
                    suggestions=[
                        SuggestionType.EXECUTE_START,
                        SuggestionType.DISABLE_BOOT,
                    ],
                )

    async def shutdown(self, stage: AddonStartup) -> None:
        """Shutdown addons."""
        tasks: list[Addon] = []
        for addon in self.installed:
            if addon.state != AddonState.STARTED or addon.startup != stage:
                continue
            tasks.append(addon)

        # Evaluate add-ons which need to be stopped
        _LOGGER.info("Phase '%s' stopping %d add-ons", stage, len(tasks))
        if not tasks:
            return

        # Stop Add-ons sequential
        # avoid issue on slow IO
        for addon in tasks:
            try:
                await addon.stop()
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.warning("Can't stop Add-on %s: %s", addon.slug, err)
                await async_capture_exception(err)

    @Job(
        name="addon_manager_install",
        conditions=ADDON_UPDATE_CONDITIONS,
        on_condition=AddonsJobError,
    )
    async def install(self, slug: str) -> None:
        """Install an add-on."""
        self.sys_jobs.current.reference = slug

        if slug in self.local:
            raise AddonsError(f"Add-on {slug} is already installed", _LOGGER.warning)
        store = self.store.get(slug)

        if not store:
            raise AddonsError(f"Add-on {slug} does not exist", _LOGGER.error)

        store.validate_availability()

        await Addon(self.coresys, slug).install()

        _LOGGER.info("Add-on '%s' successfully installed", slug)

    @Job(name="addon_manager_uninstall")
    async def uninstall(self, slug: str, *, remove_config: bool = False) -> None:
        """Remove an add-on."""
        if slug not in self.local:
            _LOGGER.warning("Add-on %s is not installed", slug)
            return

        shared_image = any(
            self.local[slug].image == addon.image
            and self.local[slug].version == addon.version
            for addon in self.installed
            if addon.slug != slug
        )
        await self.local[slug].uninstall(
            remove_config=remove_config, remove_image=not shared_image
        )

        _LOGGER.info("Add-on '%s' successfully removed", slug)

    @Job(
        name="addon_manager_update",
        conditions=ADDON_UPDATE_CONDITIONS,
        on_condition=AddonsJobError,
    )
    async def update(
        self, slug: str, backup: bool | None = False
    ) -> asyncio.Task | None:
        """Update add-on.

        Returns a Task that completes when addon has state 'started' (see addon.start)
        if addon is started after update. Else nothing is returned.
        """
        self.sys_jobs.current.reference = slug

        if slug not in self.local:
            raise AddonsError(f"Add-on {slug} is not installed", _LOGGER.error)
        addon = self.local[slug]

        if addon.is_detached:
            raise AddonsError(
                f"Add-on {slug} is not available inside store", _LOGGER.error
            )
        store = self.store[slug]

        if addon.version == store.version:
            raise AddonsError(f"No update available for add-on {slug}", _LOGGER.warning)

        # Check if available, Maybe something have changed
        store.validate_availability()

        if backup:
            await self.sys_backups.do_backup_partial(
                name=f"addon_{addon.slug}_{addon.version}",
                homeassistant=False,
                addons=[addon.slug],
            )

        return await addon.update()

    @Job(
        name="addon_manager_rebuild",
        conditions=[
            JobCondition.FREE_SPACE,
            JobCondition.INTERNET_HOST,
            JobCondition.HEALTHY,
        ],
        on_condition=AddonsJobError,
    )
    async def rebuild(self, slug: str) -> asyncio.Task | None:
        """Perform a rebuild of local build add-on.

        Returns a Task that completes when addon has state 'started' (see addon.start)
        if addon is started after rebuild. Else nothing is returned.
        """
        self.sys_jobs.current.reference = slug

        if slug not in self.local:
            raise AddonsError(f"Add-on {slug} is not installed", _LOGGER.error)
        addon = self.local[slug]

        if addon.is_detached:
            raise AddonsError(
                f"Add-on {slug} is not available inside store", _LOGGER.error
            )
        store = self.store[slug]

        # Check if a rebuild is possible now
        if addon.version != store.version:
            raise AddonsError(
                "Version changed, use Update instead Rebuild", _LOGGER.error
            )
        if not addon.need_build:
            raise AddonsNotSupportedError(
                "Can't rebuild a image based add-on", _LOGGER.error
            )

        return await addon.rebuild()

    @Job(
        name="addon_manager_restore",
        conditions=[
            JobCondition.FREE_SPACE,
            JobCondition.INTERNET_HOST,
            JobCondition.HEALTHY,
        ],
        on_condition=AddonsJobError,
    )
    async def restore(
        self, slug: str, tar_file: tarfile.TarFile
    ) -> asyncio.Task | None:
        """Restore state of an add-on.

        Returns a Task that completes when addon has state 'started' (see addon.start)
        if addon is started after restore. Else nothing is returned.
        """
        self.sys_jobs.current.reference = slug

        if slug not in self.local:
            _LOGGER.debug("Add-on %s is not local available for restore", slug)
            addon = Addon(self.coresys, slug)
            had_ingress: bool | None = False
        else:
            _LOGGER.debug("Add-on %s is local available for restore", slug)
            addon = self.local[slug]
            had_ingress = addon.ingress_panel

        wait_for_start = await addon.restore(tar_file)

        # Check if new
        if slug not in self.local:
            _LOGGER.info("Detect new Add-on after restore %s", slug)
            self.local[slug] = addon

        # Update ingress
        if had_ingress != addon.ingress_panel:
            await self.sys_ingress.reload()
            with suppress(HomeAssistantAPIError):
                await self.sys_ingress.update_hass_panel(addon)

        return wait_for_start

    @Job(
        name="addon_manager_repair",
        conditions=[JobCondition.FREE_SPACE, JobCondition.INTERNET_HOST],
    )
    async def repair(self) -> None:
        """Repair local add-ons."""
        needs_repair: list[Addon] = []

        # Evaluate Add-ons to repair
        for addon in self.installed:
            if await addon.instance.exists():
                continue
            needs_repair.append(addon)

        _LOGGER.info("Found %d add-ons to repair", len(needs_repair))
        if not needs_repair:
            return

        for addon in needs_repair:
            _LOGGER.info("Repairing for add-on: %s", addon.slug)
            with suppress(DockerError, KeyError):
                # Need pull a image again
                if not addon.need_build:
                    await addon.instance.install(addon.version, addon.image)
                    continue

                # Need local lookup
                if addon.need_build and not addon.is_detached:
                    store = self.store[addon.slug]
                    # If this add-on is available for rebuild
                    if addon.version == store.version:
                        await addon.instance.install(addon.version, addon.image)
                        continue

            _LOGGER.error("Can't repair %s", addon.slug)
            with suppress(AddonsError):
                await self.uninstall(addon.slug)

    async def sync_dns(self) -> None:
        """Sync add-ons DNS names."""
        # Update hosts
        add_host_coros: list[Awaitable[None]] = []
        for addon in self.installed:
            try:
                if not await addon.instance.is_running():
                    continue
            except DockerError as err:
                _LOGGER.warning("Add-on %s is corrupt: %s", addon.slug, err)
                self.sys_resolution.create_issue(
                    IssueType.CORRUPT_DOCKER,
                    ContextType.ADDON,
                    reference=addon.slug,
                    suggestions=[SuggestionType.EXECUTE_REPAIR],
                )
                await async_capture_exception(err)
            else:
                add_host_coros.append(
                    self.sys_plugins.dns.add_host(
                        ipv4=addon.ip_address, names=[addon.hostname], write=False
                    )
                )

        await asyncio.gather(*add_host_coros)

        # Write hosts files
        with suppress(CoreDNSError):
            await self.sys_plugins.dns.write_hosts()
