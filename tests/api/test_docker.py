"""Test Docker API."""

from aiohttp.test_utils import TestClient
import pytest

from supervisor.coresys import CoreSys
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue, Suggestion

from tests.dbus_service_mocks.agent_system import System as SystemService
from tests.dbus_service_mocks.base import DBusServiceMock


@pytest.mark.asyncio
async def test_api_docker_info(api_client: TestClient):
    """Test docker info api."""
    resp = await api_client.get("/docker/info")
    result = await resp.json()

    assert result["data"]["logging"] == "journald"
    assert result["data"]["storage"] == "overlay2"
    assert result["data"]["version"] == "1.0.0"


async def test_api_network_enable_ipv6(coresys: CoreSys, api_client: TestClient):
    """Test setting docker network for enabled IPv6."""
    assert coresys.docker.config.enable_ipv6 is None

    resp = await api_client.post("/docker/options", json={"enable_ipv6": True})
    assert resp.status == 200

    assert coresys.docker.config.enable_ipv6 is True

    resp = await api_client.get("/docker/info")
    assert resp.status == 200
    body = await resp.json()
    assert body["data"]["enable_ipv6"] is True


async def test_api_network_mtu(coresys: CoreSys, api_client: TestClient):
    """Test setting docker network MTU."""
    assert coresys.docker.config.mtu is None

    resp = await api_client.post("/docker/options", json={"mtu": 1450})
    assert resp.status == 200

    assert coresys.docker.config.mtu == 1450

    resp = await api_client.get("/docker/info")
    assert resp.status == 200
    body = await resp.json()
    assert body["data"]["mtu"] == 1450

    # Test setting MTU to None
    resp = await api_client.post("/docker/options", json={"mtu": None})
    assert resp.status == 200

    assert coresys.docker.config.mtu is None

    resp = await api_client.get("/docker/info")
    assert resp.status == 200
    body = await resp.json()
    assert body["data"]["mtu"] is None


async def test_api_network_combined_options(coresys: CoreSys, api_client: TestClient):
    """Test setting both IPv6 and MTU together."""
    assert coresys.docker.config.enable_ipv6 is None
    assert coresys.docker.config.mtu is None

    resp = await api_client.post(
        "/docker/options", json={"enable_ipv6": True, "mtu": 1400}
    )
    assert resp.status == 200

    assert coresys.docker.config.enable_ipv6 is True
    assert coresys.docker.config.mtu == 1400

    resp = await api_client.get("/docker/info")
    assert resp.status == 200
    body = await resp.json()
    assert body["data"]["enable_ipv6"] is True
    assert body["data"]["mtu"] == 1400


async def test_registry_not_found(api_client: TestClient):
    """Test registry not found error."""
    resp = await api_client.delete("/docker/registries/bad")
    assert resp.status == 404
    body = await resp.json()
    assert body["message"] == "Hostname bad does not exist in registries"


@pytest.mark.parametrize("os_available", ["17.0.rc1"], indirect=True)
async def test_api_migrate_docker_storage_driver(
    api_client: TestClient,
    coresys: CoreSys,
    os_agent_services: dict[str, DBusServiceMock],
    os_available,
):
    """Test Docker storage driver migration."""
    system_service: SystemService = os_agent_services["agent_system"]
    system_service.MigrateDockerStorageDriver.calls.clear()

    resp = await api_client.post(
        "/docker/migrate-storage-driver",
        json={"storage_driver": "overlayfs"},
    )
    assert resp.status == 200

    assert system_service.MigrateDockerStorageDriver.calls == [("overlayfs",)]
    assert (
        Issue(IssueType.REBOOT_REQUIRED, ContextType.SYSTEM)
        in coresys.resolution.issues
    )
    assert (
        Suggestion(SuggestionType.EXECUTE_REBOOT, ContextType.SYSTEM)
        in coresys.resolution.suggestions
    )

    # Test migration back to overlay2 (graph driver)
    system_service.MigrateDockerStorageDriver.calls.clear()
    resp = await api_client.post(
        "/docker/migrate-storage-driver",
        json={"storage_driver": "overlay2"},
    )
    assert resp.status == 200
    assert system_service.MigrateDockerStorageDriver.calls == [("overlay2",)]


@pytest.mark.parametrize("os_available", ["17.0.rc1"], indirect=True)
async def test_api_migrate_docker_storage_driver_invalid_backend(
    api_client: TestClient,
    os_available,
):
    """Test 400 is returned for invalid storage driver."""
    resp = await api_client.post(
        "/docker/migrate-storage-driver",
        json={"storage_driver": "invalid"},
    )
    assert resp.status == 400


async def test_api_migrate_docker_storage_driver_not_os(
    api_client: TestClient,
    coresys: CoreSys,
):
    """Test 404 is returned if not running on HAOS."""
    resp = await api_client.post(
        "/docker/migrate-storage-driver",
        json={"storage_driver": "overlayfs"},
    )
    assert resp.status == 404


@pytest.mark.parametrize("os_available", ["16.2"], indirect=True)
async def test_api_migrate_docker_storage_driver_old_os(
    api_client: TestClient,
    coresys: CoreSys,
    os_available,
):
    """Test 404 is returned if OS is older than 17.0."""
    resp = await api_client.post(
        "/docker/migrate-storage-driver",
        json={"storage_driver": "overlayfs"},
    )
    assert resp.status == 404
