"""Common test functions."""
from functools import partial
from inspect import unwrap
import os
from pathlib import Path
import re
import subprocess
from typing import Any
from unittest.mock import AsyncMock, MagicMock, Mock, PropertyMock, patch
from uuid import uuid4

from aiohttp import web
from aiohttp.test_utils import TestClient
from awesomeversion import AwesomeVersion
from dbus_fast import BusType
from dbus_fast.aio.message_bus import MessageBus
from dbus_fast.aio.proxy_object import ProxyInterface, ProxyObject
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
from supervisor.dbus.agent import OSAgent
from supervisor.dbus.const import (
    DBUS_OBJECT_BASE,
    DBUS_SIGNAL_NM_CONNECTION_ACTIVE_CHANGED,
    DBUS_SIGNAL_RAUC_INSTALLER_COMPLETED,
)
from supervisor.dbus.hostname import Hostname
from supervisor.dbus.interface import DBusInterface
from supervisor.dbus.network import NetworkManager
from supervisor.dbus.resolved import Resolved
from supervisor.dbus.systemd import Systemd
from supervisor.dbus.timedate import TimeDate
from supervisor.dbus.udisks2 import UDisks2
from supervisor.docker.manager import DockerAPI
from supervisor.docker.monitor import DockerMonitor
from supervisor.host.logs import LogsControl
from supervisor.store.addon import AddonStore
from supervisor.store.repository import Repository
from supervisor.utils.dbus import DBUS_INTERFACE_PROPERTIES, DBus
from supervisor.utils.dt import utcnow

from .common import (
    exists_fixture,
    get_dbus_name,
    load_binary_fixture,
    load_fixture,
    load_json_fixture,
    mock_dbus_services,
)
from .const import TEST_ADDON_SLUG
from .dbus_service_mocks.base import DBusServiceMock

# pylint: disable=redefined-outer-name, protected-access


async def mock_async_return_true() -> bool:
    """Mock methods to return True."""
    return True


@pytest.fixture
def docker() -> DockerAPI:
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
        "supervisor.docker.manager.DockerAPI.load"
    ), patch(
        "supervisor.docker.manager.DockerAPI.unload"
    ):
        docker_obj = DockerAPI(MagicMock())
        docker_obj.info.logging = "journald"
        docker_obj.info.storage = "overlay2"
        docker_obj.info.version = "1.0.0"

        docker_obj.config.registries = {}

        yield docker_obj


@pytest.fixture
async def dbus_bus() -> MessageBus:
    """Message bus mock."""
    bus = AsyncMock(spec=MessageBus)
    setattr(bus, "_name_owners", {})
    yield bus


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
async def dbus_services(
    request: pytest.FixtureRequest, dbus_session: MessageBus
) -> dict[str, DBusServiceMock | list[DBusServiceMock]]:
    """Mock specified dbus services on session bus.

    Should be used indirectly. Provide a dictionary where the key a dbus service to mock
    (module must exist in dbus_service_mocks). Value is the object path for the mocked service.
    Can also be a list of object paths or None (if the mocked service defines the object path).
    """
    with patch("supervisor.dbus.manager.MessageBus.connect", return_value=dbus_session):
        yield await mock_dbus_services(request.param, dbus_session)


def _process_pseudo_variant(data: dict[str, Any]) -> Any:
    """Process pseudo variant into value."""
    if data["_type"] == "ay":
        return bytearray(data["_value"], encoding="utf-8")
    if data["_type"] == "aay":
        return [bytearray(i, encoding="utf-8") for i in data["_value"]]

    # Unknown type, return as is
    return data


def process_dbus_json(data: Any) -> Any:
    """Replace pseudo-variants with values of unsupported json types as necessary."""
    if not isinstance(data, dict):
        return data

    if len(data.keys()) == 2 and "_type" in data and "_value" in data:
        return _process_pseudo_variant(data)

    return {k: process_dbus_json(v) for k, v in data.items()}


def mock_get_properties(object_path: str, interface: str) -> str:
    """Mock get dbus properties."""
    base, _, latest = object_path.rpartition("/")
    fixture = interface.replace(".", "_")

    if latest.isnumeric() or base in [
        "/org/freedesktop/UDisks2/block_devices",
        "/org/freedesktop/UDisks2/drives",
    ]:
        fixture = f"{fixture}_{latest}"

    return process_dbus_json(load_json_fixture(f"{fixture}.json"))


async def mock_init_proxy(self):
    """Mock init dbus proxy."""
    filetype = "xml"
    fixture = (
        self.object_path.replace("/", "_")[1:]
        if self.object_path != DBUS_OBJECT_BASE
        else self.bus_name.replace(".", "_")
    )

    if not exists_fixture(f"{fixture}.{filetype}"):
        fixture = re.sub(r"_[0-9]+$", "", fixture)

        # special case
        if exists_fixture(f"{fixture}_~.{filetype}"):
            fixture = f"{fixture}_~"

    # Use dbus-next infrastructure to parse introspection xml
    self._proxy_obj = ProxyObject(
        self.bus_name,
        self.object_path,
        load_fixture(f"{fixture}.{filetype}"),
        self._bus,
    )
    self._add_interfaces()

    if DBUS_INTERFACE_PROPERTIES in self._proxies:
        setattr(
            self._proxies[DBUS_INTERFACE_PROPERTIES],
            "call_get_all",
            lambda interface: mock_get_properties(self.object_path, interface),
        )


