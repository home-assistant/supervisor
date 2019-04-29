"""Init file for Hass.io add-ons."""
import asyncio
import logging
from typing import Dict, List, Optional

from .addon import Addon
from .data import AddonsData
from ..const import BOOT_AUTO, STATE_STARTED
from ..coresys import CoreSys, CoreSysAttributes

_LOGGER = logging.getLogger(__name__)


class AddonManager(CoreSysAttributes):
    """Manage add-ons inside Hass.io."""

    def __init__(self, coresys: CoreSys):
        """Initialize Docker base wrapper."""
        self.coresys: CoreSys = coresys
        self.data: AddonsData = AddonsData(coresys)
        self.addons: Dict[str, Addon] = {}

    @property
    def all(self) -> List[Addon]:
        """Return a list of all installed add-ons."""
        return list(self.addons.values())

    def get(self, addon_slug: str) -> Optional[Addon]:
        """Return an add-on from slug."""
        return self.addons.get(addon_slug)

    def from_token(self, token: str) -> Optional[Addon]:
        """Return an add-on from Hass.io token."""
        for addon in self.all:
            if addon.is_installed and token == addon.hassio_token:
                return addon
        return None

    async def load(self) -> None:
        """Start up add-on management."""
        self.data.reload()

        # Initialize and load add-ons
        await self.load_addons()

    async def reload(self) -> None:
        """Update add-ons from repository and reload list."""
        self.data.reload()

        # update addons
        await self.load_addons()

    async def load_addons(self) -> None:
        """Update/add internal add-on store."""
        all_addons = set(self.data.system) | set(self.data.cache)

        # calc diff
        add_addons = all_addons - set(self.addons)
        del_addons = set(self.addons) - all_addons

        _LOGGER.info("Load add-ons: %d all - %d new - %d remove",
                     len(all_addons), len(add_addons), len(del_addons))

        # new addons
        tasks = []
        for addon_slug in add_addons:
            addon = Addon(self.coresys, addon_slug)

            tasks.append(addon.load())
            self.addons[addon_slug] = addon

        if tasks:
            await asyncio.wait(tasks)

        # remove
        for addon_slug in del_addons:
            self.addons.pop(addon_slug)

    async def boot(self, stage: str) -> None:
        """Boot add-ons with mode auto."""
        tasks = []
        for addon in self.addons.values():
            if addon.is_installed and addon.boot == BOOT_AUTO and \
                    addon.startup == stage:
                tasks.append(addon.start())

        _LOGGER.info("Startup %s run %d add-ons", stage, len(tasks))
        if tasks:
            await asyncio.wait(tasks)
            await asyncio.sleep(self.sys_config.wait_boot)

    async def shutdown(self, stage: str) -> None:
        """Shutdown addons."""
        tasks = []
        for addon in self.addons.values():
            if addon.is_installed and \
                    await addon.state() == STATE_STARTED and \
                    addon.startup == stage:
                tasks.append(addon.stop())

        _LOGGER.info("Shutdown %s stop %d add-ons", stage, len(tasks))
        if tasks:
            await asyncio.wait(tasks)
