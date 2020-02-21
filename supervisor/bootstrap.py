"""Bootstrap Supervisor."""
import logging
import os
from pathlib import Path
import shutil
import signal

from colorlog import ColoredFormatter

from .addons import AddonManager
from .api import RestAPI
from .arch import CpuArch
from .auth import Auth
from .const import SOCKET_DOCKER, UpdateChannels
from .core import supervisor
from .coresys import CoreSys
from .dbus import DBusManager
from .discovery import Discovery
from .dns import CoreDNS
from .hassos import HassOS
from .homeassistant import HomeAssistant
from .host import HostManager
from .ingress import Ingress
from .services import ServiceManager
from .snapshots import SnapshotManager
from .store import StoreManager
from .supervisor import Supervisor
from .tasks import Tasks
from .updater import Updater
from .secrets import SecretsManager
from .utils.dt import fetch_timezone

_LOGGER: logging.Logger = logging.getLogger(__name__)

ENV_SHARE = "SUPERVISOR_SHARE"
ENV_NAME = "SUPERVISOR_NAME"
ENV_REPO = "HOMEASSISTANT_REPOSITORY"

MACHINE_ID = Path("/etc/machine-id")


async def initialize_coresys():
    """Initialize supervisor coresys/objects."""
    coresys = CoreSys()

    # Initialize core objects
    coresys.core = supervisor(coresys)
    coresys.dns = CoreDNS(coresys)
    coresys.arch = CpuArch(coresys)
    coresys.auth = Auth(coresys)
    coresys.updater = Updater(coresys)
    coresys.api = RestAPI(coresys)
    coresys.supervisor = Supervisor(coresys)
    coresys.homeassistant = HomeAssistant(coresys)
    coresys.addons = AddonManager(coresys)
    coresys.snapshots = SnapshotManager(coresys)
    coresys.host = HostManager(coresys)
    coresys.ingress = Ingress(coresys)
    coresys.tasks = Tasks(coresys)
    coresys.services = ServiceManager(coresys)
    coresys.store = StoreManager(coresys)
    coresys.discovery = Discovery(coresys)
    coresys.dbus = DBusManager(coresys)
    coresys.hassos = HassOS(coresys)
    coresys.secrets = SecretsManager(coresys)

    # bootstrap config
    initialize_system_data(coresys)

    # Set Machine/Host ID
    if MACHINE_ID.exists():
        coresys.machine_id = MACHINE_ID.read_text().strip()

    # Init TimeZone
    if coresys.config.timezone == "UTC":
        coresys.config.timezone = await fetch_timezone(coresys.websession)

    return coresys


def initialize_system_data(coresys: CoreSys):
    """Set up the default configuration and create folders."""
    config = coresys.config

    # Home Assistant configuration folder
    if not config.path_homeassistant.is_dir():
        _LOGGER.info(
            "Create Home Assistant configuration folder %s", config.path_homeassistant
        )
        config.path_homeassistant.mkdir()

    # supervisor ssl folder
    if not config.path_ssl.is_dir():
        _LOGGER.info("Create Supervisor SSL/TLS folder %s", config.path_ssl)
        config.path_ssl.mkdir()

    # supervisor addon data folder
    if not config.path_addons_data.is_dir():
        _LOGGER.info("Create Supervisor Add-on data folder %s", config.path_addons_data)
        config.path_addons_data.mkdir(parents=True)

    if not config.path_addons_local.is_dir():
        _LOGGER.info(
            "Create Supervisor Add-on local repository folder %s",
            config.path_addons_local,
        )
        config.path_addons_local.mkdir(parents=True)

    if not config.path_addons_git.is_dir():
        _LOGGER.info(
            "Create Supervisor Add-on git repositories folder %s",
            config.path_addons_git,
        )
        config.path_addons_git.mkdir(parents=True)

    # supervisor tmp folder
    if not config.path_tmp.is_dir():
        _LOGGER.info("Create Supervisor temp folder %s", config.path_tmp)
        config.path_tmp.mkdir(parents=True)

    # supervisor backup folder
    if not config.path_backup.is_dir():
        _LOGGER.info("Create Supervisor backup folder %s", config.path_backup)
        config.path_backup.mkdir()

    # share folder
    if not config.path_share.is_dir():
        _LOGGER.info("Create Supervisor share folder %s", config.path_share)
        config.path_share.mkdir()

    # apparmor folder
    if not config.path_apparmor.is_dir():
        _LOGGER.info("Create Supervisor Apparmor folder %s", config.path_apparmor)
        config.path_apparmor.mkdir()

    # dns folder
    if not config.path_dns.is_dir():
        _LOGGER.info("Create Supervisor DNS folder %s", config.path_dns)
        config.path_dns.mkdir()

    # Update log level
    coresys.config.modify_log_level()

    # Check if ENV is in development mode
    if bool(os.environ.get("SUPERVISOR_DEV", 0)):
        _LOGGER.warning("SUPERVISOR_DEV is set")
        coresys.updater.channel = UpdateChannels.DEV
        coresys.config.logging = "debug"
        coresys.config.debug = True


