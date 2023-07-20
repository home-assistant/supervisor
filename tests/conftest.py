"""Common test functions."""
from functools import partial
from inspect import unwrap
import os
from pathlib import Path
import subprocess
from unittest.mock import AsyncMock, MagicMock, Mock, PropertyMock, patch
from uuid import uuid4

from aiohttp import web
from aiohttp.test_utils import TestClient
from awesomeversion import AwesomeVersion
from dbus_fast import BusType
from dbus_fast.aio.message_bus import MessageBus
import pytest
from securetar import SecureTarFile

from supervisor import config as su_config
from supervisor.addons.addon import Addon
from supervisor.addons.validate import SCHEMA_ADDON_SYSTEM
from supervisor.api import RestAPI
from supervisor.backups.backup import Backup
from supervisor.backups.const import BackupType
from supervisor.backups.validate import ALL_FOLDERS
from supervisor.bootstrap import initialize_coresys
from supervisor.const import (
    ATTR_ADDONS,
    ATTR_ADDONS_CUSTOM_LIST,
    ATTR_DATE,
    ATTR_FOLDERS,
    ATTR_HOMEASSISTANT,
    ATTR_NAME,
    ATTR_REPOSITORIES,
    ATTR_SIZE,
    ATTR_SLUG,
    ATTR_TYPE,
    ATTR_VERSION,
    REQUEST_FROM,
)
from supervisor.coresys import CoreSys
from supervisor.dbus.network import NetworkManager
from supervisor.docker.manager import DockerAPI
from supervisor.docker.monitor import DockerMonitor
from supervisor.host.logs import LogsControl
from supervisor.os.manager import OSManager
from supervisor.store.addon import AddonStore
from supervisor.store.repository import Repository
from supervisor.utils.dt import utcnow

from .common import (
    load_binary_fixture,
    load_fixture,
    load_json_fixture,
    mock_dbus_services,
)
from .const import TEST_ADDON_SLUG
from .dbus_service_mocks.base import DBusServiceMock
from .dbus_service_mocks.network_connection_settings import (
    ConnectionSettings as ConnectionSettingsService,
)
from .dbus_service_mocks.network_manager import NetworkManager as NetworkManagerService

# pylint: disable=redefined-outer-name, protected-access


@pytest.fixture
async def path_extern() -> None:
    """Set external path env for tests."""
    os.environ["SUPERVISOR_SHARE"] = "/mnt/data/supervisor"
    yield


@pytest.fixture
async def docker() -> DockerAPI:
    """Mock DockerAPI."""
    images = [MagicMock(tags=["ghcr.io/home-assistant/amd64-hassio-supervisor:latest"])]

    with patch(
        "supervisor.docker.manager.DockerClient", return_value=MagicMock()
    ), patch(
        "supervisor.docker.manager.DockerAPI.images", return_value=MagicMock()
    ), patch(
        "supervisor.docker.manager.DockerAPI.containers", return_value=MagicMock()
    ), patch(
        "supervisor.docker.manager.DockerAPI.api", return_value=MagicMock()
    ), patch(
        "supervisor.docker.manager.DockerAPI.images.list", return_value=images
    ), patch(
        "supervisor.docker.manager.DockerAPI.info",
        return_value=MagicMock(),
    ), patch(
        "supervisor.docker.manager.DockerConfig",
        return_value=MagicMock(),
    ), patch(
        "supervisor.docker.manager.DockerAPI.unload"
    ):
        docker_obj = DockerAPI(MagicMock())
        with patch("supervisor.docker.monitor.DockerMonitor.load"):
            await docker_obj.load()

        docker_obj.info.logging = "journald"
        docker_obj.info.storage = "overlay2"
        docker_obj.info.version = "1.0.0"

        docker_obj.config.registries = {}

        yield docker_obj


@pytest.fixture(scope="session")
def dbus_session() -> None:
    """Start a dbus session."""
    dbus_launch = subprocess.run(["dbus-launch"], stdout=subprocess.PIPE, check=False)
    envs = dbus_launch.stdout.decode(encoding="utf-8").rstrip()

    for env in envs.split("\n"):
        name, value = env.split("=", 1)
        os.environ[name] = value


