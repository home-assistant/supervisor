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

from supervisor import config as su_config
from supervisor.addons.addon import Addon
from supervisor.api import RestAPI
from supervisor.bootstrap import initialize_coresys
from supervisor.const import REQUEST_FROM
from supervisor.coresys import CoreSys
from supervisor.dbus.const import DBUS_SIGNAL_NM_CONNECTION_ACTIVE_CHANGED
from supervisor.dbus.network import NetworkManager
from supervisor.docker import DockerAPI
from supervisor.store.addon import AddonStore
from supervisor.store.repository import Repository
from supervisor.utils.dbus import DBus

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

    with patch("supervisor.docker.DockerClient", return_value=MagicMock()), patch(
        "supervisor.docker.DockerAPI.images", return_value=MagicMock()
    ), patch("supervisor.docker.DockerAPI.containers", return_value=MagicMock()), patch(
        "supervisor.docker.DockerAPI.api", return_value=MagicMock()
    ), patch(
        "supervisor.docker.DockerAPI.images.list", return_value=images
    ), patch(
        "supervisor.docker.DockerAPI.info",
        return_value=MagicMock(),
    ), patch(
        "supervisor.docker.DockerConfig",
        return_value=MagicMock(),
    ):
        docker_obj = DockerAPI()
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

    async def mock_call_dbus(self, method: str, *args: list[Any]):

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


@pytest.fixture
async def coresys(loop, docker, network_manager, aiohttp_client, run_dir) -> CoreSys:
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

    # Mock test client
    coresys_obj.arch._default_arch = "amd64"
    coresys_obj._machine = "qemux86-64"
    coresys_obj._machine_id = uuid4()

    # Mock host communication
    coresys_obj._dbus._network = network_manager

    # Mock docker
    coresys_obj._docker = docker

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
    coresys.store.data.addons[addon_obj.slug] = load_json_fixture("add-on.json")
    yield addon_obj


@pytest.fixture
async def repository(coresys: CoreSys):
    """Repository fixture."""
    coresys.config.drop_addon_repository("https://github.com/hassio-addons/repository")
    await coresys.store.load()
    repository_obj = Repository(
        coresys, "https://github.com/awesome-developer/awesome-repo"
    )

    coresys.store.repositories[repository_obj.slug] = repository_obj

    yield repository_obj


@pytest.fixture
def install_addon_ssh(coresys: CoreSys, repository):
    """Install local_ssh add-on."""
    store = coresys.addons.store[TEST_ADDON_SLUG]
    coresys.addons.data.install(store)
    addon = Addon(coresys, store.slug)
    coresys.addons.local[addon.slug] = addon
