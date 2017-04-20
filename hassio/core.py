"""Main file for HassIO."""
import asyncio
import logging

import aiohttp
import docker

from . import bootstrap
from .addons import AddonManager
from .api import RestAPI
from .host_controll import HostControll
from .const import (
    SOCKET_DOCKER, RUN_UPDATE_INFO_TASKS, RUN_RELOAD_ADDONS_TASKS,
    RUN_UPDATE_SUPERVISOR_TASKS, STARTUP_AFTER, STARTUP_BEFORE)
from .scheduler import Scheduler
from .dock.homeassistant import DockerHomeAssistant
from .dock.supervisor import DockerSupervisor
from .tools import get_arch_from_image, get_local_ip

_LOGGER = logging.getLogger(__name__)


class HassIO(object):
    """Main object of hassio."""

    def __init__(self, loop):
        """Initialize hassio object."""
        self.exit_code = 0
        self.loop = loop
        self.websession = aiohttp.ClientSession(loop=self.loop)
        self.config = bootstrap.initialize_system_data(self.websession)
        self.scheduler = Scheduler(self.loop)
        self.api = RestAPI(self.config, self.loop)
        self.dock = docker.DockerClient(
            base_url="unix:/{}".format(SOCKET_DOCKER), version='auto')

        # init basic docker container
        self.supervisor = DockerSupervisor(
            self.config, self.loop, self.dock, self)
        self.homeassistant = DockerHomeAssistant(
            self.config, self.loop, self.dock)

        # init HostControll
        self.host_controll = HostControll(self.loop)

        # init addon system
        self.addons = AddonManager(self.config, self.loop, self.dock)

    async def setup(self):
        """Setup HassIO orchestration."""
        # supervisor
        await self.supervisor.attach()
        await self.supervisor.cleanup()

        # set api endpoint
        self.config.api_endpoint = await get_local_ip(self.loop)

        # hostcontroll
        host_info = await self.host_controll.info()
        if host_info:
            self.host_controll.version = host_info.get('version')
            _LOGGER.info(
                "Connected to HostControll. OS: %s Version: %s Hostname: %s "
                "Feature-lvl: %d", host_info.get('os'),
                host_info.get('version'), host_info.get('hostname'),
                host_info.get('level', 0))

        # rest api views
        self.api.register_host(self.host_controll)
        self.api.register_network(self.host_controll)
        self.api.register_supervisor(self.supervisor, self.addons)
        self.api.register_homeassistant(self.homeassistant)
        self.api.register_addons(self.addons)

        # schedule update info tasks
        self.scheduler.register_task(
            self.config.fetch_update_infos, RUN_UPDATE_INFO_TASKS,
            now=True)

        # first start of supervisor?
        if not await self.homeassistant.exists():
            _LOGGER.info("No HomeAssistant docker found.")
            await self._setup_homeassistant()

        # Load addons
        arch = get_arch_from_image(self.supervisor.image)
        await self.addons.prepare(arch)

        # schedule addon update task
        self.scheduler.register_task(
            self.addons.relaod, RUN_RELOAD_ADDONS_TASKS, now=True)

        # schedule self update task
        self.scheduler.register_task(
            self._hassio_update, RUN_UPDATE_SUPERVISOR_TASKS)

    async def start(self):
        """Start HassIO orchestration."""
        # start api
        await self.api.start()
        _LOGGER.info("Start hassio api on %s", self.config.api_endpoint)

        # HomeAssistant is already running / supervisor have only reboot
        if await self.homeassistant.is_running():
            _LOGGER.info("HassIO reboot detected")
            return

        # start addon mark as before
        await self.addons.auto_boot(STARTUP_BEFORE)

        # run HomeAssistant
        await self.homeassistant.run()

        # start addon mark as after
        await self.addons.auto_boot(STARTUP_AFTER)

    async def stop(self, exit_code=0):
        """Stop a running orchestration."""
        # don't process scheduler anymore
        self.scheduler.stop()

        # process stop task pararell
        tasks = [self.websession.close(), self.api.stop()]
        await asyncio.wait(tasks, loop=self.loop)

        self.exit_code = exit_code
        self.loop.stop()

    async def _setup_homeassistant(self):
        """Install a homeassistant docker container."""
        while True:
            # read homeassistant tag and install it
            if not self.config.current_homeassistant:
                await self.config.fetch_update_infos()

            tag = self.config.current_homeassistant
            if tag and await self.homeassistant.install(tag):
                break
            _LOGGER.warning("Error on setup HomeAssistant. Retry in 60.")
            await asyncio.sleep(60, loop=self.loop)

        # store version
        _LOGGER.info("HomeAssistant docker now installed.")

    async def _hassio_update(self):
        """Check and run update of supervisor hassio."""
        if self.config.current_hassio == self.supervisor.version:
            return

        _LOGGER.info(
            "Found new HassIO version %s.", self.config.current_hassio)
        await self.supervisor.update(self.config.current_hassio)