@pytest.fixture
async def dbus_session_bus(dbus_session) -> MessageBus:
    """Return message bus connected to session dbus."""
    bus = await MessageBus(bus_type=BusType.SESSION).connect()
    yield bus
    bus.disconnect()


@pytest.fixture
async def dbus_is_connected():
    """Mock DBusInterface.is_connected for tests."""
    with patch(
        "supervisor.dbus.interface.DBusInterface.is_connected",
        return_value=True,
    ) as is_connected:
        yield is_connected


@pytest.fixture(name="network_manager_services")
async def fixture_network_manager_services(
    dbus_session_bus: MessageBus,
) -> dict[str, DBusServiceMock | dict[str, DBusServiceMock]]:
    """Mock all services network manager connects to."""
    yield await mock_dbus_services(
        {
            "network_access_point": [
                "/org/freedesktop/NetworkManager/AccessPoint/43099",
                "/org/freedesktop/NetworkManager/AccessPoint/43100",
            ],
            "network_active_connection": None,
            "network_connection_settings": None,
            "network_device_wireless": None,
            "network_device": [
                "/org/freedesktop/NetworkManager/Devices/1",
                "/org/freedesktop/NetworkManager/Devices/3",
            ],
            "network_dns_manager": None,
            "network_ip4config": None,
            "network_ip6config": None,
            "network_manager": None,
            "network_settings": None,
        },
        dbus_session_bus,
    )


@pytest.fixture
async def network_manager(
    network_manager_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
    dbus_session_bus: MessageBus,
) -> NetworkManager:
    """Mock Network Manager."""
    nm_obj = NetworkManager()
    await nm_obj.connect(dbus_session_bus)
    yield nm_obj


@pytest.fixture
async def network_manager_service(
    network_manager_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]]
) -> NetworkManagerService:
    """Return Network Manager service mock."""
    yield network_manager_services["network_manager"]


@pytest.fixture(name="connection_settings_service")
async def fixture_connection_settings_service(
    network_manager_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]]
) -> ConnectionSettingsService:
    """Return mock connection settings service."""
    yield network_manager_services["network_connection_settings"]


@pytest.fixture(name="udisks2_services")
async def fixture_udisks2_services(
    dbus_session_bus: MessageBus,
) -> dict[str, DBusServiceMock | dict[str, DBusServiceMock]]:
    """Mock all services UDisks2 connects to."""
    yield await mock_dbus_services(
        {
            "udisks2_block": [
                "/org/freedesktop/UDisks2/block_devices/loop0",
                "/org/freedesktop/UDisks2/block_devices/mmcblk1",
                "/org/freedesktop/UDisks2/block_devices/mmcblk1p1",
                "/org/freedesktop/UDisks2/block_devices/mmcblk1p2",
                "/org/freedesktop/UDisks2/block_devices/mmcblk1p3",
                "/org/freedesktop/UDisks2/block_devices/sda",
                "/org/freedesktop/UDisks2/block_devices/sda1",
                "/org/freedesktop/UDisks2/block_devices/sdb",
                "/org/freedesktop/UDisks2/block_devices/sdb1",
                "/org/freedesktop/UDisks2/block_devices/zram1",
            ],
            "udisks2_drive": [
                "/org/freedesktop/UDisks2/drives/BJTD4R_0x97cde291",
                "/org/freedesktop/UDisks2/drives/Generic_Flash_Disk_61BCDDB6",
                "/org/freedesktop/UDisks2/drives/SSK_SSK_Storage_DF56419883D56",
            ],
            "udisks2_filesystem": [
                "/org/freedesktop/UDisks2/block_devices/mmcblk1p1",
                "/org/freedesktop/UDisks2/block_devices/mmcblk1p3",
                "/org/freedesktop/UDisks2/block_devices/sda1",
                "/org/freedesktop/UDisks2/block_devices/sdb1",
                "/org/freedesktop/UDisks2/block_devices/zram1",
            ],
            "udisks2_loop": None,
            "udisks2_manager": None,
            "udisks2_partition_table": [
                "/org/freedesktop/UDisks2/block_devices/mmcblk1",
                "/org/freedesktop/UDisks2/block_devices/sda",
                "/org/freedesktop/UDisks2/block_devices/sdb",
            ],
            "udisks2_partition": [
                "/org/freedesktop/UDisks2/block_devices/mmcblk1p1",
                "/org/freedesktop/UDisks2/block_devices/mmcblk1p2",
                "/org/freedesktop/UDisks2/block_devices/mmcblk1p3",
                "/org/freedesktop/UDisks2/block_devices/sda1",
                "/org/freedesktop/UDisks2/block_devices/sdb1",
            ],
        },
        dbus_session_bus,
    )


