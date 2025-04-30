"""Test Store API."""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

from aiohttp import ClientResponse
from aiohttp.test_utils import TestClient
import pytest

from supervisor.addons.addon import Addon
from supervisor.arch import CpuArch
from supervisor.config import CoreConfig
from supervisor.const import AddonState
from supervisor.coresys import CoreSys
from supervisor.docker.addon import DockerAddon
from supervisor.docker.const import ContainerState
from supervisor.docker.interface import DockerInterface
from supervisor.docker.monitor import DockerContainerStateEvent
from supervisor.store.addon import AddonStore
from supervisor.store.repository import Repository

from tests.common import load_json_fixture
from tests.const import TEST_ADDON_SLUG

REPO_URL = "https://github.com/awesome-developer/awesome-repo"


@pytest.mark.asyncio
async def test_api_store(
    api_client: TestClient,
    store_addon: AddonStore,
    repository: Repository,
    caplog: pytest.LogCaptureFixture,
):
    """Test /store REST API."""
    resp = await api_client.get("/store")
    result = await resp.json()

    assert result["data"]["addons"][-1]["slug"] == store_addon.slug
    assert result["data"]["repositories"][-1]["slug"] == repository.slug

    assert (
        f"Add-on {store_addon.slug} not supported on this platform" not in caplog.text
    )


@pytest.mark.asyncio
async def test_api_store_addons(api_client: TestClient, store_addon: AddonStore):
    """Test /store/addons REST API."""
    resp = await api_client.get("/store/addons")
    result = await resp.json()

    assert result["data"]["addons"][-1]["slug"] == store_addon.slug


@pytest.mark.asyncio
async def test_api_store_addons_addon(api_client: TestClient, store_addon: AddonStore):
    """Test /store/addons/{addon} REST API."""
    resp = await api_client.get(f"/store/addons/{store_addon.slug}")
    result = await resp.json()
    assert result["data"]["slug"] == store_addon.slug


@pytest.mark.asyncio
async def test_api_store_addons_addon_version(
    api_client: TestClient, store_addon: AddonStore
):
    """Test /store/addons/{addon}/{version} REST API."""
    resp = await api_client.get(f"/store/addons/{store_addon.slug}/1.0.0")
    result = await resp.json()
    assert result["data"]["slug"] == store_addon.slug


@pytest.mark.asyncio
async def test_api_store_repositories(api_client: TestClient, repository: Repository):
    """Test /store/repositories REST API."""
    resp = await api_client.get("/store/repositories")
    result = await resp.json()

    assert result["data"][-1]["slug"] == repository.slug


@pytest.mark.asyncio
async def test_api_store_repositories_repository(
    api_client: TestClient, repository: Repository
):
    """Test /store/repositories/{repository} REST API."""
    resp = await api_client.get(f"/store/repositories/{repository.slug}")
    result = await resp.json()

    assert result["data"]["slug"] == repository.slug


async def test_api_store_add_repository(
    api_client: TestClient, coresys: CoreSys, supervisor_internet: AsyncMock
) -> None:
    """Test POST /store/repositories REST API."""
    with (
        patch("supervisor.store.repository.Repository.load", return_value=None),
        patch("supervisor.store.repository.Repository.validate", return_value=True),
    ):
        response = await api_client.post(
            "/store/repositories", json={"repository": REPO_URL}
        )

    assert response.status == 200
    assert REPO_URL in coresys.store.repository_urls
    assert isinstance(coresys.store.get_from_url(REPO_URL), Repository)


async def test_api_store_remove_repository(
    api_client: TestClient, coresys: CoreSys, repository: Repository
):
    """Test DELETE /store/repositories/{repository} REST API."""
    response = await api_client.delete(f"/store/repositories/{repository.slug}")

    assert response.status == 200
    assert repository.source not in coresys.store.repository_urls
    assert repository.slug not in coresys.store.repositories


