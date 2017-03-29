"""Main file for HassIO."""
import asyncio
import logging

import aiohttp
import docker

from . import bootstrap, tools
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
        """Start HassIO."""
        await self.supervisor.attach()
        _LOGGER.info(
            "Attach to supervisor image %s tag %s", self.supervisor.image,
            self.supervisor.tag)

        host_info = await self.host_controll.info()
        if host_info:
            _LOGGER.info(
                "Connected to host controll daemon. OS: %s Version: %s",
                host_info.get('host'), host_info.get('version'))

        # first start of supervisor?
        if self.config.homeassistant_tag is None:
            _LOGGER.info("No HomeAssistant docker found. Install it now")

            # read homeassistant tag and install it
            current = None
            while True:
                current = await tools.fetch_current_versions(self.websession)
                if current and HOMEASSISTANT_TAG in current:
                    resp = await self.homeassistant.install(
                        current[HOMEASSISTANT_TAG])
                    if resp:
                        break
                _LOGGER.warning("Can't fetch info from github. Retry in 60.")
                await asyncio.sleep(60, loop=self.loop)

            self.config.homeassistant_tag = current[HOMEASSISTANT_TAG]
        else:
            _LOGGER.info("HomeAssistant docker is exists.")

        # run HomeAssistant
        await self.homeassistant.run()