@pytest.fixture(name="os_agent_services")
async def fixture_os_agent_services(
    dbus_session_bus: MessageBus,
) -> dict[str, DBusServiceMock]:
    """Mock all services os agent connects to."""
    yield await mock_dbus_services(
        {
            "os_agent": None,
            "agent_apparmor": None,
            "agent_cgroup": None,
            "agent_datadisk": None,
            "agent_system": None,
            "agent_boards": None,
            "agent_boards_yellow": None,
        },
        dbus_session_bus,
    )


@pytest.fixture(name="all_dbus_services")
async def fixture_all_dbus_services(
    dbus_session_bus: MessageBus,
    network_manager_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
    udisks2_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
    os_agent_services: dict[str, DBusServiceMock],
) -> dict[str, DBusServiceMock | dict[str, DBusServiceMock]]:
    """Mock all dbus services supervisor uses."""
    yield (
        await mock_dbus_services(
            {
                "hostname": None,
                "logind": None,
                "rauc": None,
                "resolved": None,
                "systemd": None,
                "systemd_unit": None,
                "timedate": None,
            },
            dbus_session_bus,
        )
    ) | network_manager_services | udisks2_services | os_agent_services


@pytest.fixture
async def coresys(
    event_loop, docker, dbus_session_bus, all_dbus_services, aiohttp_client, run_dir
) -> CoreSys:
    """Create a CoreSys Mock."""
    with patch("supervisor.bootstrap.initialize_system"), patch(
        "supervisor.utils.sentry.sentry_sdk.init"
    ):
        coresys_obj = await initialize_coresys()

    # Mock save json
    coresys_obj._ingress.save_data = MagicMock()
    coresys_obj._auth.save_data = MagicMock()
    coresys_obj._updater.save_data = MagicMock()
    coresys_obj._config.save_data = MagicMock()
    coresys_obj._jobs.save_data = MagicMock()
    coresys_obj._resolution.save_data = MagicMock()
    coresys_obj._addons.data.save_data = MagicMock()
    coresys_obj._store.save_data = MagicMock()
    coresys_obj._mounts.save_data = MagicMock()

    # Mock test client
    coresys_obj.arch._default_arch = "amd64"
    coresys_obj._machine = "qemux86-64"
    coresys_obj._machine_id = uuid4()

    # Mock host communication
    with patch("supervisor.dbus.manager.MessageBus") as message_bus, patch(
        "supervisor.dbus.manager.SOCKET_DBUS"
    ):
        message_bus.return_value.connect = AsyncMock(return_value=dbus_session_bus)
        await coresys_obj._dbus.load()

    # Mock docker
    coresys_obj._docker = docker
    coresys_obj.docker._monitor = DockerMonitor(coresys_obj)

    # Set internet state
    coresys_obj.supervisor._connectivity = True
    coresys_obj.host.network._connectivity = True

    # Fix Paths
    su_config.ADDONS_CORE = Path(
        Path(__file__).parent.joinpath("fixtures"), "addons/core"
    )
    su_config.ADDONS_LOCAL = Path(
        Path(__file__).parent.joinpath("fixtures"), "addons/local"
    )
    su_config.ADDONS_GIT = Path(
        Path(__file__).parent.joinpath("fixtures"), "addons/git"
    )
    su_config.APPARMOR_DATA = Path(
        Path(__file__).parent.joinpath("fixtures"), "apparmor"
    )

    # WebSocket
    coresys_obj.homeassistant.api.check_api_state = AsyncMock(return_value=True)
    coresys_obj.homeassistant._websocket._client = AsyncMock(
        ha_version=AwesomeVersion("2021.2.4")
    )

    # Remove rate limiting decorator from fetch_data
    coresys_obj.updater.fetch_data = partial(
        unwrap(coresys_obj.updater.fetch_data), coresys_obj.updater
    )

    # Don't remove files/folders related to addons and stores
    with patch("supervisor.store.git.GitRepo._remove"):
        yield coresys_obj

    await coresys_obj.dbus.unload()
    await coresys_obj.websession.close()