async def test_api_store_update_healthcheck(
    api_client: TestClient,
    coresys: CoreSys,
    install_addon_ssh: Addon,
    container: MagicMock,
    tmp_supervisor_data,
    path_extern,
):
    """Test updating an addon with healthcheck waits for health status."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    container.status = "running"
    container.attrs["Config"] = {"Healthcheck": "exists"}
    install_addon_ssh.path_data.mkdir()
    await install_addon_ssh.load()
    with patch(
        "supervisor.store.data.read_json_or_yaml_file",
        return_value=load_json_fixture("addon-config-add-image.json"),
    ):
        await coresys.store.data.update()

    assert install_addon_ssh.need_update is True

    state_changes: list[AddonState] = []
    _container_events_task: asyncio.Task | None = None

    async def container_events():
        nonlocal state_changes
        await asyncio.sleep(0.01)

        await install_addon_ssh.container_state_changed(
            DockerContainerStateEvent(
                name=f"addon_{TEST_ADDON_SLUG}",
                state=ContainerState.STOPPED,
                id="abc123",
                time=1,
            )
        )

        state_changes.append(install_addon_ssh.state)
        await install_addon_ssh.container_state_changed(
            DockerContainerStateEvent(
                name=f"addon_{TEST_ADDON_SLUG}",
                state=ContainerState.RUNNING,
                id="abc123",
                time=1,
            )
        )

        state_changes.append(install_addon_ssh.state)
        await install_addon_ssh.container_state_changed(
            DockerContainerStateEvent(
                name=f"addon_{TEST_ADDON_SLUG}",
                state=ContainerState.HEALTHY,
                id="abc123",
                time=1,
            )
        )

    async def container_events_task(*args, **kwargs):
        nonlocal _container_events_task
        _container_events_task = asyncio.create_task(container_events())

    with (
        patch.object(DockerAddon, "run", new=container_events_task),
        patch.object(DockerInterface, "install"),
        patch.object(DockerAddon, "is_running", return_value=False),
        patch.object(CpuArch, "supported", new=PropertyMock(return_value=["amd64"])),
    ):
        resp = await api_client.post(f"/store/addons/{TEST_ADDON_SLUG}/update")

    assert state_changes == [AddonState.STOPPED, AddonState.STARTUP]
    assert install_addon_ssh.state == AddonState.STARTED
    assert resp.status == 200

    await _container_events_task


@pytest.mark.parametrize("resource", ["store/addons", "addons"])
async def test_api_store_addons_no_changelog(
    api_client: TestClient, coresys: CoreSys, store_addon: AddonStore, resource: str
):
    """Test /store/addons/{addon}/changelog REST API.

    Currently the frontend expects a valid body even in the error case. Make sure that is
    what the API returns.
    """
    assert store_addon.with_changelog is False
    resp = await api_client.get(f"/{resource}/{store_addon.slug}/changelog")
    assert resp.status == 200
    result = await resp.text()
    assert result == "No changelog found for add-on test_store_addon!"


@pytest.mark.parametrize("resource", ["store/addons", "addons"])
async def test_api_detached_addon_changelog(
    api_client: TestClient,
    coresys: CoreSys,
    install_addon_ssh: Addon,
    tmp_supervisor_data: Path,
    resource: str,
):
    """Test /store/addons/{addon}/changelog for an detached addon.

    Currently the frontend expects a valid body even in the error case. Make sure that is
    what the API returns.
    """
    (addons_dir := tmp_supervisor_data / "addons" / "local").mkdir()
    with patch.object(
        CoreConfig, "path_addons_local", new=PropertyMock(return_value=addons_dir)
    ):
        await coresys.store.load()

    assert install_addon_ssh.is_detached is True
    assert install_addon_ssh.with_changelog is False

    resp = await api_client.get(f"/{resource}/{install_addon_ssh.slug}/changelog")
    assert resp.status == 200
    result = await resp.text()
    assert result == "Addon local_ssh does not exist in the store"


@pytest.mark.parametrize("resource", ["store/addons", "addons"])
async def test_api_store_addons_no_documentation(
    api_client: TestClient, coresys: CoreSys, store_addon: AddonStore, resource: str
):
    """Test /store/addons/{addon}/documentation REST API.

    Currently the frontend expects a valid body even in the error case. Make sure that is
    what the API returns.
    """
    assert store_addon.with_documentation is False
    resp = await api_client.get(f"/{resource}/{store_addon.slug}/documentation")
    assert resp.status == 200
    result = await resp.text()
    assert result == "No documentation found for add-on test_store_addon!"


@pytest.mark.parametrize("resource", ["store/addons", "addons"])
async def test_api_detached_addon_documentation(
    api_client: TestClient,
    coresys: CoreSys,
    install_addon_ssh: Addon,
    tmp_supervisor_data: Path,
    resource: str,
):
    """Test /store/addons/{addon}/changelog for an detached addon.

    Currently the frontend expects a valid body even in the error case. Make sure that is
    what the API returns.
    """
    (addons_dir := tmp_supervisor_data / "addons" / "local").mkdir()
    with patch.object(
        CoreConfig, "path_addons_local", new=PropertyMock(return_value=addons_dir)
    ):
        await coresys.store.load()

    assert install_addon_ssh.is_detached is True
    assert install_addon_ssh.with_documentation is False

    resp = await api_client.get(f"/{resource}/{install_addon_ssh.slug}/documentation")
    assert resp.status == 200
    result = await resp.text()
    assert result == "Addon local_ssh does not exist in the store"


async def get_message(resp: ClientResponse, json_expected: bool) -> str:
    """Get message from response based on response type."""
    if json_expected:
        body = await resp.json()
        return body["message"]
    return await resp.text()


@pytest.mark.parametrize(
    ("method", "url", "json_expected"),
    [
        ("get", "/store/addons/bad", True),
        ("get", "/store/addons/bad/1", True),
        ("get", "/store/addons/bad/icon", False),
        ("get", "/store/addons/bad/logo", False),
        ("post", "/store/addons/bad/install", True),
        ("post", "/store/addons/bad/install/1", True),
        ("post", "/store/addons/bad/update", True),
        ("post", "/store/addons/bad/update/1", True),
        # Legacy paths
        ("get", "/addons/bad/icon", False),
        ("get", "/addons/bad/logo", False),
        ("post", "/addons/bad/install", True),
        ("post", "/addons/bad/update", True),
    ],
)
async def test_store_addon_not_found(
    api_client: TestClient, method: str, url: str, json_expected: bool
):
    """Test store addon not found error."""
    resp = await api_client.request(method, url)
    assert resp.status == 404
    assert await get_message(resp, json_expected) == "Addon bad does not exist"


@pytest.mark.parametrize(
    ("method", "url"),
    [
        ("post", "/store/addons/local_ssh/update"),
        ("post", "/store/addons/local_ssh/update/1"),
        # Legacy paths
        ("post", "/addons/local_ssh/update"),
    ],
)
@pytest.mark.usefixtures("repository")
async def test_store_addon_not_installed(api_client: TestClient, method: str, url: str):
    """Test store addon not installed error."""
    resp = await api_client.request(method, url)
    assert resp.status == 400
    body = await resp.json()
    assert body["message"] == "Addon local_ssh is not installed"


@pytest.mark.parametrize(
    ("method", "url"),
    [
        ("get", "/store/repositories/bad"),
        ("delete", "/store/repositories/bad"),
    ],
)
async def test_repository_not_found(api_client: TestClient, method: str, url: str):
    """Test repository not found error."""
    resp = await api_client.request(method, url)
    assert resp.status == 404
    body = await resp.json()
    assert body["message"] == "Repository bad does not exist in the store"


@pytest.mark.parametrize("resource", ["store/addons", "addons"])
async def test_api_store_addons_documentation_corrupted(
    api_client: TestClient, coresys: CoreSys, store_addon: AddonStore, resource: str
):
    """Test /store/addons/{addon}/documentation REST API.

    Test add-on with documentation file with byte sequences which cannot be decoded
    using UTF-8.
    """
    store_addon.path_documentation.write_bytes(b"Text with an invalid UTF-8 char: \xff")
    await store_addon.refresh_path_cache()
    assert store_addon.with_documentation is True

    resp = await api_client.get(f"/{resource}/{store_addon.slug}/documentation")
    assert resp.status == 200
    result = await resp.text()
    assert result == "Text with an invalid UTF-8 char: �"


@pytest.mark.parametrize("resource", ["store/addons", "addons"])
async def test_api_store_addons_changelog_corrupted(
    api_client: TestClient, coresys: CoreSys, store_addon: AddonStore, resource: str
):
    """Test /store/addons/{addon}/changelog REST API.

    Test add-on with changelog file with byte sequences which cannot be decoded
    using UTF-8.
    """
    store_addon.path_changelog.write_bytes(b"Text with an invalid UTF-8 char: \xff")
    await store_addon.refresh_path_cache()
    assert store_addon.with_changelog is True

    resp = await api_client.get(f"/{resource}/{store_addon.slug}/changelog")
    assert resp.status == 200
    result = await resp.text()
    assert result == "Text with an invalid UTF-8 char: �"
