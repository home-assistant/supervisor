"""Test Docker API."""

from aiohttp.test_utils import TestClient
from dbus_fast import DBusError, ErrorType
import pytest

from supervisor.coresys import CoreSys
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue, Suggestion

from tests.dbus_service_mocks.agent_system import System as SystemService
from tests.dbus_service_mocks.base import DBusServiceMock


async def test_api_docker_info(api_client_with_prefix: tuple[TestClient, str]):
    """Test docker info api."""
    api_client, prefix = api_client_with_prefix
    resp = await api_client.get(f"{prefix}/docker/info")
    result = await resp.json()

    assert result["data"]["logging"] == "journald"
    assert result["data"]["storage"] == "overlay2"
    assert result["data"]["version"] == "1.0.0"


async def test_api_network_enable_ipv6(
    coresys: CoreSys, api_client_with_prefix: tuple[TestClient, str]
):
    """Test setting docker network for enabled IPv6."""
    api_client, prefix = api_client_with_prefix
    assert coresys.docker.config.enable_ipv6 is None

    resp = await api_client.post(f"{prefix}/docker/options", json={"enable_ipv6": True})
    assert resp.status == 200

    assert coresys.docker.config.enable_ipv6 is True

    resp = await api_client.get(f"{prefix}/docker/info")
    assert resp.status == 200
    body = await resp.json()
    assert body["data"]["enable_ipv6"] is True


async def test_api_network_mtu(
    coresys: CoreSys, api_client_with_prefix: tuple[TestClient, str]
):
    """Test setting docker network MTU."""
    api_client, prefix = api_client_with_prefix
    assert coresys.docker.config.mtu is None

    resp = await api_client.post(f"{prefix}/docker/options", json={"mtu": 1450})
    assert resp.status == 200

    assert coresys.docker.config.mtu == 1450

    resp = await api_client.get(f"{prefix}/docker/info")
    assert resp.status == 200
    body = await resp.json()
    assert body["data"]["mtu"] == 1450

    # Test setting MTU to None
    resp = await api_client.post(f"{prefix}/docker/options", json={"mtu": None})
    assert resp.status == 200

    assert coresys.docker.config.mtu is None

    resp = await api_client.get(f"{prefix}/docker/info")
    assert resp.status == 200
    body = await resp.json()
    assert body["data"]["mtu"] is None


async def test_api_network_combined_options(
    coresys: CoreSys, api_client_with_prefix: tuple[TestClient, str]
):
    """Test setting both IPv6 and MTU together."""
    api_client, prefix = api_client_with_prefix
    assert coresys.docker.config.enable_ipv6 is None
    assert coresys.docker.config.mtu is None

    resp = await api_client.post(
        f"{prefix}/docker/options", json={"enable_ipv6": True, "mtu": 1400}
    )
    assert resp.status == 200

    assert coresys.docker.config.enable_ipv6 is True
    assert coresys.docker.config.mtu == 1400

    resp = await api_client.get(f"{prefix}/docker/info")
    assert resp.status == 200
    body = await resp.json()
    assert body["data"]["enable_ipv6"] is True
    assert body["data"]["mtu"] == 1400


async def test_registry_not_found(api_client_with_prefix: tuple[TestClient, str]):
    """Test registry not found error."""
    api_client, prefix = api_client_with_prefix
    resp = await api_client.delete(f"{prefix}/docker/registries/bad")
    assert resp.status == 404
    body = await resp.json()
    assert body["message"] == "Hostname bad does not exist in registries"


