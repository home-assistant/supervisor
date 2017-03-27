"""Main file for HassIO."""
import asyncio
import logging

import aiohttp
import docker

import .bootstrap
import .tools
from .const import CONF_HOMEASSISTANT_TAG
from .docker.homeassistant import DockerHomeAssistant

_LOGGER = logging.getLogger(__name__)


async def run_hassio(loop):
    """Start HassIO."""
    websession = aiohttp.ClientSession(loop=loop)
    dock = docker.Client(base_url='unix://var/run/docker.sock', version='auto')

    # init system
    config = bootstrap.initialize_system_data()

    # init HomeAssistant Docker
    docker_hass = DockerHomeAssistant(
        config, loop, dock, config.homeassistant_image,
        config.homeassistant_tag
    )

    # first start of supervisor?
    if config.homeassistant_tag is None:
        _LOGGER.info("First start of supervisor, read version from github.")

        # read homeassistant tag and install it
        current = None
        while True:
            current = await tools.fetch_current_versions(websession)
            if current and CONF_HOMEASSISTANT_TAG in current:
                if await docker_hass.install(current[CONF_HOMEASSISTANT_TAG]):
                    break
            _LOGGER.warning("Can't fetch info from github. Retry in 60")
            await asyncio.sleep(60, loop=loop)

        config.homeassistant_tag = current[CONF_HOMEASSISTANT_TAG]

    # run HomeAssistant
    await docker_hass.run()