@pytest.fixture
async def tmp_supervisor_data(coresys: CoreSys, tmp_path: Path) -> Path:
    """Patch supervisor data to be tmp_path."""
    with patch.object(
        su_config.CoreConfig, "path_supervisor", new=PropertyMock(return_value=tmp_path)
    ):
        coresys.config.path_emergency.mkdir()
        coresys.config.path_media.mkdir()
        coresys.config.path_mounts.mkdir()
        coresys.config.path_mounts_credentials.mkdir()
        coresys.config.path_backup.mkdir()
        coresys.config.path_tmp.mkdir()
        coresys.config.path_homeassistant.mkdir()
        coresys.config.path_audio.mkdir()
        coresys.config.path_dns.mkdir()
        coresys.config.path_share.mkdir()
        coresys.config.path_addons_data.mkdir(parents=True)
        yield tmp_path


@pytest.fixture
async def journald_gateway() -> MagicMock:
    """Mock logs control."""
    with patch("supervisor.host.logs.Path.is_socket", return_value=True), patch(
        "supervisor.host.logs.ClientSession.get"
    ) as get:
        get.return_value.__aenter__.return_value.text = AsyncMock(
            return_value=load_fixture("logs_host.txt")
        )
        yield get


@pytest.fixture
def sys_machine():
    """Mock sys_machine."""
    with patch("supervisor.coresys.CoreSys.machine", new_callable=PropertyMock) as mock:
        yield mock


@pytest.fixture
def sys_supervisor():
    """Mock sys_supervisor."""
    with patch(
        "supervisor.coresys.CoreSys.supervisor", new_callable=PropertyMock
    ) as mock:
        mock.return_value = MagicMock()
        yield MagicMock


@pytest.fixture
async def api_client(
    aiohttp_client, coresys: CoreSys, request: pytest.FixtureRequest
) -> TestClient:
    """Fixture for RestAPI client."""

    request_from: str | None = getattr(request, "param", None)

    @web.middleware
    async def _security_middleware(request: web.Request, handler: web.RequestHandler):
        """Make request are from Core or specified add-on."""
        if request_from:
            request[REQUEST_FROM] = coresys.addons.get(request_from, local_only=True)
        else:
            request[REQUEST_FROM] = coresys.homeassistant

        return await handler(request)

    api = RestAPI(coresys)
    api.webapp = web.Application(middlewares=[_security_middleware])
    api.start = AsyncMock()
    with patch("supervisor.docker.supervisor.os") as os:
        os.environ = {"SUPERVISOR_NAME": "hassio_supervisor"}
        await api.load()
    yield await aiohttp_client(api.webapp)


@pytest.fixture
def store_manager(coresys: CoreSys):
    """Fixture for the store manager."""
    sm_obj = coresys.store
    with patch("supervisor.store.data.StoreData.update", return_value=MagicMock()):
        yield sm_obj


@pytest.fixture
def run_dir(tmp_path):
    """Fixture to inject hassio env."""
    with patch("supervisor.core.RUN_SUPERVISOR_STATE") as mock_run:
        tmp_state = Path(tmp_path, "supervisor")
        mock_run.write_text = tmp_state.write_text
        yield tmp_state