@pytest.mark.parametrize("os_available", ["17.0.rc1"], indirect=True)
async def test_api_migrate_docker_storage_driver(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    os_agent_services: dict[str, DBusServiceMock],
    os_available,
):
    """Test Docker storage driver migration."""
    api_client, prefix = api_client_with_prefix
    system_service: SystemService = os_agent_services["agent_system"]
    system_service.MigrateDockerStorageDriver.calls.clear()

    resp = await api_client.post(
        f"{prefix}/docker/migrate-storage-driver",
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


@pytest.mark.parametrize("os_available", ["17.0.rc1"], indirect=True)
async def test_api_migrate_docker_storage_driver_invalid_backend(
    api_client_with_prefix: tuple[TestClient, str],
    os_available,
):
    """Test 400 is returned for invalid storage driver."""
    api_client, prefix = api_client_with_prefix
    resp = await api_client.post(
        f"{prefix}/docker/migrate-storage-driver",
        json={"storage_driver": "invalid"},
    )
    assert resp.status == 400


async def test_api_migrate_docker_storage_driver_not_os(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
):
    """Test 404 is returned if not running on HAOS."""
    api_client, prefix = api_client_with_prefix
    resp = await api_client.post(
        f"{prefix}/docker/migrate-storage-driver",
        json={"storage_driver": "overlayfs"},
    )
    assert resp.status == 404


@pytest.mark.parametrize("os_available", ["16.2"], indirect=True)
async def test_api_migrate_docker_storage_driver_old_os(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    os_available,
):
    """Test 404 is returned if OS is older than 17.0."""
    api_client, prefix = api_client_with_prefix
    resp = await api_client.post(
        f"{prefix}/docker/migrate-storage-driver",
        json={"storage_driver": "overlayfs"},
    )
    assert resp.status == 404


@pytest.mark.parametrize("os_available", ["18.3.dev20260826"], indirect=True)
async def test_api_docker_reset_storage(
    coresys: CoreSys,
    api_client_with_prefix: tuple[TestClient, str],
    os_agent_services: dict[str, DBusServiceMock],
    os_available,
):
    """Test Docker storage reset."""
    api_client, prefix = api_client_with_prefix
    system_service: SystemService = os_agent_services["agent_system"]
    system_service.ScheduleDockerStorageReset.calls.clear()

    resp = await api_client.post(f"{prefix}/docker/reset-storage")
    assert resp.status == 200

    assert system_service.ScheduleDockerStorageReset.calls == [()]
    assert (
        Issue(IssueType.REBOOT_REQUIRED, ContextType.SYSTEM)
        in coresys.resolution.issues
    )
    assert (
        Suggestion(SuggestionType.EXECUTE_REBOOT, ContextType.SYSTEM)
        in coresys.resolution.suggestions
    )


async def test_api_docker_reset_storage_not_os(
    api_client_with_prefix: tuple[TestClient, str],
):
    """Test 404 is returned if not running on HAOS."""
    api_client, prefix = api_client_with_prefix
    resp = await api_client.post(f"{prefix}/docker/reset-storage")
    assert resp.status == 404


@pytest.mark.parametrize("os_available", ["18.3.dev20260825"], indirect=True)
async def test_api_docker_reset_storage_old_os(
    api_client_with_prefix: tuple[TestClient, str],
    os_available,
):
    """Test 404 is returned if OS is older than the first release with the reset."""
    api_client, prefix = api_client_with_prefix
    resp = await api_client.post(f"{prefix}/docker/reset-storage")
    assert resp.status == 404


@pytest.mark.parametrize("os_available", ["18.3.dev20260826"], indirect=True)
async def test_api_docker_reset_storage_schedule_failed(
    coresys: CoreSys,
    api_client_with_prefix: tuple[TestClient, str],
    os_agent_services: dict[str, DBusServiceMock],
    os_available,
):
    """Test error if OS Agent could not schedule the reset."""
    api_client, prefix = api_client_with_prefix
    system_service: SystemService = os_agent_services["agent_system"]
    system_service.ScheduleDockerStorageReset.calls.clear()
    system_service.response_schedule_docker_storage_reset = False

    resp = await api_client.post(f"{prefix}/docker/reset-storage")
    assert resp.status == 400
    body = await resp.json()
    assert (
        body["message"]
        == "Can't schedule Docker storage reset, check host logs for details"
    )

    assert system_service.ScheduleDockerStorageReset.calls == [()]
    assert (
        Issue(IssueType.REBOOT_REQUIRED, ContextType.SYSTEM)
        not in coresys.resolution.issues
    )


@pytest.mark.parametrize("os_available", ["18.3.dev20260826"], indirect=True)
async def test_api_docker_reset_storage_dbus_error(
    coresys: CoreSys,
    api_client_with_prefix: tuple[TestClient, str],
    os_agent_services: dict[str, DBusServiceMock],
    os_available,
):
    """Test error if the D-Bus call fails."""
    api_client, prefix = api_client_with_prefix
    system_service: SystemService = os_agent_services["agent_system"]
    system_service.ScheduleDockerStorageReset.calls.clear()
    system_service.response_schedule_docker_storage_reset = DBusError(
        ErrorType.FAILED, "fail"
    )

    resp = await api_client.post(f"{prefix}/docker/reset-storage")
    assert resp.status == 400
    body = await resp.json()
    assert body["message"] == "Can't schedule Docker storage reset: fail"

    assert system_service.ScheduleDockerStorageReset.calls == [()]
    assert (
        Issue(IssueType.REBOOT_REQUIRED, ContextType.SYSTEM)
        not in coresys.resolution.issues
    )