def migrate_system_env(coresys: CoreSys):
    """Cleanup some stuff after update."""
    config = coresys.config

    # hass.io 0.37 -> 0.38
    old_build = Path(config.path_hassio, "addons/build")
    if old_build.is_dir():
        try:
            old_build.rmdir()
        except OSError:
            _LOGGER.warning("Can't cleanup old Add-on build directory")


def initialize_logging():
    """Setup the logging."""
    logging.basicConfig(level=logging.INFO)
    fmt = "%(asctime)s %(levelname)s (%(threadName)s) [%(name)s] %(message)s"
    colorfmt = f"%(log_color)s{fmt}%(reset)s"
    datefmt = "%y-%m-%d %H:%M:%S"

    # suppress overly verbose logs from libraries that aren't helpful
    logging.getLogger("aiohttp.access").setLevel(logging.WARNING)

    logging.getLogger().handlers[0].setFormatter(
        ColoredFormatter(
            colorfmt,
            datefmt=datefmt,
            reset=True,
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red",
            },
        )
    )


def check_environment():
    """Check if all environment are exists."""
    # check environment variables
    for key in (ENV_SHARE, ENV_NAME, ENV_REPO):
        try:
            os.environ[key]
        except KeyError:
            _LOGGER.fatal("Can't find %s in env!", key)
            return False

    # check docker socket
    if not SOCKET_DOCKER.is_socket():
        _LOGGER.fatal("Can't find Docker socket!")
        return False

    # check socat exec
    if not shutil.which("socat"):
        _LOGGER.fatal("Can't find socat!")
        return False

    # check socat exec
    if not shutil.which("gdbus"):
        _LOGGER.fatal("Can't find gdbus!")
        return False

    return True


def reg_signal(loop):
    """Register SIGTERM and SIGKILL to stop system."""
    try:
        loop.add_signal_handler(signal.SIGTERM, lambda: loop.call_soon(loop.stop))
    except (ValueError, RuntimeError):
        _LOGGER.warning("Could not bind to SIGTERM")

    try:
        loop.add_signal_handler(signal.SIGHUP, lambda: loop.call_soon(loop.stop))
    except (ValueError, RuntimeError):
        _LOGGER.warning("Could not bind to SIGHUP")

    try:
        loop.add_signal_handler(signal.SIGINT, lambda: loop.call_soon(loop.stop))
    except (ValueError, RuntimeError):
        _LOGGER.warning("Could not bind to SIGINT")


def supervisor_debugger(coresys: CoreSys) -> None:
    """Setup debugger if needed."""
    if not coresys.config.debug:
        return
    # pylint: disable=import-outside-toplevel
    import ptvsd

    _LOGGER.info("Initialize Supervisor debugger")

    ptvsd.enable_attach(address=("0.0.0.0", 33333), redirect_output=True)
    if coresys.config.debug_block:
        _LOGGER.info("Wait until debugger is attached")
        ptvsd.wait_for_attach()
