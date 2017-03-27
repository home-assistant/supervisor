"""Bootstrap HassIO."""
import json
import logging
import os

from colorlog import ColoredFormatter

from .const import FILE_HASSIO_ADDONS
from .config import CoreConfig

_LOGGER = logging.getLogger(__name__)


def initialize_system_data():
    """Setup default config and create folders."""
    config = CoreConfig()

    # homeassistant config folder
    if not os.path.isdir(config.path_config):
        _LOGGER.info(
            "Create Home-Assistant config folder %s", config.path_config)
        os.mkdir(config.path_config)

    # homeassistant ssl folder
    if not os.path.isdir(config.path_ssl):
        _LOGGER.info("Create Home-Assistant ssl folder %s", config.path_ssl)
        os.mkdir(config.path_ssl)

    # installed addons
    if not os.path.isfile(FILE_HASSIO_ADDONS):
        with open(FILE_HASSIO_ADDONS) as addons_file:
            addons_file.write(json.dumps({}))

    return config


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
