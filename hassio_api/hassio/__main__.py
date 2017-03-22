"""Main file for HassIO."""
import asyncio
import logging

import aiohttp
from aiohttp import web
import docker

import .bootstrap
import .tools
from .docker.homeassistant import DockerHomeAssistant
from .const import CONF_HOMEASSISTANT_TAG

_LOGGER = logging.getLogger(__name__)


def main():
    """Start HassIO."""
    bootstrap.initialize_logging()

    # init asyncio & aiohttp client
    loop = asyncio.get_event_loop()
    websession = aiohttp.ClientSession(loop=loop)
    dock = docker.Client(base_url='unix://var/run/docker.sock', version='auto')

    # init system
    conf_version = bootstrap.initialize_system_data()

    # init HomeAssistant Docker
    docker_hass = DockerHomeAssistant(
        loop, dock, conf_version.homeassistant_image,
        conf_version.homeassistant_tag
    )

    # first start of supervisor?
    if conf_version.homeassistant_tag is None:
        _LOGGER.info("First start of supervisor, read version from github.")

        # read homeassistant tag and install it
        current = None
        while True:
            current = await tools.fetch_current_versions(websession)
            if current and CONF_HOMEASSISTANT_TAG in current:
                if docker_hass.install(current[CONF_SUPERVISOR_TAG]):
                    break
            _LOGGER.waring("Can't fetch info from github. Retry in 60")
            await asyncio.sleep(60, loop=loop)

        conf_version.homeassistant_tag = current[CONF_HOMEASSISTANT_TAG]

    # run HomeAssistant
    docker_hass.run()

    await loop.run_forever()


if __name__ == "__main__":
    sys.exit(main())
