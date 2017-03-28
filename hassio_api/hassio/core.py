"""Main file for HassIO."""
import asyncio
import logging

import aiohttp
import docker

from . import bootstrap, tools
from .host_controll import HostControll
from .const import HOMEASSISTANT_TAG, SOCKET_DOCKER
from .docker.homeassistant import DockerHomeAssistant
from .docker.supervisor import DockerSupervisor

_LOGGER = logging.getLogger(__name__)


async def run_hassio(loop):
    """Start HassIO."""
    websession = aiohttp.ClientSession(loop=loop)
    dock = docker.DockerClient(
        base_url="unix:/{}".format(SOCKET_DOCKER), version='auto')

    # init system
    config = bootstrap.initialize_system_data()

    # init Supervisor Docker
    docker_super = DockerSupervisor(config, loop, dock)
    await docker_super.attach()

    # init HomeAssistant Docker
    docker_hass = DockerHomeAssistant(
        config, loop, dock, image=config.homeassistant_image,
        tag=config.homeassistant_tag
    )

    # init hostcontroll
    host_controll = HostControll(loop)
    await host_controll.info()

    # first start of supervisor?
    if config.homeassistant_tag is None:
        _LOGGER.info("First start of supervisor, read version from github.")

        # read homeassistant tag and install it
        current = None
        while True:
            current = await tools.fetch_current_versions(websession)
            if current and HOMEASSISTANT_TAG in current:
                if await docker_hass.install(current[HOMEASSISTANT_TAG]):
                    break
            _LOGGER.warning("Can't fetch info from github. Retry in 60.")
            await asyncio.sleep(60, loop=loop)

        config.homeassistant_tag = current[HOMEASSISTANT_TAG]
    else:
        _LOGGER.info("HomeAssistant docker is exists.")

    # run HomeAssistant
    await docker_hass.run()