@pytest.fixture
def dbus(dbus_bus: MessageBus) -> list[str]:
    """Mock DBUS."""
    dbus_commands = []

    async def mock_wait_for_signal(self):
        if (
            self._interface + "." + self._member
            == DBUS_SIGNAL_NM_CONNECTION_ACTIVE_CHANGED
        ):
            return [2, 0]

        if self._interface + "." + self._member == DBUS_SIGNAL_RAUC_INSTALLER_COMPLETED:
            return [0]

    async def mock_signal___aenter__(self):
        return self

    async def mock_signal___aexit__(self, exc_t, exc_v, exc_tb):
        pass

    async def mock_call_dbus(
        proxy_interface: ProxyInterface,
        method: str,
        *args,
        unpack_variants: bool = True,
    ):
        if (
            proxy_interface.introspection.name == DBUS_INTERFACE_PROPERTIES
            and method == "call_get_all"
        ):
            return mock_get_properties(proxy_interface.path, args[0])

        [dbus_type, dbus_name] = method.split("_", 1)

        if dbus_type in ["get", "set"]:
            dbus_name = get_dbus_name(
                proxy_interface.introspection.properties, dbus_name
            )
            dbus_commands.append(
                f"{proxy_interface.path}-{proxy_interface.introspection.name}.{dbus_name}"
            )

            if dbus_type == "set":
                return

            return mock_get_properties(
                proxy_interface.path, proxy_interface.introspection.name
            )[dbus_name]

        dbus_name = get_dbus_name(proxy_interface.introspection.methods, dbus_name)
        dbus_commands.append(
            f"{proxy_interface.path}-{proxy_interface.introspection.name}.{dbus_name}"
        )

        if proxy_interface.path != DBUS_OBJECT_BASE:
            fixture = proxy_interface.path.replace("/", "_")[1:]
            fixture = f"{fixture}-{dbus_name}"
        else:
            fixture = (
                f'{proxy_interface.introspection.name.replace(".", "_")}_{dbus_name}'
            )

        if exists_fixture(f"{fixture}.json"):
            return process_dbus_json(load_json_fixture(f"{fixture}.json"))

    with patch("supervisor.utils.dbus.DBus.call_dbus", new=mock_call_dbus), patch(
        "supervisor.utils.dbus.DBus._init_proxy", new=mock_init_proxy
    ), patch(
        "supervisor.utils.dbus.DBusSignalWrapper.__aenter__", new=mock_signal___aenter__
    ), patch(
        "supervisor.utils.dbus.DBusSignalWrapper.__aexit__", new=mock_signal___aexit__
    ), patch(
        "supervisor.utils.dbus.DBusSignalWrapper.wait_for_signal",
        new=mock_wait_for_signal,
    ), patch(
        "supervisor.dbus.manager.MessageBus.connect", return_value=dbus_bus
    ):
        yield dbus_commands


@pytest.fixture
async def dbus_minimal(dbus_bus: MessageBus) -> MessageBus:
    """Mock DBus without mocking call_dbus or signals but handle properties fixture."""
    with patch("supervisor.utils.dbus.DBus._init_proxy", new=mock_init_proxy), patch(
        "supervisor.dbus.manager.MessageBus.connect", return_value=dbus_bus
    ):
        yield dbus_bus


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
) -> dict[str, DBusServiceMock]:
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
    network_manager_services: dict[str, DBusServiceMock], dbus_session_bus: MessageBus
) -> NetworkManager:
    """Mock NetworkManager."""
    nm_obj = NetworkManager()
    await nm_obj.connect(dbus_session_bus)
    yield nm_obj


async def mock_dbus_interface(
    dbus: DBus, dbus_bus: MessageBus, instance: DBusInterface
) -> DBusInterface:
    """Mock dbus for a DBusInterface instance."""
    instance.dbus = dbus
    await instance.connect(dbus_bus)
    return instance


@pytest.fixture
async def hostname(dbus: DBus, dbus_bus: MessageBus) -> Hostname:
    """Mock Hostname."""
    yield await mock_dbus_interface(dbus, dbus_bus, Hostname())


@pytest.fixture
async def timedate(dbus: DBus, dbus_bus: MessageBus) -> TimeDate:
    """Mock Timedate."""
    yield await mock_dbus_interface(dbus, dbus_bus, TimeDate())


@pytest.fixture
async def systemd(dbus: DBus, dbus_bus: MessageBus) -> Systemd:
    """Mock Systemd."""
    yield await mock_dbus_interface(dbus, dbus_bus, Systemd())


@pytest.fixture
async def os_agent(dbus: DBus, dbus_bus: MessageBus) -> OSAgent:
    """Mock OSAgent."""
    yield await mock_dbus_interface(dbus, dbus_bus, OSAgent())


@pytest.fixture
async def resolved(dbus: DBus, dbus_bus: MessageBus) -> Resolved:
    """Mock REsolved."""
    yield await mock_dbus_interface(dbus, dbus_bus, Resolved())


@pytest.fixture
async def udisks2(dbus: DBus, dbus_bus: MessageBus) -> UDisks2:
    """Mock UDisks2."""
    yield await mock_dbus_interface(dbus, dbus_bus, UDisks2())


@pytest.fixture
async def coresys(
    event_loop, docker, dbus, dbus_bus, aiohttp_client, run_dir
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

    # Mock test client
    coresys_obj.arch._default_arch = "amd64"
    coresys_obj._machine = "qemux86-64"
    coresys_obj._machine_id = uuid4()

    # Mock host communication
    coresys_obj._dbus._bus = dbus_bus
    network_manager = NetworkManager()
    network_manager.dbus = dbus
    await network_manager.connect(dbus_bus)
    coresys_obj._dbus._network = network_manager

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
    coresys_obj.homeassistant.api.check_api_state = mock_async_return_true
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

    await coresys_obj.websession.close()


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
async def api_client(aiohttp_client, coresys: CoreSys) -> TestClient:
    """Fixture for RestAPI client."""

    @web.middleware
    async def _security_middleware(request: web.Request, handler: web.RequestHandler):
        """Make request are from Core."""
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
