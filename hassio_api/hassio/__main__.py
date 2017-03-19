"""Main file for HassIO."""
import asyncio
import logging

import aiohttp
from aiohttp import web
import docker

import .bootstrap
import .tools
from .docker.homeassistant import DockerHomeAssistant

_LOGGER = logging.getLogger(__name__)


def main():
    """Start HassIO."""
    bootstrap.initialize_logging()

    # init asyncio & aiohttp client
    loop = asyncio.get_event_loop()
    websession = aiohttp.ClientSession(loop=loop)
    dock = docker.from_env()

    # init system
    versions = bootstrap.initialize_system_data()

    # init HomeAssistant Docker
    docker_hass = DockerHomeAssistant(
        loop, dock, versions[CONF_HOMEASSISTANT_IMAGE],
        versions[CONF_HOMEASSISTANT_TAG])

    # first start of supervisor?
    if versions['CONF_HOMEASSISTANT_TAG'] is None:
        _LOGGER.info("First start of supervisor, read version from github.")

        # read homeassistant tag and install it
        current = None
        while True:
            current = await tools.fetch_current_versions(websession)
            if current and 'homeassistant_tag' in current:
                if docker_hass.install(current['homeassistant_tag']):
                    break
            _LOGGER.waring("Can't fetch info from github. Retry in 60")
            await asyncio.sleep(60, loop=loop)


if __name__ == "__main__":
    sys.exit(main())
