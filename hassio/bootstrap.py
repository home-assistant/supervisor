"""Bootstrap HassIO."""
import logging
import os
import signal
import shutil
from pathlib import Path

from colorlog import ColoredFormatter

from .addons import AddonManager
from .api import RestAPI
from .const import SOCKET_DOCKER
from .coresys import CoreSys
from .supervisor import Supervisor
from .homeassistant import HomeAssistant
from .snapshots import SnapshotManager
from .tasks import Tasks
from .updater import Updater
from .services import ServiceManager

_LOGGER = logging.getLogger(__name__)


def initialize_coresys(loop):
    """Initialize HassIO coresys/objects."""
    coresys = CoreSys(loop)

    # Initialize core objects
    coresys.updater = Updater(coresys)
    coresys.api = RestAPI(coresys)
    coresys.supervisor = Supervisor(coresys)
    coresys.homeassistant = HomeAssistant(coresys)
    coresys.addons = AddonManager(coresys)
    coresys.snapshots = SnapshotManager(coresys)
    coresys.tasks = Tasks(coresys)
    coresys.services = ServiceManager(coresys)

    # bootstrap config
    initialize_system_data(coresys)

    return coresys


def initialize_system_data(coresys):
    """Setup default config and create folders."""
    config = coresys.config

    # homeassistant config folder
    if not config.path_config.is_dir():
        _LOGGER.info(
            "Create Home-Assistant config folder %s", config.path_config)
        config.path_config.mkdir()

    # hassio ssl folder
    if not config.path_ssl.is_dir():
        _LOGGER.info("Create hassio ssl folder %s", config.path_ssl)
        config.path_ssl.mkdir()

    # hassio addon data folder
    if not config.path_addons_data.is_dir():
        _LOGGER.info(
            "Create hassio addon data folder %s", config.path_addons_data)
        config.path_addons_data.mkdir(parents=True)

    if not config.path_addons_local.is_dir():
        _LOGGER.info("Create hassio addon local repository folder %s",
                     config.path_addons_local)
        config.path_addons_local.mkdir(parents=True)

    if not config.path_addons_git.is_dir():
        _LOGGER.info("Create hassio addon git repositories folder %s",
                     config.path_addons_git)
        config.path_addons_git.mkdir(parents=True)

    # hassio tmp folder
    if not config.path_tmp.is_dir():
        _LOGGER.info("Create hassio temp folder %s", config.path_tmp)
        config.path_tmp.mkdir(parents=True)

    # hassio backup folder
    if not config.path_backup.is_dir():
        _LOGGER.info("Create hassio backup folder %s", config.path_backup)
        config.path_backup.mkdir()

    # share folder
    if not config.path_share.is_dir():
        _LOGGER.info("Create hassio share folder %s", config.path_share)
        config.path_share.mkdir()

    return config


def migrate_system_env(coresys):
    """Cleanup some stuff after update."""
    config = coresys.config

    # hass.io 0.37 -> 0.38
    old_build = Path(config.path_hassio, "addons/build")
    if old_build.is_dir():
        try:
            old_build.rmdir()
        except OSError:
            _LOGGER.warning("Can't cleanup old addons build dir.")


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
    # check environment variables
    for key in ('SUPERVISOR_SHARE', 'SUPERVISOR_NAME',
                'HOMEASSISTANT_REPOSITORY'):
        try:
            os.environ[key]
        except KeyError:
            _LOGGER.fatal("Can't find %s in env!", key)
            return False

    # check docker socket
    if not SOCKET_DOCKER.is_socket():
        _LOGGER.fatal("Can't find docker socket!")
        return False

    # check socat exec
    if not shutil.which('socat'):
        _LOGGER.fatal("Can0t find socat program!")
        return False

    return True


def reg_signal(loop):
    """Register SIGTERM, SIGKILL to stop system."""
    try:
        loop.add_signal_handler(
            signal.SIGTERM, lambda: loop.call_soon(loop.stop))
    except (ValueError, RuntimeError):
        _LOGGER.warning("Could not bind to SIGTERM")

    try:
        loop.add_signal_handler(
            signal.SIGHUP, lambda: loop.call_soon(loop.stop))
    except (ValueError, RuntimeError):
        _LOGGER.warning("Could not bind to SIGHUP")

    try:
        loop.add_signal_handler(
            signal.SIGINT, lambda: loop.call_soon(loop.stop))
    except (ValueError, RuntimeError):
        _LOGGER.warning("Could not bind to SIGINT")
