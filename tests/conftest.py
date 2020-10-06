"""Common test functions."""
from unittest.mock import MagicMock, PropertyMock, patch
from uuid import uuid4

from aiohttp import web
from aiohttp.test_utils import TestClient
import pytest

from supervisor.api import RestAPI
from supervisor.bootstrap import initialize_coresys
from supervisor.coresys import CoreSys
from supervisor.dbus.const import DBUS_NAME_NM, DBUS_OBJECT_BASE
from supervisor.dbus.network import NetworkManager
from supervisor.dbus.network.interface import NetworkInterface
from supervisor.docker import DockerAPI
from supervisor.utils.gdbus import DBus

from tests.common import load_fixture, load_json_fixture

# pylint: disable=redefined-outer-name, protected-access


@pytest.fixture
def docker() -> DockerAPI:
    """Mock DockerAPI."""
    images = [MagicMock(tags=["homeassistant/amd64-hassio-supervisor:latest"])]

    with patch("docker.DockerClient", return_value=MagicMock()), patch(
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

    async def mock_get_properties(_, interface):
        return load_json_fixture(f"{interface.replace('.', '_')}.json")

    async def mock_send(_, command, silent=False):
        if silent:
            return ""

        filetype = "xml" if "--xml" in command else "fixture"
        fixture = f"{command[6].replace('/', '_')[1:]}.{filetype}"
        return load_fixture(fixture)

    with patch("supervisor.utils.gdbus.DBus._send", new=mock_send), patch(
        "supervisor.dbus.interface.DBusInterface.is_connected",
        return_value=True,
    ), patch("supervisor.utils.gdbus.DBus.get_properties", new=mock_get_properties):

        dbus_obj = DBus(DBUS_NAME_NM, DBUS_OBJECT_BASE)

        yield dbus_obj


@pytest.fixture
async def network_manager(dbus) -> NetworkManager:
    """Mock NetworkManager."""

    async def dns_update():
        pass

    with patch("supervisor.dbus.network.NetworkManager.dns", return_value=MagicMock()):
        nm_obj = NetworkManager()
    nm_obj.dns.update = dns_update
    nm_obj.dbus = dbus
    await nm_obj.connect()
    await nm_obj.update()

    yield nm_obj


@pytest.fixture
async def coresys(loop, docker, dbus, network_manager, aiohttp_client) -> CoreSys:
    """Create a CoreSys Mock."""
    with patch("supervisor.bootstrap.initialize_system_data"), patch(
        "supervisor.bootstrap.setup_diagnostics"
    ), patch(
        "supervisor.bootstrap.fetch_timezone",
        return_value="Europe/Zurich",
    ), patch(
        "aiohttp.ClientSession",
        return_value=TestClient.session,
    ):
        coresys_obj = await initialize_coresys()

    # Mock save json
    coresys_obj.ingress.save_data = MagicMock()

    # Mock test client
    coresys_obj.arch._default_arch = "amd64"
    coresys_obj._machine = "qemux86-64"
    coresys_obj._machine_id = uuid4()

    # Mock host communication
    coresys_obj._dbus = dbus
    coresys_obj._dbus.network = network_manager

    # Mock docker
    coresys_obj._docker = docker

    yield coresys_obj


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
    api = RestAPI(coresys)
    api.webapp = web.Application()
    await api.load()
    yield await aiohttp_client(api.webapp)


@pytest.fixture
async def network_interface(dbus):
    """Fixture for a network interface."""
    interface = NetworkInterface()
    await interface.connect(dbus, "/org/freedesktop/NetworkManager/ActiveConnection/1")
    await interface.connection.update_information()
    yield interface


@pytest.fixture
def store_manager(coresys: CoreSys):
    """Fixture for the store manager."""
    sm_obj = coresys.store
    sm_obj.repositories = set(coresys.config.addons_repositories)
    with patch("supervisor.store.data.StoreData.update", return_value=MagicMock()):
        yield sm_obj
