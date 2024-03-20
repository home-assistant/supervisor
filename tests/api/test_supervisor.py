"""Test Supervisor API."""
# pylint: disable=protected-access
from unittest.mock import MagicMock, patch

from aiohttp.test_utils import TestClient
import pytest

from supervisor.coresys import CoreSys
from supervisor.exceptions import StoreGitError, StoreNotFound
from supervisor.store.repository import Repository

from tests.api import common_test_api_advanced_logs
from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.os_agent import OSAgent as OSAgentService

REPO_URL = "https://github.com/awesome-developer/awesome-repo"


async def test_api_supervisor_options_debug(api_client: TestClient, coresys: CoreSys):
    """Test security options force security."""
    assert not coresys.config.debug

    await api_client.post("/supervisor/options", json={"debug": True})

    assert coresys.config.debug


async def test_api_supervisor_options_add_repository(
    api_client: TestClient, coresys: CoreSys
):
    """Test add a repository via POST /supervisor/options REST API."""
    assert REPO_URL not in coresys.store.repository_urls
    with pytest.raises(StoreNotFound):
        coresys.store.get_from_url(REPO_URL)

    with patch("supervisor.store.repository.Repository.load", return_value=None), patch(
        "supervisor.store.repository.Repository.validate", return_value=True
    ):
        response = await api_client.post(
            "/supervisor/options", json={"addons_repositories": [REPO_URL]}
        )

    assert response.status == 200
    assert REPO_URL in coresys.store.repository_urls
    assert isinstance(coresys.store.get_from_url(REPO_URL), Repository)


async def test_api_supervisor_options_remove_repository(
    api_client: TestClient, coresys: CoreSys, repository: Repository
):
    """Test remove a repository via POST /supervisor/options REST API."""
    assert repository.source in coresys.store.repository_urls
    assert repository.slug in coresys.store.repositories

    response = await api_client.post(
        "/supervisor/options", json={"addons_repositories": []}
    )

    assert response.status == 200
    assert repository.source not in coresys.store.repository_urls
    assert repository.slug not in coresys.store.repositories


@pytest.mark.parametrize("git_error", [None, StoreGitError()])
async def test_api_supervisor_options_repositories_skipped_on_error(
    api_client: TestClient, coresys: CoreSys, git_error: StoreGitError
):
    """Test repositories skipped on error via POST /supervisor/options REST API."""
    with patch(
        "supervisor.store.repository.Repository.load", side_effect=git_error
    ), patch(
        "supervisor.store.repository.Repository.validate", return_value=False
    ), patch("supervisor.store.repository.Repository.remove"):
        response = await api_client.post(
            "/supervisor/options", json={"addons_repositories": [REPO_URL]}
        )

    assert response.status == 400
    assert len(coresys.resolution.suggestions) == 0
    assert REPO_URL not in coresys.store.repository_urls
    with pytest.raises(StoreNotFound):
        coresys.store.get_from_url(REPO_URL)


async def test_api_supervisor_options_repo_error_with_config_change(
    api_client: TestClient, coresys: CoreSys
):
    """Test config change with add repository error via POST /supervisor/options REST API."""
    assert not coresys.config.debug

    with patch(
        "supervisor.store.repository.Repository.load", side_effect=StoreGitError()
    ):
        response = await api_client.post(
            "/supervisor/options",
            json={"debug": True, "addons_repositories": [REPO_URL]},
        )

    assert response.status == 400
    assert REPO_URL not in coresys.store.repository_urls

    assert coresys.config.debug
    coresys.updater.save_data.assert_called_once()
    coresys.config.save_data.assert_called_once()


async def test_api_supervisor_options_auto_update(
    api_client: TestClient, coresys: CoreSys
):
    """Test disabling auto update via api."""
    assert coresys.updater.auto_update is True

    response = await api_client.post("/supervisor/options", json={"auto_update": False})

    assert response.status == 200

    assert coresys.updater.auto_update is False


async def test_api_supervisor_options_diagnostics(
    api_client: TestClient,
    coresys: CoreSys,
    os_agent_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
):
    """Test changing diagnostics."""
    os_agent_service: OSAgentService = os_agent_services["os_agent"]
    os_agent_service.Diagnostics = False
    await os_agent_service.ping()
    assert coresys.dbus.agent.diagnostics is False

    with patch("supervisor.utils.sentry.sentry_sdk.init") as sentry_init:
        response = await api_client.post(
            "/supervisor/options", json={"diagnostics": True}
        )
        assert response.status == 200
        sentry_init.assert_called_once()

    await os_agent_service.ping()
    assert coresys.dbus.agent.diagnostics is True

    with patch("supervisor.api.supervisor.close_sentry") as close_sentry:
        response = await api_client.post(
            "/supervisor/options", json={"diagnostics": False}
        )
        assert response.status == 200
        close_sentry.assert_called_once()

    await os_agent_service.ping()
    assert coresys.dbus.agent.diagnostics is False


async def test_api_supervisor_logs(api_client: TestClient, journald_logs: MagicMock):
    """Test supervisor logs."""
    await common_test_api_advanced_logs(
        "/supervisor", "hassio_supervisor", api_client, journald_logs
    )


async def test_api_supervisor_fallback(
    api_client: TestClient, journald_logs: MagicMock, docker_logs: MagicMock
):
    """Check that supervisor logs read from container logs if reading from journald gateway fails badly."""
    journald_logs.side_effect = OSError("Something bad happened!")

    with patch("supervisor.api._LOGGER.exception") as logger:
        resp = await api_client.get("/supervisor/logs")
        logger.assert_called_once_with(
            "Failed to get supervisor logs using advanced_logs API"
        )

    assert resp.status == 200
    assert resp.content_type == "application/octet-stream"
    content = await resp.read()
    assert content.split(b"\n")[0:2] == [
        b"\x1b[36m22-10-11 14:04:23 DEBUG (MainThread) [supervisor.utils.dbus] D-Bus call - org.freedesktop.DBus.Properties.call_get_all on /io/hass/os\x1b[0m",
        b"\x1b[36m22-10-11 14:04:23 DEBUG (MainThread) [supervisor.utils.dbus] D-Bus call - org.freedesktop.DBus.Properties.call_get_all on /io/hass/os/AppArmor\x1b[0m",
    ]


async def test_api_supervisor_reload(api_client: TestClient):
    """Test supervisor reload."""
    resp = await api_client.post("/supervisor/reload")
    assert resp.status == 200
