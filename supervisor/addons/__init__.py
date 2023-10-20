"""Init file for Supervisor add-ons."""
import asyncio
from collections.abc import Awaitable
from contextlib import suppress
import logging
import tarfile
from typing import Union

from ..const import AddonBoot, AddonStartup, AddonState
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import (
    AddonConfigurationError,
    AddonsError,
    AddonsJobError,
    AddonsNotSupportedError,
    CoreDNSError,
    DockerAPIError,
    DockerError,
    DockerNotFound,
    HomeAssistantAPIError,
    HostAppArmorError,
)
from ..jobs.decorator import Job, JobCondition
from ..resolution.const import ContextType, IssueType, SuggestionType
from ..store.addon import AddonStore
from ..utils import check_exception_chain
from ..utils.sentry import capture_exception
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

    async def load(self) -> None:
        """Start up add-on management."""
        tasks = []
        for slug in self.data.system:
            addon = self.local[slug] = Addon(self.coresys, slug)
            tasks.append(self.sys_create_task(addon.load()))

        # Run initial tasks
        _LOGGER.info("Found %d installed add-ons", len(tasks))
        if tasks:
            await asyncio.wait(tasks)

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
            except AddonsError as err:
                # Check if there is an system/user issue
                if check_exception_chain(
                    err, (DockerAPIError, DockerNotFound, AddonConfigurationError)
                ):
                    addon.boot = AddonBoot.MANUAL
                    addon.save_persist()
            except Exception as err:  # pylint: disable=broad-except
                capture_exception(err)
            else:
                continue

            _LOGGER.warning("Can't start Add-on %s", addon.slug)

        # Ignore exceptions from waiting for addon startup, addon errors handled elsewhere
        await asyncio.gather(*wait_boot, return_exceptions=True)

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
                capture_exception(err)

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

        self.data.install(store)
        addon = Addon(self.coresys, slug)
        await addon.load()

        if not addon.path_data.is_dir():
            _LOGGER.info(
                "Creating Home Assistant add-on data folder %s", addon.path_data
            )
            addon.path_data.mkdir()

        # Setup/Fix AppArmor profile
        await addon.install_apparmor()

        try:
            await addon.instance.install(store.version, store.image, arch=addon.arch)
        except DockerError as err:
            self.data.uninstall(addon)
            raise AddonsError() from err

        self.local[slug] = addon

        # Reload ingress tokens
        if addon.with_ingress:
            await self.sys_ingress.reload()

        _LOGGER.info("Add-on '%s' successfully installed", slug)

    async def uninstall(self, slug: str) -> None:
        """Remove an add-on."""
        if slug not in self.local:
            _LOGGER.warning("Add-on %s is not installed", slug)
            return
        addon = self.local[slug]

        try:
            await addon.instance.remove()
        except DockerError as err:
            raise AddonsError() from err

        addon.state = AddonState.UNKNOWN

        await addon.unload()

        # Cleanup audio settings
        if addon.path_pulse.exists():
            with suppress(OSError):
                addon.path_pulse.unlink()

        # Cleanup AppArmor profile
        with suppress(HostAppArmorError):
            await addon.uninstall_apparmor()

        # Cleanup Ingress panel from sidebar
        if addon.ingress_panel:
            addon.ingress_panel = False
            with suppress(HomeAssistantAPIError):
                await self.sys_ingress.update_hass_panel(addon)

        # Cleanup Ingress dynamic port assignment
        if addon.with_ingress:
            self.sys_create_task(self.sys_ingress.reload())
            self.sys_ingress.del_dynamic_port(slug)

        # Cleanup discovery data
        for message in self.sys_discovery.list_messages:
            if message.addon != addon.slug:
                continue
            self.sys_discovery.remove(message)

        # Cleanup services data
        for service in self.sys_services.list_services:
            if addon.slug not in service.active:
                continue
            service.del_service_data(addon)

        self.data.uninstall(addon)
        self.local.pop(slug)

        _LOGGER.info("Add-on '%s' successfully removed", slug)

    @Job(
        name="addon_manager_update",
        conditions=ADDON_UPDATE_CONDITIONS,
        on_condition=AddonsJobError,
    )
    async def update(
        self, slug: str, backup: bool | None = False
    ) -> Awaitable[None] | None:
        """Update add-on.

        Returns a coroutine that completes when addon has state 'started' (see addon.start)
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

        # Update instance
        old_image = addon.image
        # Cache data to prevent races with other updates to global
        store = store.clone()

        try:
            await addon.instance.update(store.version, store.image)
        except DockerError as err:
            raise AddonsError() from err

        # Stop the addon if running
        if (last_state := addon.state) in {AddonState.STARTED, AddonState.STARTUP}:
            await addon.stop()

        try:
            _LOGGER.info("Add-on '%s' successfully updated", slug)
            self.data.update(store)

            # Cleanup
            with suppress(DockerError):
                await addon.instance.cleanup(
                    old_image=old_image, image=store.image, version=store.version
                )

            # Setup/Fix AppArmor profile
            await addon.install_apparmor()

        finally:
            # restore state. Return awaitable for caller if no exception
            out = (
                await addon.start()
                if last_state in {AddonState.STARTED, AddonState.STARTUP}
                else None
            )
        return out

    @Job(
        name="addon_manager_rebuild",
        conditions=[
            JobCondition.FREE_SPACE,
            JobCondition.INTERNET_HOST,
            JobCondition.HEALTHY,
        ],
        on_condition=AddonsJobError,
    )
    async def rebuild(self, slug: str) -> Awaitable[None] | None:
        """Perform a rebuild of local build add-on.

        Returns a coroutine that completes when addon has state 'started' (see addon.start)
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

        # remove docker container but not addon config
        last_state: AddonState = addon.state
        try:
            await addon.instance.remove()
            await addon.instance.install(addon.version)
        except DockerError as err:
            raise AddonsError() from err

        self.data.update(store)
        _LOGGER.info("Add-on '%s' successfully rebuilt", slug)

        # restore state
        return (
            await addon.start()
            if last_state in [AddonState.STARTED, AddonState.STARTUP]
            else None
        )

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
    ) -> Awaitable[None] | None:
        """Restore state of an add-on.

        Returns a coroutine that completes when addon has state 'started' (see addon.start)
        if addon is started after restore. Else nothing is returned.
        """
        self.sys_jobs.current.reference = slug

        if slug not in self.local:
            _LOGGER.debug("Add-on %s is not local available for restore", slug)
            addon = Addon(self.coresys, slug)
            had_ingress = False
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
                capture_exception(err)
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
