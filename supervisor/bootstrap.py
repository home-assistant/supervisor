"""Bootstrap Supervisor."""
import logging
import os
from pathlib import Path
import signal

from colorlog import ColoredFormatter

from .addons import AddonManager
from .api import RestAPI
from .arch import CpuArch
from .auth import Auth
from .backups.manager import BackupManager
from .bus import Bus
from .const import (
    ATTR_ADDONS_CUSTOM_LIST,
    ATTR_REPOSITORIES,
    ENV_HOMEASSISTANT_REPOSITORY,
    ENV_SUPERVISOR_MACHINE,
    ENV_SUPERVISOR_NAME,
    ENV_SUPERVISOR_SHARE,
    MACHINE_ID,
    SOCKET_DOCKER,
    LogLevel,
    UpdateChannel,
)
from .core import Core
from .coresys import CoreSys
from .dbus.manager import DBusManager
from .discovery import Discovery
from .docker.manager import DockerAPI
from .hardware.manager import HardwareManager
from .homeassistant.module import HomeAssistant
from .host.manager import HostManager
from .ingress import Ingress
from .jobs import JobManager
from .misc.scheduler import Scheduler
from .misc.tasks import Tasks
from .mounts.manager import MountManager
from .os.manager import OSManager
from .plugins.manager import PluginManager
from .resolution.module import ResolutionManager
from .security.module import Security
from .services import ServiceManager
from .store import StoreManager
from .store.validate import ensure_builtin_repositories
from .supervisor import Supervisor
from .updater import Updater
from .utils.sentry import init_sentry

_LOGGER: logging.Logger = logging.getLogger(__name__)


async def initialize_coresys() -> CoreSys:
    """Initialize supervisor coresys/objects."""
    coresys = CoreSys()

    # Initialize core objects
    coresys.docker = DockerAPI(coresys)
    coresys.resolution = ResolutionManager(coresys)
    coresys.jobs = JobManager(coresys)
    coresys.core = Core(coresys)
    coresys.plugins = PluginManager(coresys)
    coresys.arch = CpuArch(coresys)
    coresys.auth = Auth(coresys)
    coresys.updater = Updater(coresys)
    coresys.api = RestAPI(coresys)
    coresys.supervisor = Supervisor(coresys)
    coresys.homeassistant = HomeAssistant(coresys)
    coresys.addons = AddonManager(coresys)
    coresys.backups = BackupManager(coresys)
    coresys.host = HostManager(coresys)
    coresys.hardware = HardwareManager(coresys)
    coresys.ingress = Ingress(coresys)
    coresys.tasks = Tasks(coresys)
    coresys.services = ServiceManager(coresys)
    coresys.store = StoreManager(coresys)
    coresys.discovery = Discovery(coresys)
    coresys.dbus = DBusManager(coresys)
    coresys.os = OSManager(coresys)
    coresys.scheduler = Scheduler(coresys)
    coresys.security = Security(coresys)
    coresys.bus = Bus(coresys)
    coresys.mounts = MountManager(coresys)

    # diagnostics
    if coresys.config.diagnostics:
        init_sentry(coresys)

    # bootstrap config
    initialize_system(coresys)

    # Set Machine/Host ID
    if MACHINE_ID.exists():
        coresys.machine_id = MACHINE_ID.read_text(encoding="utf-8").strip()

    # Check if ENV is in development mode
    if coresys.dev:
        _LOGGER.warning("Environment variable 'SUPERVISOR_DEV' is set")
        coresys.config.logging = LogLevel.DEBUG
        coresys.config.debug = True
        coresys.updater.channel = UpdateChannel.DEV
        coresys.security.content_trust = False
    else:
        coresys.config.modify_log_level()

    # Convert datetime
    logging.Formatter.converter = lambda *args: coresys.now().timetuple()

    # Set machine type
    if os.environ.get(ENV_SUPERVISOR_MACHINE):
        coresys.machine = os.environ[ENV_SUPERVISOR_MACHINE]
    elif os.environ.get(ENV_HOMEASSISTANT_REPOSITORY):
        coresys.machine = os.environ[ENV_HOMEASSISTANT_REPOSITORY][14:-14]
        _LOGGER.warning(
            "Missing SUPERVISOR_MACHINE environment variable. Fallback to deprecated extraction!"
        )
    _LOGGER.info("Seting up coresys for machine: %s", coresys.machine)

    return coresys


