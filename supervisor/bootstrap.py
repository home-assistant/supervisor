"""Bootstrap Supervisor."""
import logging
import os
from pathlib import Path
import shutil
import signal

from colorlog import ColoredFormatter
import sentry_sdk
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from .addons import AddonManager
from .api import RestAPI
from .arch import CpuArch
from .auth import Auth
from .const import (
    ENV_HOMEASSISTANT_REPOSITORY,
    ENV_SUPERVISOR_DEV,
    ENV_SUPERVISOR_MACHINE,
    ENV_SUPERVISOR_NAME,
    ENV_SUPERVISOR_SHARE,
    MACHINE_ID,
    SOCKET_DOCKER,
    SUPERVISOR_VERSION,
    LogLevel,
    UpdateChannel,
)
from .core import Core
from .coresys import CoreSys
from .dbus import DBusManager
from .discovery import Discovery
from .hassos import HassOS
from .homeassistant import HomeAssistant
from .host import HostManager
from .ingress import Ingress
from .misc.filter import filter_data
from .misc.hwmon import HwMonitor
from .misc.scheduler import Scheduler
from .misc.tasks import Tasks
from .plugins import PluginManager
from .services import ServiceManager
from .snapshots import SnapshotManager
from .store import StoreManager
from .supervisor import Supervisor
from .updater import Updater
from .utils.dt import fetch_timezone

_LOGGER: logging.Logger = logging.getLogger(__name__)


async def initialize_coresys() -> CoreSys:
    """Initialize supervisor coresys/objects."""
    coresys = CoreSys()

    # Initialize core objects
    coresys.core = Core(coresys)
    coresys.plugins = PluginManager(coresys)
    coresys.arch = CpuArch(coresys)
    coresys.auth = Auth(coresys)
    coresys.updater = Updater(coresys)
    coresys.api = RestAPI(coresys)
    coresys.supervisor = Supervisor(coresys)
    coresys.homeassistant = HomeAssistant(coresys)
    coresys.addons = AddonManager(coresys)
    coresys.snapshots = SnapshotManager(coresys)
    coresys.host = HostManager(coresys)
    coresys.hwmonitor = HwMonitor(coresys)
    coresys.ingress = Ingress(coresys)
    coresys.tasks = Tasks(coresys)
    coresys.services = ServiceManager(coresys)
    coresys.store = StoreManager(coresys)
    coresys.discovery = Discovery(coresys)
    coresys.dbus = DBusManager(coresys)
    coresys.hassos = HassOS(coresys)
    coresys.scheduler = Scheduler(coresys)

    # diagnostics
    setup_diagnostics(coresys)

    # bootstrap config
    initialize_system_data(coresys)

    # Set Machine/Host ID
    if MACHINE_ID.exists():
        coresys.machine_id = MACHINE_ID.read_text().strip()

    # Init TimeZone
    if coresys.config.timezone == "UTC":
        coresys.config.timezone = await fetch_timezone(coresys.websession)

    # Set machine type
    if os.environ.get(ENV_SUPERVISOR_MACHINE):
        coresys.machine = os.environ[ENV_SUPERVISOR_MACHINE]
    elif os.environ.get(ENV_HOMEASSISTANT_REPOSITORY):
        coresys.machine = os.environ[ENV_HOMEASSISTANT_REPOSITORY][14:-14]
    _LOGGER.info("Setup coresys for machine: %s", coresys.machine)

    return coresys


