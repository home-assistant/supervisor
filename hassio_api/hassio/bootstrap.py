"""Bootstrap HassIO."""
import asyncio
import json
import logging
import os

from colorlog import ColoredFormatter

from .const import FILE_HASSIO_ADDONS, HOMEASSISTANT_CONFIG, HOMEASSISTANT_SSL
from .version import Version

_LOGGER = logging.getLogger(__name__)


def initialize_system_data():
    """Setup default config and create folders."""
    # homeassistant config folder
    if not os.path.isdir(HOMEASSISTANT_CONFIG):
        _LOGGER.info(
            "Create Home-Assistant config folder %s", HOMEASSISTANT_CONFIG)
        os.mkdir(HOMEASSISTANT_CONFIG)

    # homeassistant ssl folder
    if not os.path.isdir(HOMEASSISTANT_SSL):
        _LOGGER.info(
            "Create Home-Assistant ssl folder %s", HOMEASSISTANT_SSL)
        os.mkdir(HOMEASSISTANT_SSL)

    # installed addons
    if not os.path.isfile(FILE_HASSIO_ADDONS):
        with open(FILE_HASSIO_ADDONS) as addons_file:
            addons_file.write(json.dumps({}))

    # supervisor/homeassistant image/tag versions
    conf_version = Version()

    return conf_version


def initialize_logging():
    """Setup the logging."""
    logging.basicConfig(level=logging.INFO)
    fmt = ("%(asctime)s %(levelname)s (%(threadName)s) "
           "[%(name)s] %(message)s")
    colorfmt = "%(log_color)s{}%(reset)s".format(fmt)
    datefmt = '%y-%m-%d %H:%M:%S'

    # suppress overly verbose logs from libraries that aren't helpful
    logging.getLogger("aiohttp.access").setLevel(logging.WARNING)

    logging.getLogger().handlers[0].setFormatter(ColoredFormatter(
        colorfmt,
        datefmt=datefmt,
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red',
        }
    ))