@pytest.fixture
def store_addon(coresys: CoreSys, tmp_path, repository):
    """Store add-on fixture."""
    addon_obj = AddonStore(coresys, "test_store_addon")

    coresys.addons.store[addon_obj.slug] = addon_obj
    coresys.store.data.addons[addon_obj.slug] = SCHEMA_ADDON_SYSTEM(
        load_json_fixture("add-on.json")
    )
    yield addon_obj


@pytest.fixture
async def repository(coresys: CoreSys):
    """Repository fixture."""
    coresys.store._data[ATTR_REPOSITORIES].remove(
        "https://github.com/hassio-addons/repository"
    )
    coresys.store._data[ATTR_REPOSITORIES].remove(
        "https://github.com/esphome/home-assistant-addon"
    )
    coresys.config._data[ATTR_ADDONS_CUSTOM_LIST] = []

    with patch(
        "supervisor.store.validate.BUILTIN_REPOSITORIES", {"local", "core"}
    ), patch("supervisor.store.git.GitRepo.load", return_value=None):
        await coresys.store.load()

        repository_obj = Repository(
            coresys, "https://github.com/awesome-developer/awesome-repo"
        )

        coresys.store.repositories[repository_obj.slug] = repository_obj
        coresys.store._data[ATTR_REPOSITORIES].append(
            "https://github.com/awesome-developer/awesome-repo"
        )

        yield repository_obj


@pytest.fixture
def install_addon_ssh(coresys: CoreSys, repository):
    """Install local_ssh add-on."""
    store = coresys.addons.store[TEST_ADDON_SLUG]
    coresys.addons.data.install(store)
    coresys.addons.data._data = coresys.addons.data._schema(coresys.addons.data._data)

    addon = Addon(coresys, store.slug)
    coresys.addons.local[addon.slug] = addon
    yield addon


@pytest.fixture
async def mock_full_backup(coresys: CoreSys, tmp_path) -> Backup:
    """Mock a full backup."""
    mock_backup = Backup(coresys, Path(tmp_path, "test_backup"))
    mock_backup.new("test", "Test", utcnow().isoformat(), BackupType.FULL)
    mock_backup.repositories = ["https://github.com/awesome-developer/awesome-repo"]
    mock_backup.docker = {}
    mock_backup._data[ATTR_ADDONS] = [
        {
            ATTR_SLUG: "local_ssh",
            ATTR_NAME: "SSH",
            ATTR_VERSION: "1.0.0",
            ATTR_SIZE: 0,
        }
    ]
    mock_backup._data[ATTR_FOLDERS] = ALL_FOLDERS
    mock_backup._data[ATTR_HOMEASSISTANT] = {
        ATTR_VERSION: AwesomeVersion("2022.8.0"),
        ATTR_SIZE: 0,
    }
    coresys.backups._backups = {"test": mock_backup}
    yield mock_backup


@pytest.fixture
async def mock_partial_backup(coresys: CoreSys, tmp_path) -> Backup:
    """Mock a partial backup."""
    mock_backup = Backup(coresys, Path(tmp_path, "test_backup"))
    mock_backup.new("test", "Test", utcnow().isoformat(), BackupType.PARTIAL)
    mock_backup.repositories = ["https://github.com/awesome-developer/awesome-repo"]
    mock_backup.docker = {}
    mock_backup._data[ATTR_ADDONS] = [
        {
            ATTR_SLUG: "local_ssh",
            ATTR_NAME: "SSH",
            ATTR_VERSION: "1.0.0",
            ATTR_SIZE: 0,
        }
    ]
    mock_backup._data[ATTR_FOLDERS] = ALL_FOLDERS
    mock_backup._data[ATTR_HOMEASSISTANT] = {
        ATTR_VERSION: AwesomeVersion("2022.8.0"),
        ATTR_SIZE: 0,
    }
    coresys.backups._backups = {"test": mock_backup}
    yield mock_backup


