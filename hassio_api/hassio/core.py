"""Main file for HassIO."""
import asyncio
import logging

import aiohttp
import docker

from . import bootstrap, tools
from .api import RestAPI
from .host_controll import HostControll
from .const import HOMEASSISTANT_TAG, SOCKET_DOCKER
from .dock.homeassistant import DockerHomeAssistant
from .dock.supervisor import DockerSupervisor

_LOGGER = logging.getLogger(__name__)


class HassIO(object):
    """Main object of hassio."""

    def __init__(self, loop):
        """Initialize hassio object."""
        self.loop = loop
        self.config = bootstrap.initialize_system_data()
        self.websession = aiohttp.ClientSession(loop=self.loop)
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

    async def start(self):
        """Start HassIO orchestration."""
        # supervisor
        await self.supervisor.attach()
        _LOGGER.info(
            "Attach to supervisor image %s version %s", self.supervisor.image,
            self.supervisor.version)

        # hostcontroll
        host_info = await self.host_controll.info()
        if host_info:
            _LOGGER.info(
                "Connected to HostControll. OS: %s Version: %s Hostname: %s "
                "Feature-lvl: %d", host_info.get('os'),
                host_info.get('version'), host_info.get('hostname'),
                host_info.get('level'))

        # rest api views
        self.api.registerHost(self.host_controll)
        self.api.registerSupervisor(self.host_controll)
        self.api.registerHomeAssistant(self.homeassistant)

        # first start of supervisor?
        if self.config.homeassistant_tag is None:
            _LOGGER.info("No HomeAssistant docker found.")
            await self._setup_homeassistant()

        # start api
        await self.api.start()

        # run HomeAssistant
        _LOGGER.info("Run HomeAssistant now.")
        await self.homeassistant.run()

    async def stop(self):
        """Stop a running orchestration."""
        tasks = [self.websession.close(), self.api.stop()]
        await asyncio.wait(tasks, loop=self.loop)

        self.loop.close()

    async def _setup_homeassistant(self):
        """Install a homeassistant docker container."""
        current = None
        while True:
            # read homeassistant tag and install it
            current = await tools.fetch_current_versions(self.websession)
            if current and HOMEASSISTANT_TAG in current:
                resp = await self.homeassistant.install(
                    current[HOMEASSISTANT_TAG])
                if resp:
                    break
            _LOGGER.warning("Error on setup HomeAssistant. Retry in 60.")
            await asyncio.sleep(60, loop=self.loop)

        # store version
        self.config.homeassistant_tag = current[HOMEASSISTANT_TAG]
        _LOGGER.info("HomeAssistant docker now exists.")
