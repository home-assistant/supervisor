"""Test Supervisor API."""
# pylint: disable=protected-access
import asyncio
from unittest.mock import patch

from aiohttp.test_utils import TestClient
import pytest

from supervisor.coresys import CoreSys
from supervisor.exceptions import StoreGitError, StoreNotFound
from supervisor.store.repository import Repository

REPO_URL = "https://github.com/awesome-developer/awesome-repo"


@pytest.mark.asyncio
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
    ), patch(
        "supervisor.store.repository.Repository.remove"
    ):
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
    api_client: TestClient, coresys: CoreSys, dbus: list[str]
):
    """Test changing diagnostics."""
    await coresys.dbus.agent.connect(coresys.dbus.bus)
    dbus.clear()

    response = await api_client.post("/supervisor/options", json={"diagnostics": True})
    await asyncio.sleep(0)

    assert response.status == 200
    assert dbus == ["/io/hass/os-io.hass.os.Diagnostics"]
