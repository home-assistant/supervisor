"""Init file for Supervisor add-ons."""
import asyncio
from contextlib import suppress
import logging
import tarfile
from typing import Dict, List, Optional, Union

from ..const import BOOT_AUTO, AddonStartup, AddonState
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import (
    AddonsError,
    AddonsNotSupportedError,
    CoreDNSError,
    DockerAPIError,
    HomeAssistantAPIError,
    HostAppArmorError,
)
from ..store.addon import AddonStore
from .addon import Addon
from .data import AddonsData

_LOGGER: logging.Logger = logging.getLogger(__name__)

AnyAddon = Union[Addon, AddonStore]


class AddonManager(CoreSysAttributes):
    """Manage add-ons inside Supervisor."""

    def __init__(self, coresys: CoreSys):
        """Initialize Docker base wrapper."""
        self.coresys: CoreSys = coresys
        self.data: AddonsData = AddonsData(coresys)
        self.local: Dict[str, Addon] = {}
        self.store: Dict[str, AddonStore] = {}

    @property
    def all(self) -> List[AnyAddon]:
        """Return a list of all add-ons."""
        addons: Dict[str, AnyAddon] = {**self.store, **self.local}
        return list(addons.values())

    @property
    def installed(self) -> List[Addon]:
        """Return a list of all installed add-ons."""
        return list(self.local.values())

    def get(self, addon_slug: str, local_only: bool = False) -> Optional[AnyAddon]:
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

    def from_token(self, token: str) -> Optional[Addon]:
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
            tasks.append(addon.load())

        # Run initial tasks
        _LOGGER.info("Found %d installed add-ons", len(tasks))
        if tasks:
            await asyncio.wait(tasks)

        # Sync DNS
        await self.sync_dns()

    async def boot(self, stage: AddonStartup) -> None:
        """Boot add-ons with mode auto."""
        tasks: List[Addon] = []
        for addon in self.installed:
            if addon.boot != BOOT_AUTO or addon.startup != stage:
                continue
            tasks.append(addon)

        # Evaluate add-ons which need to be started
        _LOGGER.info("Phase '%s' start %d add-ons", stage, len(tasks))
        if not tasks:
            return

        # Start Add-ons sequential
        # avoid issue on slow IO
        for addon in tasks:
            try:
                await addon.start()
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.warning("Can't start Add-on %s: %s", addon.slug, err)
                self.sys_capture_exception(err)

        await asyncio.sleep(self.sys_config.wait_boot)

    async def shutdown(self, stage: AddonStartup) -> None:
        """Shutdown addons."""
        tasks: List[Addon] = []
        for addon in self.installed:
            if await addon.state() != AddonState.STARTED or addon.startup != stage:
                continue
            tasks.append(addon)

        # Evaluate add-ons which need to be stopped
        _LOGGER.info("Phase '%s' stop %d add-ons", stage, len(tasks))
        if not tasks:
            return

        # Stop Add-ons sequential
        # avoid issue on slow IO
        for addon in tasks:
            try:
                await addon.stop()
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.warning("Can't stop Add-on %s: %s", addon.slug, err)
                self.sys_capture_exception(err)

    async def install(self, slug: str) -> None:
        """Install an add-on."""
        if slug in self.local:
            _LOGGER.warning("Add-on %s is already installed", slug)
            return
        store = self.store.get(slug)

        if not store:
            _LOGGER.error("Add-on %s not exists", slug)
            raise AddonsError()

        if not store.available:
            _LOGGER.error("Add-on %s not supported on that platform", slug)
            raise AddonsNotSupportedError()

        self.data.install(store)
        addon = Addon(self.coresys, slug)

        if not addon.path_data.is_dir():
            _LOGGER.info("Create Home Assistant add-on data folder %s", addon.path_data)
            addon.path_data.mkdir()

        # Setup/Fix AppArmor profile
        await addon.install_apparmor()

        try:
            await addon.instance.install(store.version, store.image)
        except DockerAPIError as err:
            self.data.uninstall(addon)
            raise AddonsError() from err
        else:
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
        except DockerAPIError as err:
            raise AddonsError() from err

        await addon.remove_data()

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

    async def update(self, slug: str) -> None:
        """Update add-on."""
        if slug not in self.local:
            _LOGGER.error("Add-on %s is not installed", slug)
            raise AddonsError()
        addon = self.local[slug]

        if addon.is_detached:
            _LOGGER.error("Add-on %s is not available inside store", slug)
            raise AddonsError()
        store = self.store[slug]

        if addon.version == store.version:
            _LOGGER.warning("No update available for add-on %s", slug)
            return

        # Check if available, Maybe something have changed
        if not store.available:
            _LOGGER.error("Add-on %s not supported on that platform", slug)
            raise AddonsNotSupportedError()

        # Update instance
        last_state: AddonState = await addon.state()
        try:
            await addon.instance.update(store.version, store.image)

            # Cleanup
            with suppress(DockerAPIError):
                await addon.instance.cleanup()
        except DockerAPIError as err:
            raise AddonsError() from err
        else:
            self.data.update(store)
            _LOGGER.info("Add-on '%s' successfully updated", slug)

        # Setup/Fix AppArmor profile
        await addon.install_apparmor()

        # restore state
        if last_state == AddonState.STARTED:
            await addon.start()

    async def rebuild(self, slug: str) -> None:
        """Perform a rebuild of local build add-on."""
        if slug not in self.local:
            _LOGGER.error("Add-on %s is not installed", slug)
            raise AddonsError()
        addon = self.local[slug]

        if addon.is_detached:
            _LOGGER.error("Add-on %s is not available inside store", slug)
            raise AddonsError()
        store = self.store[slug]

        # Check if a rebuild is possible now
        if addon.version != store.version:
            _LOGGER.error("Version changed, use Update instead Rebuild")
            raise AddonsError()
        if not addon.need_build:
            _LOGGER.error("Can't rebuild a image based add-on")
            raise AddonsNotSupportedError()

        # remove docker container but not addon config
        last_state: AddonState = await addon.state()
        try:
            await addon.instance.remove()
            await addon.instance.install(addon.version)
        except DockerAPIError as err:
            raise AddonsError() from err
        else:
            self.data.update(store)
            _LOGGER.info("Add-on '%s' successfully rebuilt", slug)

        # restore state
        if last_state == AddonState.STARTED:
            await addon.start()

    async def restore(self, slug: str, tar_file: tarfile.TarFile) -> None:
        """Restore state of an add-on."""
        if slug not in self.local:
            _LOGGER.debug("Add-on %s is not local available for restore", slug)
            addon = Addon(self.coresys, slug)
        else:
            _LOGGER.debug("Add-on %s is local available for restore", slug)
            addon = self.local[slug]

        await addon.restore(tar_file)

        # Check if new
        if slug not in self.local:
            _LOGGER.info("Detect new Add-on after restore %s", slug)
            self.local[slug] = addon

        # Update ingress
        if addon.with_ingress:
            await self.sys_ingress.reload()
            with suppress(HomeAssistantAPIError):
                await self.sys_ingress.update_hass_panel(addon)

    async def repair(self) -> None:
        """Repair local add-ons."""
        needs_repair: List[Addon] = []

        # Evaluate Add-ons to repair
        for addon in self.installed:
            if await addon.instance.exists():
                continue
            needs_repair.append(addon)

        _LOGGER.info("Found %d add-ons to repair", len(needs_repair))
        if not needs_repair:
            return

        for addon in needs_repair:
            _LOGGER.info("Start repair for add-on: %s", addon.slug)
            await self.sys_run_in_executor(
                self.sys_docker.network.stale_cleanup, addon.instance.name
            )

            with suppress(DockerAPIError, KeyError):
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
        for addon in self.installed:
            if not await addon.instance.is_running():
                continue
            self.sys_plugins.dns.add_host(
                ipv4=addon.ip_address, names=[addon.hostname], write=False
            )

        # Write hosts files
        with suppress(CoreDNSError):
            self.sys_plugins.dns.write_hosts()
