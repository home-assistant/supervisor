"""Init file for Hass.io add-ons."""
import asyncio
from contextlib import suppress
import logging
import tarfile
from typing import Dict, List, Optional, Union

from ..const import BOOT_AUTO, STATE_STARTED
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

_LOGGER = logging.getLogger(__name__)

AnyAddon = Union[Addon, AddonStore]


class AddonManager(CoreSysAttributes):
    """Manage add-ons inside Hass.io."""

    def __init__(self, coresys: CoreSys):
        """Initialize Docker base wrapper."""
        self.coresys: CoreSys = coresys
        self.data: AddonsData = AddonsData(coresys)
        self.local: Dict[str, Addon] = {}
        self.store: Dict[str, AddonStore] = {}

    @property
    def all(self) -> List[AnyAddon]:
        """Return a list of all add-ons."""
        addons = {**self.store, **self.local}
        return list(addons.values())

    @property
    def installed(self) -> List[Addon]:
        """Return a list of all installed add-ons."""
        return list(self.local.values())

    def get(self, addon_slug: str) -> Optional[AnyAddon]:
        """Return an add-on from slug.

        Prio:
          1 - Local
          2 - Store
        """
        if addon_slug in self.local:
            return self.local[addon_slug]
        return self.store.get(addon_slug)

    def from_token(self, token: str) -> Optional[Addon]:
        """Return an add-on from Hass.io token."""
        for addon in self.installed:
            if token == addon.hassio_token:
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

    async def boot(self, stage: str) -> None:
        """Boot add-ons with mode auto."""
        tasks = []
        for addon in self.installed:
            if addon.boot != BOOT_AUTO or addon.startup != stage:
                continue
            tasks.append(addon.start())

        _LOGGER.info("Phase '%s' start %d add-ons", stage, len(tasks))
        if tasks:
            await asyncio.wait(tasks)
            await asyncio.sleep(self.sys_config.wait_boot)

    async def shutdown(self, stage: str) -> None:
        """Shutdown addons."""
        tasks = []
        for addon in self.installed:
            if await addon.state() != STATE_STARTED or addon.startup != stage:
                continue
            tasks.append(addon.stop())

        _LOGGER.info("Phase '%s' stop %d add-ons", stage, len(tasks))
        if tasks:
            await asyncio.wait(tasks)

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
        except DockerAPIError:
            self.data.uninstall(addon)
            raise AddonsError() from None
        else:
            self.local[slug] = addon
            _LOGGER.info("Add-on '%s' successfully installed", slug)

    async def uninstall(self, slug: str) -> None:
        """Remove an add-on."""
        if slug not in self.local:
            _LOGGER.warning("Add-on %s is not installed", slug)
            return
        addon = self.local.get(slug)

        try:
            await addon.instance.remove()
        except DockerAPIError:
            raise AddonsError() from None

        await addon.remove_data()

        # Cleanup audio settings
        if addon.path_asound.exists():
            with suppress(OSError):
                addon.path_asound.unlink()

        # Cleanup AppArmor profile
        with suppress(HostAppArmorError):
            await addon.uninstall_apparmor()

        # Cleanup Ingress panel from sidebar
        if addon.ingress_panel:
            addon.ingress_panel = False
            with suppress(HomeAssistantAPIError):
                await self.sys_ingress.update_hass_panel(addon)

        # Cleanup internal data
        addon.remove_discovery()

        self.data.uninstall(addon)
        self.local.pop(slug)

        _LOGGER.info("Add-on '%s' successfully removed", slug)

    async def update(self, slug: str) -> None:
        """Update add-on."""
        if slug not in self.local:
            _LOGGER.error("Add-on %s is not installed", slug)
            raise AddonsError()
        addon = self.local.get(slug)

        if addon.is_detached:
            _LOGGER.error("Add-on %s is not available inside store", slug)
            raise AddonsError()
        store = self.store.get(slug)

        if addon.version == store.version:
            _LOGGER.warning("No update available for add-on %s", slug)
            return

        # Check if available, Maybe something have changed
        if not store.available:
            _LOGGER.error("Add-on %s not supported on that platform", slug)
            raise AddonsNotSupportedError()

        # Update instance
        last_state = await addon.state()
        try:
            await addon.instance.update(store.version, store.image)

            # Cleanup
            with suppress(DockerAPIError):
                await addon.instance.cleanup()
        except DockerAPIError:
            raise AddonsError() from None
        else:
            self.data.update(store)
            _LOGGER.info("Add-on '%s' successfully updated", slug)

        # Setup/Fix AppArmor profile
        await addon.install_apparmor()

        # restore state
        if last_state == STATE_STARTED:
            await addon.start()

    async def rebuild(self, slug: str) -> None:
        """Perform a rebuild of local build add-on."""
        if slug not in self.local:
            _LOGGER.error("Add-on %s is not installed", slug)
            raise AddonsError()
        addon = self.local.get(slug)

        if addon.is_detached:
            _LOGGER.error("Add-on %s is not available inside store", slug)
            raise AddonsError()
        store = self.store.get(slug)

        # Check if a rebuild is possible now
        if addon.version != store.version:
            _LOGGER.error("Version changed, use Update instead Rebuild")
            raise AddonsError()
        if not addon.need_build:
            _LOGGER.error("Can't rebuild a image based add-on")
            raise AddonsNotSupportedError()

        # remove docker container but not addon config
        last_state = await addon.state()
        try:
            await addon.instance.remove()
            await addon.instance.install(addon.version)
        except DockerAPIError:
            raise AddonsError() from None
        else:
            self.data.update(store)
            _LOGGER.info("Add-on '%s' successfully rebuilded", slug)

        # restore state
        if last_state == STATE_STARTED:
            await addon.start()

    async def restore(self, slug: str, tar_file: tarfile.TarFile) -> None:
        """Restore state of an add-on."""
        if slug not in self.local:
            _LOGGER.debug("Add-on %s is not local available for restore")
            addon = Addon(self.coresys, slug)
        else:
            _LOGGER.debug("Add-on %s is local available for restore")
            addon = self.local[slug]

        await addon.restore(tar_file)

        # Check if new
        if slug in self.local:
            return

        _LOGGER.info("Detect new Add-on after restore %s", slug)
        self.local[slug] = addon

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

            with suppress(DockerAPIError, KeyError):
                # Need pull a image again
                if not addon.need_build:
                    await addon.instance.install(addon.version, addon.image)
                    continue

                # Need local lookup
                elif addon.need_build and not addon.is_detached:
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
            if not await addon.is_running():
                continue
            self.sys_dns.add_host(
                ipv4=addon.ip_address, names=[addon.hostname], write=False
            )

        # Write hosts files
        with suppress(CoreDNSError):
            self.sys_dns.write_hosts()
