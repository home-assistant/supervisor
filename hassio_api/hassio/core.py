"""Main file for HassIO."""
import asyncio
import logging

import aiohttp
import docker

from . import bootstrap
from .api import RestAPI
from .host_controll import HostControll
from .const import SOCKET_DOCKER, RUN_UPDATE_INFO_TASKS
from .scheduler import Scheduler
from .dock.homeassistant import DockerHomeAssistant
from .dock.supervisor import DockerSupervisor

_LOGGER = logging.getLogger(__name__)


class HassIO(object):
    """Main object of hassio."""

    def __init__(self, loop):
        """Initialize hassio object."""
        self.loop = loop
        self.websession = aiohttp.ClientSession(loop=self.loop)
        self.config = bootstrap.initialize_system_data(self.websession)
        self.scheduler = Scheduler(self.loop)
        self.api = RestAPI(self.config, self.loop)
        self.dock = docker.DockerClient(
            base_url="unix:/{}".format(SOCKET_DOCKER), version='auto')

        # init basic docker container
        self.supervisor = DockerSupervisor(
            self.config, self.loop, self.dock)
        self.homeassistant = DockerHomeAssistant(
            self.config, self.loop, self.dock)

        # init HostControll
        self.host_controll = HostControll(self.loop)

    async def setup(self):
        """Setup HassIO orchestration."""
        # supervisor
        await self.supervisor.attach()

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
        self.api.register_supervisor(self.host_controll)
        self.api.register_homeassistant(self.homeassistant)

        # schedule update info tasks
        self.scheduler.register_task(
            self.config.fetch_update_infos, RUN_UPDATE_INFO_TASKS,
            first_run=True)

        # first start of supervisor?
        if not await self.homeassistant.exists():
            _LOGGER.info("No HomeAssistant docker found.")
            await self._setup_homeassistant()

    async def start(self):
        """Start HassIO orchestration."""
        # start api
        await self.api.start()

        # run HomeAssistant
        await self.homeassistant.run()

    async def stop(self):
        """Stop a running orchestration."""
        tasks = [self.websession.close(), self.api.stop()]
        await asyncio.wait(tasks, loop=self.loop)

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
