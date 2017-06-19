"""Init file for HassIO addons."""
import asyncio
import logging
import shutil

from .addon import Addon
from .data import AddonsData
from .git import AddonsRepoHassIO, AddonsRepoCustom
from ..const import STATE_STOPPED, STATE_STARTED
from ..dock.addon import DockerAddon

_LOGGER = logging.getLogger(__name__)


class AddonManager(AddonsData):
    """Manage addons inside HassIO."""

    def __init__(self, config, loop, dock):
        """Initialize docker base wrapper."""
        self.loop = loop
        self.dock = dock
        self.data = AddonsData(config)
        self.repositories = []
        self.dockers = {}

    @property
    def list_installed(self):
        """Return a list of installed addons."""
        return set(Addon(self.data, slug) for slug in self.data.system)

    @property
    def list_all(self):
        """Return a dict of all addons."""
        return set(self._system_data) | set(self._cache_data)

    def list_startup(self, start_type):
        """Get list of installed addon with need start by type."""
        addon_list = set()
        for addon in self._system_data.keys():
            if self.get_boot(addon) != BOOT_AUTO:
                continue

            try:
                if self._system_data[addon][ATTR_STARTUP] == start_type:
                    addon_list.add(addon)
            except KeyError:
                _LOGGER.warning("Orphaned addon detect %s", addon)
                continue

        return addon_list

    @property
    def list_detached(self):
        """Return local addons they not support from repo."""
        addon_list = set()
        for addon in self._system_data.keys():
            if addon not in self._cache_data:
                addon_list.add(addon)

        return addon_list

    @property
    def list_repositories(self):
        """Return list of addon repositories."""
        return list(self.repositories.values())

    async def prepare(self, arch):
        """Startup addon management."""
        self.arch = arch
        self.data.arch = self.arch

        # init hassio repository
        self.repositories.append(AddonsRepoHassIO(self.config, self.loop))

        # init custom repositories
        for url in self.config.addons_repositories:
            self.repositories.append(
                AddonsRepoCustom(self.config, self.loop, url))

        # load addon repository
        tasks = [addon.load() for addon in self.repositories]
        if tasks:
            await asyncio.wait(tasks, loop=self.loop)

            # read data from repositories
            self.data.read_data_from_repositories()
            self.data.merge_update_config()

        # load installed addons
        for addon_slug in self.data.list_installed:
            addon = Addon(self.data, addon_slug)

            self.dockers[addon.slug] = DockerAddon(
                self.config, self.loop, self.dock, addon)
            await self.dockers[addon.slug].attach()

    async def add_git_repository(self, url):
        """Add a new custom repository."""
        if url in self.config.addons_repositories:
            _LOGGER.warning("Repository already exists %s", url)
            return False

        repo = AddonsRepoCustom(self.config, self.loop, url)

        if not await repo.load():
            _LOGGER.error("Can't load from repository %s", url)
            return False

        self.config.addons_repositories = url
        self.repositories.append(repo)
        return True

    def drop_git_repository(self, url):
        """Remove a custom repository."""
        for repo in self.repositories:
            if repo.url == url:
                self.repositories.remove(repo)
                self.config.drop_addon_repository(url)
                repo.remove()
                return True

        return False

    async def reload(self):
        """Update addons from repo and reload list."""
        tasks = [repository.pull() for repository in self.repositories]
        if not tasks:
            return

        await asyncio.wait(tasks, loop=self.loop)

        # read data from repositories
        self.data.read_data_from_repositories()
        self.data.merge_update_config()

        # remove stalled addons
        for addon_slug in self.data.list_detached:
            _LOGGER.warning("Dedicated addon '%s' found!", addon_slug)

    async def auto_boot(self, start_type):
        """Boot addons with mode auto."""
        tasks = []
        for addon_slug in self.data.list_startup(start_type):
           tasks.append(self.start(Addon(self.data, addon_slug))

        _LOGGER.info("Startup %s run %d addons", start_type, len(tasks))
        if tasks:
            await asyncio.wait(tasks, loop=self.loop)

    async def install(self, addon, version=None):
        """Install a addon."""
        if self.arch not in addon.supported_arch:
            _LOGGER.error("Addon %s not supported on %s", addon, self.arch)
            return False

        if addon.is_installed:
            _LOGGER.error("Addon %s is already installed", addon)
            return False

        if not addon.path_data.is_dir():
            _LOGGER.info(
                "Create Home-Assistant addon data folder %s", addon.path_data)
            addon.path_data.mkdir()

        addon_docker = DockerAddon(self.config, self.loop, self.dock, addon)

        version = version or addon.last_version
        if not await addon_docker.install(version):
            return False

        self.dockers[addon.slug] = addon_docker
        addon.set_install(version)
        return True

    async def uninstall(self, addon):
        """Remove a addon."""
        if not addon.is_installed:
            _LOGGER.error("Addon %s is already uninstalled", addon)
            return False

        if addon.slug not in self.dockers:
            _LOGGER.error("No docker found for addon %s", addon)
            return False

        if not await self.dockers[addon.slug].remove():
            return False

        if addon.path_data.is_dir():
            _LOGGER.info(
                "Remove Home-Assistant addon data folder %s", addon.path_data)
            shutil.rmtree(str(addon.path_data))

        self.dockers.pop(addon.slug)
        addon.set_uninstall()
        return True

    async def state(self, addon):
        """Return running state of addon."""
        if addon.slug not in self.dockers:
            _LOGGER.error("No docker found for addon %s", addon)
            return

        if await self.dockers[addon.slug].is_running():
            return STATE_STARTED
        return STATE_STOPPED

    async def start(self, addon):
        """Set options and start addon."""
        if addon.slug not in self.dockers:
            _LOGGER.error("No docker found for addon %s", addon)
            return False

        if not addon.write_addon_options():
            _LOGGER.error("Can't write options for addon %s", addon)
            return False

        return await self.dockers[addon.slug].run()

    async def stop(self, addon):
        """Stop addon."""
        if addon.slug not in self.dockers:
            _LOGGER.error("No docker found for addon %s", addon)
            return False

        return await self.dockers[addon.slug].stop()

    async def update(self, addon, version=None):
        """Update addon."""
        if addon.slug not in self.dockers:
            _LOGGER.error("No docker found for addon %s", addon)
            return False

        version = version or addon.last_version

        # update
        if not await self.dockers[addon.slug].update(version):
            return False

        addon.set_update(version)
        return True

    async def restart(self, addon):
        """Restart addon."""
        if addon.slug not in self.dockers:
            _LOGGER.error("No docker found for addon %s", addon)
            return False

        if not addon.write_addon_options():
            _LOGGER.error("Can't write options for addon %s", addon)
            return False

        return await self.dockers[addon.slug].restart()

    async def logs(self, addon):
        """Return addons log output."""
        if addon.slug not in self.dockers:
            _LOGGER.error("No docker found for addon %s", addon)
            return False

        return await self.dockers[addon.slug].logs()