def initialize_system_data(coresys: CoreSys) -> None:
    """Set up the default configuration and create folders."""
    config = coresys.config

    # Home Assistant configuration folder
    if not config.path_homeassistant.is_dir():
        _LOGGER.info(
            "Create Home Assistant configuration folder %s", config.path_homeassistant
        )
        config.path_homeassistant.mkdir()

    # Supervisor ssl folder
    if not config.path_ssl.is_dir():
        _LOGGER.info("Create Supervisor SSL/TLS folder %s", config.path_ssl)
        config.path_ssl.mkdir()

    # Supervisor addon data folder
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

    # Supervisor tmp folder
    if not config.path_tmp.is_dir():
        _LOGGER.info("Create Supervisor temp folder %s", config.path_tmp)
        config.path_tmp.mkdir(parents=True)

    # Supervisor backup folder
    if not config.path_backup.is_dir():
        _LOGGER.info("Create Supervisor backup folder %s", config.path_backup)
        config.path_backup.mkdir()

    # Share folder
    if not config.path_share.is_dir():
        _LOGGER.info("Create Supervisor share folder %s", config.path_share)
        config.path_share.mkdir()

    # Apparmor folder
    if not config.path_apparmor.is_dir():
        _LOGGER.info("Create Supervisor Apparmor folder %s", config.path_apparmor)
        config.path_apparmor.mkdir()

    # DNS folder
    if not config.path_dns.is_dir():
        _LOGGER.info("Create Supervisor DNS folder %s", config.path_dns)
        config.path_dns.mkdir()

    # Audio folder
    if not config.path_audio.is_dir():
        _LOGGER.info("Create Supervisor audio folder %s", config.path_audio)
        config.path_audio.mkdir()

    # Media folder
    if not config.path_media.is_dir():
        _LOGGER.info("Create Supervisor media folder %s", config.path_media)
        config.path_media.mkdir()

    # Update log level
    coresys.config.modify_log_level()

    # Check if ENV is in development mode
    if bool(os.environ.get(ENV_SUPERVISOR_DEV, 0)):
        _LOGGER.warning("SUPERVISOR_DEV is set")
        coresys.updater.channel = UpdateChannel.DEV
        coresys.config.logging = LogLevel.DEBUG
        coresys.config.debug = True


def migrate_system_env(coresys: CoreSys) -> None:
    """Cleanup some stuff after update."""
    config = coresys.config

    # hass.io 0.37 -> 0.38
    old_build = Path(config.path_supervisor, "addons/build")
    if old_build.is_dir():
        try:
            old_build.rmdir()
        except OSError:
            _LOGGER.warning("Can't cleanup old Add-on build directory")


def initialize_logging() -> None:
    """Initialize the logging."""
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


def check_environment() -> None:
    """Check if all environment are exists."""
    # check environment variables
    for key in (ENV_SUPERVISOR_SHARE, ENV_SUPERVISOR_NAME):
        try:
            os.environ[key]
        except KeyError:
            _LOGGER.critical("Can't find %s in env!", key)

    # Check Machine info
    if not os.environ.get(ENV_HOMEASSISTANT_REPOSITORY) and not os.environ.get(
        ENV_SUPERVISOR_MACHINE
    ):
        _LOGGER.critical("Can't find any kind of machine/homeassistant details!")
    elif not os.environ.get(ENV_SUPERVISOR_MACHINE):
        _LOGGER.info("Use the old homeassistant repository for machine extraction")

    # check docker socket
    if not SOCKET_DOCKER.is_socket():
        _LOGGER.critical("Can't find Docker socket!")

    # check socat exec
    if not shutil.which("gdbus"):
        _LOGGER.critical("Can't find gdbus!")


def reg_signal(loop, coresys: CoreSys) -> None:
    """Register SIGTERM and SIGKILL to stop system."""
    try:
        loop.add_signal_handler(
            signal.SIGTERM, lambda: loop.create_task(coresys.core.stop())
        )
    except (ValueError, RuntimeError):
        _LOGGER.warning("Could not bind to SIGTERM")

    try:
        loop.add_signal_handler(
            signal.SIGHUP, lambda: loop.create_task(coresys.core.stop())
        )
    except (ValueError, RuntimeError):
        _LOGGER.warning("Could not bind to SIGHUP")

    try:
        loop.add_signal_handler(
            signal.SIGINT, lambda: loop.create_task(coresys.core.stop())
        )
    except (ValueError, RuntimeError):
        _LOGGER.warning("Could not bind to SIGINT")


def supervisor_debugger(coresys: CoreSys) -> None:
    """Start debugger if needed."""
    if not coresys.config.debug:
        return
    # pylint: disable=import-outside-toplevel
    import debugpy

    _LOGGER.info("Initialize Supervisor debugger")

    debugpy.listen(("0.0.0.0", 33333))
    if coresys.config.debug_block:
        _LOGGER.info("Wait until debugger is attached")
        debugpy.wait_for_client()


def setup_diagnostics(coresys: CoreSys) -> None:
    """Sentry diagnostic backend."""
    sentry_logging = LoggingIntegration(
        level=logging.WARNING, event_level=logging.CRITICAL
    )

    _LOGGER.info("Initialize Supervisor Sentry")
    sentry_sdk.init(
        dsn="https://9c6ea70f49234442b4746e447b24747e@o427061.ingest.sentry.io/5370612",
        before_send=lambda event, hint: filter_data(coresys, event, hint),
        max_breadcrumbs=30,
        integrations=[AioHttpIntegration(), sentry_logging],
        release=SUPERVISOR_VERSION,
    )
