"""Bootstrap HassIO."""
import logging
import os
import stat

from colorlog import ColoredFormatter

from .const import SOCKET_DOCKER
from .config import CoreConfig

_LOGGER = logging.getLogger(__name__)


def initialize_system_data(websession):
    """Setup default config and create folders."""
    config = CoreConfig(websession)

    # homeassistant config folder
    if not os.path.isdir(config.path_config):
        _LOGGER.info(
            "Create Home-Assistant config folder %s", config.path_config)
        os.mkdir(config.path_config)

    # homeassistant ssl folder
    if not os.path.isdir(config.path_ssl):
        _LOGGER.info("Create Home-Assistant ssl folder %s", config.path_ssl)
        os.mkdir(config.path_ssl)

    # homeassistant addon data folder
    if not os.path.isdir(config.path_addons_data):
        _LOGGER.info("Create Home-Assistant addon data folder %s",
                     config.path_addons_data)
        os.mkdir(config.path_addons_data)

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


def check_environment():
    """Check if all environment are exists."""
    for key in ('SUPERVISOR_SHARE', 'SUPERVISOR_NAME',
                'HOMEASSISTANT_REPOSITORY'):
        try:
            os.environ[key]
        except KeyError:
            _LOGGER.fatal("Can't find %s in env!", key)
            return False

    mode = os.stat(SOCKET_DOCKER)[stat.ST_MODE]
    if not stat.S_ISSOCK(mode):
        _LOGGER.fatal("Can't find docker socket!")
        return False

    return True
