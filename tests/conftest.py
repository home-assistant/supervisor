"""Common test functions."""
from functools import partial
from inspect import unwrap
from pathlib import Path
import re
from typing import Any
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch
from uuid import uuid4

from aiohttp import web
from awesomeversion import AwesomeVersion
from dbus_next import introspection as intr
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
from supervisor.dbus.const import DBUS_SIGNAL_NM_CONNECTION_ACTIVE_CHANGED
from supervisor.dbus.hostname import Hostname
from supervisor.dbus.interface import DBusInterface
from supervisor.dbus.network import NetworkManager
from supervisor.dbus.resolved import Resolved
from supervisor.dbus.systemd import Systemd
from supervisor.dbus.timedate import TimeDate
from supervisor.docker.manager import DockerAPI
from supervisor.docker.monitor import DockerMonitor
from supervisor.store.addon import AddonStore
from supervisor.store.repository import Repository
from supervisor.utils.dbus import DBus
from supervisor.utils.dt import utcnow

from .common import exists_fixture, load_fixture, load_json_fixture
from .const import TEST_ADDON_SLUG

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
def dbus() -> DBus:
    """Mock DBUS."""
    dbus_commands = []

    async def mock_get_properties(dbus_obj, interface):
        latest = dbus_obj.object_path.split("/")[-1]
        fixture = interface.replace(".", "_")

        if latest.isnumeric():
            fixture = f"{fixture}_{latest}"

        return load_json_fixture(f"{fixture}.json")

    async def mock_get_property(dbus_obj, interface, name):
        properties = await mock_get_properties(dbus_obj, interface)
        return properties[name]

    async def mock_wait_for_signal(self):
        if (
            self._interface + "." + self._method
            == DBUS_SIGNAL_NM_CONNECTION_ACTIVE_CHANGED
        ):
            return [2, 0]

    async def mock_signal___aenter__(self):
        return self

    async def mock_signal___aexit__(self, exc_t, exc_v, exc_tb):
        pass

    async def mock_init_proxy(self):

        filetype = "xml"
        fixture = self.object_path.replace("/", "_")[1:]
        if not exists_fixture(f"{fixture}.{filetype}"):
            fixture = re.sub(r"_[0-9]+$", "", fixture)

            # special case
            if exists_fixture(f"{fixture}_~.{filetype}"):
                fixture = f"{fixture}_~"

        # Use dbus-next infrastructure to parse introspection xml
        node = intr.Node.parse(load_fixture(f"{fixture}.{filetype}"))
        self._add_interfaces(node)

    async def mock_call_dbus(
        self, method: str, *args: list[Any], remove_signature: bool = True
    ):

        fixture = self.object_path.replace("/", "_")[1:]
        fixture = f"{fixture}-{method.split('.')[-1]}"
        dbus_commands.append(fixture)

        return load_json_fixture(f"{fixture}.json")

    with patch("supervisor.utils.dbus.DBus.call_dbus", new=mock_call_dbus), patch(
        "supervisor.dbus.interface.DBusInterface.is_connected",
        return_value=True,
    ), patch(
        "supervisor.utils.dbus.DBus.get_properties", new=mock_get_properties
    ), patch(
        "supervisor.utils.dbus.DBus._init_proxy", new=mock_init_proxy
    ), patch(
        "supervisor.utils.dbus.DBusSignalWrapper.__aenter__", new=mock_signal___aenter__
    ), patch(
        "supervisor.utils.dbus.DBusSignalWrapper.__aexit__", new=mock_signal___aexit__
    ), patch(
        "supervisor.utils.dbus.DBusSignalWrapper.wait_for_signal",
        new=mock_wait_for_signal,
    ), patch(
        "supervisor.utils.dbus.DBus.get_property", new=mock_get_property
    ):
        yield dbus_commands


@pytest.fixture
async def network_manager(dbus) -> NetworkManager:
    """Mock NetworkManager."""
    nm_obj = NetworkManager()
    nm_obj.dbus = dbus

    # Init
    await nm_obj.connect()
    await nm_obj.update()

    yield nm_obj


async def mock_dbus_interface(dbus: DBus, instance: DBusInterface) -> DBusInterface:
    """Mock dbus for a DBusInterface instance."""
    instance.dbus = dbus
    await instance.connect()
    return instance


@pytest.fixture
async def hostname(dbus: DBus) -> Hostname:
    """Mock Hostname."""
    yield await mock_dbus_interface(dbus, Hostname())


@pytest.fixture
async def timedate(dbus: DBus) -> TimeDate:
    """Mock Timedate."""
    yield await mock_dbus_interface(dbus, TimeDate())


@pytest.fixture
async def systemd(dbus: DBus) -> Systemd:
    """Mock Systemd."""
    yield await mock_dbus_interface(dbus, Systemd())


@pytest.fixture
async def os_agent(dbus: DBus) -> OSAgent:
    """Mock OSAgent."""
    yield await mock_dbus_interface(dbus, OSAgent())


@pytest.fixture
async def resolved(dbus: DBus) -> Resolved:
    """Mock REsolved."""
    yield await mock_dbus_interface(dbus, Resolved())


@pytest.fixture
async def coresys(
    event_loop, docker, network_manager, aiohttp_client, run_dir
) -> CoreSys:
    """Create a CoreSys Mock."""
    with patch("supervisor.bootstrap.initialize_system"), patch(
        "supervisor.bootstrap.setup_diagnostics"
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
async def api_client(aiohttp_client, coresys: CoreSys):
    """Fixture for RestAPI client."""

    @web.middleware
    async def _security_middleware(request: web.Request, handler: web.RequestHandler):
        """Make request are from Core."""
        request[REQUEST_FROM] = coresys.homeassistant
        return await handler(request)

    api = RestAPI(coresys)
    api.webapp = web.Application(middlewares=[_security_middleware])
    api.start = AsyncMock()
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