def initialize_system(coresys: CoreSys) -> None:
    """Set up the default configuration and create folders."""
    config = coresys.config

    # Home Assistant configuration folder
    if not config.path_homeassistant.is_dir():
        _LOGGER.debug(
            "Creating Home Assistant configuration folder at '%s'",
            config.path_homeassistant,
        )
        config.path_homeassistant.mkdir()

    # Supervisor ssl folder
    if not config.path_ssl.is_dir():
        _LOGGER.debug("Creating Supervisor SSL/TLS folder at '%s'", config.path_ssl)
        config.path_ssl.mkdir()

    # Supervisor addon data folder
    if not config.path_addons_data.is_dir():
        _LOGGER.debug(
            "Creating Supervisor Add-on data folder at '%s'", config.path_addons_data
        )
        config.path_addons_data.mkdir(parents=True)

    if not config.path_addons_local.is_dir():
        _LOGGER.debug(
            "Creating Supervisor Add-on local repository folder at '%s'",
            config.path_addons_local,
        )
        config.path_addons_local.mkdir(parents=True)

    if not config.path_addons_git.is_dir():
        _LOGGER.debug(
            "Creating Supervisor Add-on git repositories folder at '%s'",
            config.path_addons_git,
        )
        config.path_addons_git.mkdir(parents=True)

    # Supervisor tmp folder
    if not config.path_tmp.is_dir():
        _LOGGER.debug("Creating Supervisor temp folder at '%s'", config.path_tmp)
        config.path_tmp.mkdir(parents=True)

    # Supervisor backup folder
    if not config.path_backup.is_dir():
        _LOGGER.debug("Creating Supervisor backup folder at '%s'", config.path_backup)
        config.path_backup.mkdir()

    # Share folder
    if not config.path_share.is_dir():
        _LOGGER.debug("Creating Supervisor share folder at '%s'", config.path_share)
        config.path_share.mkdir()

    # Apparmor folders
    if not config.path_apparmor.is_dir():
        _LOGGER.debug(
            "Creating Supervisor Apparmor Profile folder at '%s'", config.path_apparmor
        )
        config.path_apparmor.mkdir()

    if not config.path_apparmor_cache.is_dir():
        _LOGGER.debug(
            "Creating Supervisor Apparmor Cache folder at '%s'",
            config.path_apparmor_cache,
        )
        config.path_apparmor_cache.mkdir()

    # DNS folder
    if not config.path_dns.is_dir():
        _LOGGER.debug("Creating Supervisor DNS folder at '%s'", config.path_dns)
        config.path_dns.mkdir()

    # Audio folder
    if not config.path_audio.is_dir():
        _LOGGER.debug("Creating Supervisor audio folder at '%s'", config.path_audio)
        config.path_audio.mkdir()

    # Media folder
    if not config.path_media.is_dir():
        _LOGGER.debug("Creating Supervisor media folder at '%s'", config.path_media)
        config.path_media.mkdir()

    # Mounts folders
    if not config.path_mounts.is_dir():
        _LOGGER.debug("Creating Supervisor mounts folder at '%s'", config.path_mounts)
        config.path_mounts.mkdir()

    if not config.path_mounts_credentials.is_dir():
        _LOGGER.debug(
            "Creating Supervisor mounts credentials folder at '%s'",
            config.path_mounts_credentials,
        )
        config.path_mounts_credentials.mkdir(mode=0o600)

    # Emergency folder
    if not config.path_emergency.is_dir():
        _LOGGER.debug(
            "Creating Supervisor emergency folder at '%s'", config.path_emergency
        )
        config.path_emergency.mkdir()


def migrate_system_env(coresys: CoreSys) -> None:
    """Cleanup some stuff after update."""
    config = coresys.config

    # hass.io 0.37 -> 0.38
    old_build = Path(config.path_supervisor, "addons/build")
    if old_build.is_dir():
        try:
            old_build.rmdir()
        except OSError:
            _LOGGER.error("Can't cleanup old Add-on build directory at '%s'", old_build)

    # Supervisor 2022.5 -> 2022.6. Can be removed after 2022.9
    # pylint: disable=protected-access
    if len(coresys.config.addons_repositories) > 0:
        coresys.store._data[ATTR_REPOSITORIES] = ensure_builtin_repositories(
            coresys.config.addons_repositories
        )
        coresys.config._data[ATTR_ADDONS_CUSTOM_LIST] = []
        coresys.store.save_data()
        coresys.config.save_data()


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
            _LOGGER.critical("Can't find '%s' environment variable!", key)

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

    _LOGGER.info("Initializing Supervisor debugger")

    debugpy.listen(("0.0.0.0", 33333))
    if coresys.config.debug_block:
        _LOGGER.info("Wait until debugger is attached")
        debugpy.wait_for_client()