@pytest.fixture
async def backups(
    coresys: CoreSys, tmp_path, request: pytest.FixtureRequest
) -> list[Backup]:
    """Create and return mock backups."""
    for i in range(request.param if hasattr(request, "param") else 5):
        slug = f"sn{i+1}"
        temp_tar = Path(tmp_path, f"{slug}.tar")
        with SecureTarFile(temp_tar, "w"):
            pass
        backup = Backup(coresys, temp_tar)
        backup._data = {  # pylint: disable=protected-access
            ATTR_SLUG: slug,
            ATTR_DATE: utcnow().isoformat(),
            ATTR_TYPE: BackupType.PARTIAL
            if "1" == slug[-1] or "5" == slug[-1]
            else BackupType.FULL,
        }
        coresys.backups._backups[backup.slug] = backup

    yield coresys.backups.list_backups


@pytest.fixture
async def journald_logs(coresys: CoreSys) -> MagicMock:
    """Mock journald logs and make it available."""
    with patch.object(
        LogsControl, "available", new=PropertyMock(return_value=True)
    ), patch.object(
        LogsControl, "get_boot_ids", return_value=["aaa", "bbb", "ccc"]
    ), patch.object(
        LogsControl,
        "get_identifiers",
        return_value=["hassio_supervisor", "hassos-config", "kernel"],
    ), patch.object(
        LogsControl, "journald_logs", new=MagicMock()
    ) as logs:
        await coresys.host.logs.load()
        yield logs


@pytest.fixture
async def docker_logs(docker: DockerAPI) -> MagicMock:
    """Mock log output for a container from docker."""
    container_mock = MagicMock()
    container_mock.logs.return_value = load_binary_fixture("logs_docker_container.txt")
    docker.containers.get.return_value = container_mock

    with patch("supervisor.docker.supervisor.os") as os:
        os.environ = {"SUPERVISOR_NAME": "hassio_supervisor"}

        yield container_mock.logs


@pytest.fixture
async def capture_exception() -> Mock:
    """Mock capture exception method for testing."""
    with patch("supervisor.utils.sentry.sentry_connected", return_value=True), patch(
        "supervisor.utils.sentry.sentry_sdk.capture_exception"
    ) as capture_exception:
        yield capture_exception


@pytest.fixture
async def capture_event() -> Mock:
    """Mock capture event for testing."""
    with patch("supervisor.utils.sentry.sentry_connected", return_value=True), patch(
        "supervisor.utils.sentry.sentry_sdk.capture_event"
    ) as capture_event:
        yield capture_event


@pytest.fixture
async def os_available(request: pytest.FixtureRequest) -> None:
    """Mock os as available."""
    version = (
        AwesomeVersion(request.param)
        if hasattr(request, "param")
        else AwesomeVersion("10.2")
    )
    with patch.object(
        OSManager, "available", new=PropertyMock(return_value=True)
    ), patch.object(OSManager, "version", new=PropertyMock(return_value=version)):
        yield


@pytest.fixture
async def mount_propagation(docker: DockerAPI, coresys: CoreSys) -> None:
    """Mock supervisor connected to container with propagation set."""
    os.environ["SUPERVISOR_NAME"] = "hassio_supervisor"
    docker.containers.get.return_value = supervisor = MagicMock()
    supervisor.attrs = {
        "Mounts": [
            {
                "Type": "bind",
                "Source": "/mnt/data/supervisor",
                "Destination": "/data",
                "Mode": "rw",
                "RW": True,
                "Propagation": "slave",
            }
        ]
    }
    await coresys.supervisor.load()
    yield


@pytest.fixture
async def container(docker: DockerAPI) -> MagicMock:
    """Mock attrs and status for container on attach."""
    docker.containers.get.return_value = addon = MagicMock()
    docker.containers.create.return_value = addon
    docker.images.pull.return_value = addon
    docker.images.build.return_value = (addon, "")
    addon.status = "stopped"
    addon.attrs = {"State": {"ExitCode": 0}}
    yield addon
