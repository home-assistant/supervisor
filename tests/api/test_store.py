"""Test Store API."""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, PropertyMock, patch

from aiodocker.containers import DockerContainer
from aiohttp.test_utils import TestClient
from awesomeversion import AwesomeVersion
import pytest

from supervisor.addons.addon import Addon
from supervisor.arch import CpuArchManager
from supervisor.backups.manager import BackupManager
from supervisor.config import CoreConfig
from supervisor.const import AddonState, CoreState
from supervisor.coresys import CoreSys
from supervisor.docker.addon import DockerAddon
from supervisor.docker.const import ContainerState
from supervisor.docker.interface import DockerInterface
from supervisor.docker.monitor import DockerContainerStateEvent
from supervisor.exceptions import StoreGitError
from supervisor.homeassistant.const import WSEvent
from supervisor.homeassistant.module import HomeAssistant
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue, Suggestion
from supervisor.store.addon import AddonStore
from supervisor.store.repository import Repository

from tests.common import AsyncIterator, load_json_fixture
from tests.const import TEST_ADDON_SLUG

REPO_URL = "https://github.com/awesome-developer/awesome-repo"


@pytest.mark.asyncio
async def test_api_store(
    api_client: TestClient,
    store_addon: AddonStore,
    test_repository: Repository,
    caplog: pytest.LogCaptureFixture,
):
    """Test /store REST API."""
    resp = await api_client.get("/store")
    result = await resp.json()

    assert result["data"]["addons"][-1]["slug"] == store_addon.slug
    assert result["data"]["repositories"][-1]["slug"] == test_repository.slug

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
async def test_api_store_repositories(
    api_client: TestClient, test_repository: Repository
):
    """Test /store/repositories REST API."""
    resp = await api_client.get("/store/repositories")
    result = await resp.json()

    assert result["data"][-1]["slug"] == test_repository.slug


@pytest.mark.asyncio
async def test_api_store_repositories_repository(
    api_client: TestClient, test_repository: Repository
):
    """Test /store/repositories/{repository} REST API."""
    resp = await api_client.get(f"/store/repositories/{test_repository.slug}")
    result = await resp.json()

    assert result["data"]["slug"] == test_repository.slug


async def test_api_store_add_repository(
    api_client: TestClient, coresys: CoreSys, supervisor_internet: AsyncMock
) -> None:
    """Test POST /store/repositories REST API."""
    with (
        patch("supervisor.store.repository.RepositoryGit.load", return_value=None),
        patch("supervisor.store.repository.RepositoryGit.validate", return_value=True),
    ):
        response = await api_client.post(
            "/store/repositories", json={"repository": REPO_URL}
        )

    assert response.status == 200
    assert REPO_URL in coresys.store.repository_urls


async def test_api_store_remove_repository(
    api_client: TestClient, coresys: CoreSys, test_repository: Repository
):
    """Test DELETE /store/repositories/{repository} REST API."""
    response = await api_client.delete(f"/store/repositories/{test_repository.slug}")

    assert response.status == 200
    assert test_repository.source not in coresys.store.repository_urls
    assert test_repository.slug not in coresys.store.repositories


@pytest.mark.parametrize("repo", ["core", "a474bbd1"])
@pytest.mark.usefixtures("test_repository")
async def test_api_store_repair_repository(api_client: TestClient, repo: str):
    """Test POST /store/repositories/{repository}/repair REST API."""
    with patch("supervisor.store.repository.RepositoryGit.reset") as mock_reset:
        response = await api_client.post(f"/store/repositories/{repo}/repair")

    assert response.status == 200
    mock_reset.assert_called_once()


@pytest.mark.parametrize(
    "issue_type", [IssueType.CORRUPT_REPOSITORY, IssueType.FATAL_ERROR]
)
@pytest.mark.usefixtures("test_repository")
async def test_api_store_repair_repository_removes_suggestion(
    api_client: TestClient,
    coresys: CoreSys,
    test_repository: Repository,
    issue_type: IssueType,
):
    """Test POST /store/repositories/core/repair REST API removes EXECUTE_RESET suggestions."""
    issue = Issue(issue_type, ContextType.STORE, reference=test_repository.slug)
    suggestion = Suggestion(
        SuggestionType.EXECUTE_RESET, ContextType.STORE, reference=test_repository.slug
    )
    coresys.resolution.add_issue(issue, suggestions=[SuggestionType.EXECUTE_RESET])
    with patch("supervisor.store.repository.RepositoryGit.reset") as mock_reset:
        response = await api_client.post(
            f"/store/repositories/{test_repository.slug}/repair"
        )

    assert response.status == 200
    mock_reset.assert_called_once()
    assert issue not in coresys.resolution.issues
    assert suggestion not in coresys.resolution.suggestions


@pytest.mark.usefixtures("test_repository")
async def test_api_store_repair_repository_local_fail(api_client: TestClient):
    """Test POST /store/repositories/local/repair REST API fails."""
    response = await api_client.post("/store/repositories/local/repair")

    assert response.status == 400
    result = await response.json()
    assert result["error_key"] == "store_repository_local_cannot_reset"
    assert result["extra_fields"] == {"local_repo": "local"}
    assert result["message"] == "Can't reset repository local as it is not git based!"


async def test_api_store_repair_repository_git_error(
    api_client: TestClient, test_repository: Repository
):
    """Test POST /store/repositories/{repository}/repair REST API git error."""
    with patch(
        "supervisor.store.git.GitRepo.reset",
        side_effect=StoreGitError("Git error"),
    ):
        response = await api_client.post(
            f"/store/repositories/{test_repository.slug}/repair"
        )

    assert response.status == 500
    result = await response.json()
    assert result["error_key"] == "store_repository_unknown_error"
    assert result["extra_fields"] == {
        "repo": test_repository.slug,
        "logs_command": "ha supervisor logs",
    }
    assert (
        result["message"]
        == f"An unknown error occurred with addon repository {test_repository.slug}. Check supervisor logs for details (check with 'ha supervisor logs')"
    )


@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
async def test_api_store_update_healthcheck(
    api_client: TestClient,
    coresys: CoreSys,
    install_addon_ssh: Addon,
    container: DockerContainer,
):
    """Test updating an addon with healthcheck waits for health status."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    container.show.return_value["State"]["Status"] = "running"
    container.show.return_value["State"]["Running"] = True
    container.show.return_value["Config"] = {"Healthcheck": "exists"}
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
        patch.object(
            CpuArchManager, "supported", new=PropertyMock(return_value=["amd64"])
        ),
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
        ("get", "/store/addons/bad/availability", True),
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
    if json_expected:
        body = await resp.json()
        assert body["message"] == "Addon bad does not exist in the store"
        assert body["error_key"] == "store_addon_not_found_error"
        assert body["extra_fields"] == {"addon": "bad"}
    else:
        assert await resp.text() == "Addon bad does not exist in the store"


@pytest.mark.parametrize(
    ("method", "url"),
    [
        ("post", "/store/addons/local_ssh/update"),
        ("post", "/store/addons/local_ssh/update/1"),
        # Legacy paths
        ("post", "/addons/local_ssh/update"),
    ],
)
@pytest.mark.usefixtures("test_repository")
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


@pytest.mark.usefixtures("test_repository", "tmp_supervisor_data")
async def test_addon_install_in_background(api_client: TestClient, coresys: CoreSys):
    """Test installing an addon in the background."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    event = asyncio.Event()

    # Mock a long-running install task
    async def mock_addon_install(*args, **kwargs):
        await event.wait()

    with patch.object(Addon, "install", new=mock_addon_install):
        resp = await api_client.post(
            "/store/addons/local_ssh/install", json={"background": True}
        )

    assert resp.status == 200
    body = await resp.json()
    assert (job := coresys.jobs.get_job(body["data"]["job_id"]))
    assert job.name == "addon_manager_install"
    event.set()


@pytest.mark.usefixtures("install_addon_ssh")
async def test_background_addon_install_fails_fast(
    api_client: TestClient, coresys: CoreSys
):
    """Test background addon install returns error not job if validation fails."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    resp = await api_client.post(
        "/store/addons/local_ssh/install", json={"background": True}
    )
    assert resp.status == 400
    body = await resp.json()
    assert body["message"] == "Add-on local_ssh is already installed"


@pytest.mark.parametrize(
    ("make_backup", "backup_called", "update_called"),
    [(True, True, False), (False, False, True)],
)
@pytest.mark.usefixtures("test_repository", "tmp_supervisor_data")
async def test_addon_update_in_background(
    api_client: TestClient,
    coresys: CoreSys,
    install_addon_ssh: Addon,
    make_backup: bool,
    backup_called: bool,
    update_called: bool,
):
    """Test updating an addon in the background."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    install_addon_ssh.data_store["version"] = "10.0.0"
    event = asyncio.Event()
    mock_update_called = mock_backup_called = False

    # Mock backup/update as long-running tasks
    async def mock_addon_update(*args, **kwargs):
        nonlocal mock_update_called
        mock_update_called = True
        await event.wait()

    async def mock_partial_backup(*args, **kwargs):
        nonlocal mock_backup_called
        mock_backup_called = True
        await event.wait()

    with (
        patch.object(Addon, "update", new=mock_addon_update),
        patch.object(BackupManager, "do_backup_partial", new=mock_partial_backup),
    ):
        resp = await api_client.post(
            "/store/addons/local_ssh/update",
            json={"background": True, "backup": make_backup},
        )

    assert mock_backup_called is backup_called
    assert mock_update_called is update_called

    assert resp.status == 200
    body = await resp.json()
    assert (job := coresys.jobs.get_job(body["data"]["job_id"]))
    assert job.name == "addon_manager_update"
    event.set()


@pytest.mark.usefixtures("install_addon_ssh")
async def test_background_addon_update_fails_fast(
    api_client: TestClient, coresys: CoreSys
):
    """Test background addon update returns error not job if validation doesn't succeed."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    resp = await api_client.post(
        "/store/addons/local_ssh/update", json={"background": True}
    )
    assert resp.status == 400
    body = await resp.json()
    assert body["message"] == "No update available for add-on local_ssh"


async def test_api_store_addons_addon_availability_success(
    api_client: TestClient, store_addon: AddonStore
):
    """Test /store/addons/{addon}/availability REST API - success case."""
    resp = await api_client.get(f"/store/addons/{store_addon.slug}/availability")
    assert resp.status == 200


@pytest.mark.parametrize(
    ("supported_architectures", "api_action", "api_method", "installed"),
    [
        (["i386"], "availability", "get", False),
        (["i386", "aarch64"], "availability", "get", False),
        (["i386"], "install", "post", False),
        (["i386", "aarch64"], "install", "post", False),
        (["i386"], "update", "post", True),
        (["i386", "aarch64"], "update", "post", True),
    ],
)
async def test_api_store_addons_addon_availability_arch_not_supported(
    api_client: TestClient,
    coresys: CoreSys,
    supported_architectures: list[str],
    api_action: str,
    api_method: str,
    installed: bool,
):
    """Test availability errors for /store/addons/{addon}/* REST APIs - architecture not supported."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    # Create an addon with unsupported architecture
    addon_obj = AddonStore(coresys, "test_arch_addon")
    coresys.addons.store[addon_obj.slug] = addon_obj

    # Set addon config with unsupported architecture
    addon_config = {
        "advanced": False,
        "arch": supported_architectures,
        "slug": "test_arch_addon",
        "description": "Test arch add-on",
        "name": "Test Arch Add-on",
        "repository": "test",
        "stage": "stable",
        "version": "1.0.0",
    }
    coresys.store.data.addons[addon_obj.slug] = addon_config
    if installed:
        coresys.addons.local[addon_obj.slug] = Addon(coresys, addon_obj.slug)
        coresys.addons.data.user[addon_obj.slug] = {"version": AwesomeVersion("0.0.1")}

    # Mock the system architecture to be different
    with patch.object(
        CpuArchManager, "supported", new=PropertyMock(return_value=["amd64"])
    ):
        resp = await api_client.request(
            api_method, f"/store/addons/{addon_obj.slug}/{api_action}"
        )
        assert resp.status == 400
        result = await resp.json()
        assert result["error_key"] == "addon_not_supported_architecture_error"
        assert result["extra_fields"] == {
            "slug": "test_arch_addon",
            "architectures": (architectures := ", ".join(supported_architectures)),
        }
        assert (
            result["message"]
            == f"Add-on test_arch_addon not supported on this platform, supported architectures: {architectures}"
        )


@pytest.mark.parametrize(
    ("supported_machines", "api_action", "api_method", "installed"),
    [
        (["odroid-n2"], "availability", "get", False),
        (["!qemux86-64"], "availability", "get", False),
        (["a", "b"], "availability", "get", False),
        (["odroid-n2"], "install", "post", False),
        (["!qemux86-64"], "install", "post", False),
        (["a", "b"], "install", "post", False),
        (["odroid-n2"], "update", "post", True),
        (["!qemux86-64"], "update", "post", True),
        (["a", "b"], "update", "post", True),
    ],
)
async def test_api_store_addons_addon_availability_machine_not_supported(
    api_client: TestClient,
    coresys: CoreSys,
    supported_machines: list[str],
    api_action: str,
    api_method: str,
    installed: bool,
):
    """Test availability errors for /store/addons/{addon}/* REST APIs - machine not supported."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    # Create an addon with unsupported machine type
    addon_obj = AddonStore(coresys, "test_machine_addon")
    coresys.addons.store[addon_obj.slug] = addon_obj

    # Set addon config with unsupported machine
    addon_config = {
        "advanced": False,
        "arch": ["amd64"],
        "machine": supported_machines,
        "slug": "test_machine_addon",
        "description": "Test machine add-on",
        "name": "Test Machine Add-on",
        "repository": "test",
        "stage": "stable",
        "version": "1.0.0",
    }
    coresys.store.data.addons[addon_obj.slug] = addon_config
    if installed:
        coresys.addons.local[addon_obj.slug] = Addon(coresys, addon_obj.slug)
        coresys.addons.data.user[addon_obj.slug] = {"version": AwesomeVersion("0.0.1")}

    # Mock the system machine to be different
    with patch.object(CoreSys, "machine", new=PropertyMock(return_value="qemux86-64")):
        resp = await api_client.request(
            api_method, f"/store/addons/{addon_obj.slug}/{api_action}"
        )
        assert resp.status == 400
        result = await resp.json()
        assert result["error_key"] == "addon_not_supported_machine_type_error"
        assert result["extra_fields"] == {
            "slug": "test_machine_addon",
            "machine_types": (machine_types := ", ".join(supported_machines)),
        }
        assert (
            result["message"]
            == f"Add-on test_machine_addon not supported on this machine, supported machine types: {machine_types}"
        )


@pytest.mark.parametrize(
    ("api_action", "api_method", "installed"),
    [
        ("availability", "get", False),
        ("install", "post", False),
        ("update", "post", True),
    ],
)
async def test_api_store_addons_addon_availability_homeassistant_version_too_old(
    api_client: TestClient,
    coresys: CoreSys,
    api_action: str,
    api_method: str,
    installed: bool,
):
    """Test availability errors for /store/addons/{addon}/* REST APIs - Home Assistant version too old."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    # Create an addon that requires newer Home Assistant version
    addon_obj = AddonStore(coresys, "test_version_addon")
    coresys.addons.store[addon_obj.slug] = addon_obj

    # Set addon config with minimum Home Assistant version requirement
    addon_config = {
        "advanced": False,
        "arch": ["amd64"],
        "homeassistant": "2023.1.1",  # Requires newer version than current
        "slug": "test_version_addon",
        "description": "Test version add-on",
        "name": "Test Version Add-on",
        "repository": "test",
        "stage": "stable",
        "version": "1.0.0",
    }
    coresys.store.data.addons[addon_obj.slug] = addon_config
    if installed:
        coresys.addons.local[addon_obj.slug] = Addon(coresys, addon_obj.slug)
        coresys.addons.data.user[addon_obj.slug] = {"version": AwesomeVersion("0.0.1")}

    # Mock the Home Assistant version to be older
    with patch.object(
        HomeAssistant,
        "version",
        new=PropertyMock(return_value=AwesomeVersion("2022.1.1")),
    ):
        resp = await api_client.request(
            api_method, f"/store/addons/{addon_obj.slug}/{api_action}"
        )
        assert resp.status == 400
        result = await resp.json()
        assert result["error_key"] == "addon_not_supported_home_assistant_version_error"
        assert result["extra_fields"] == {
            "slug": "test_version_addon",
            "version": "2023.1.1",
        }
        assert (
            result["message"]
            == "Add-on test_version_addon not supported on this system, requires Home Assistant version 2023.1.1 or greater"
        )


async def test_api_store_addons_addon_availability_installed_addon(
    api_client: TestClient, install_addon_ssh: Addon
):
    """Test /store/addons/{addon}/availability REST API - installed addon checks against latest version."""
    resp = await api_client.get("/store/addons/local_ssh/availability")
    assert resp.status == 200

    install_addon_ssh.data_store["version"] = AwesomeVersion("10.0.0")
    install_addon_ssh.data_store["homeassistant"] = AwesomeVersion("2023.1.1")

    # Mock the Home Assistant version to be older
    with patch.object(
        HomeAssistant,
        "version",
        new=PropertyMock(return_value=AwesomeVersion("2022.1.1")),
    ):
        resp = await api_client.get("/store/addons/local_ssh/availability")
        assert resp.status == 400
        result = await resp.json()
        assert (
            "requires Home Assistant version 2023.1.1 or greater" in result["message"]
        )


@pytest.mark.parametrize(
    ("action", "job_name", "addon_slug"),
    [
        ("install", "addon_manager_install", "local_ssh"),
        ("update", "addon_manager_update", "local_example"),
    ],
)
@pytest.mark.usefixtures("tmp_supervisor_data")
async def test_api_progress_updates_addon_install_update(
    api_client: TestClient,
    coresys: CoreSys,
    ha_ws_client: AsyncMock,
    install_addon_example: Addon,
    action: str,
    job_name: str,
    addon_slug: str,
):
    """Test progress updates sent to Home Assistant for installs/updates."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    coresys.core.set_state(CoreState.RUNNING)

    logs = load_json_fixture("docker_pull_image_log.json")
    coresys.docker.images.pull.return_value = AsyncIterator(logs)

    coresys.arch._supported_arch = ["amd64"]  # pylint: disable=protected-access
    install_addon_example.data_store["version"] = AwesomeVersion("2.0.0")

    with (
        patch.object(Addon, "load"),
        patch.object(Addon, "need_build", new=PropertyMock(return_value=False)),
        patch.object(Addon, "latest_need_build", new=PropertyMock(return_value=False)),
    ):
        resp = await api_client.post(f"/store/addons/{addon_slug}/{action}")

    assert resp.status == 200

    events = [
        {
            "stage": evt.args[0]["data"]["data"]["stage"],
            "progress": evt.args[0]["data"]["data"]["progress"],
            "done": evt.args[0]["data"]["data"]["done"],
        }
        for evt in ha_ws_client.async_send_command.call_args_list
        if "data" in evt.args[0]
        and evt.args[0]["data"]["event"] == WSEvent.JOB
        and evt.args[0]["data"]["data"]["name"] == job_name
        and evt.args[0]["data"]["data"]["reference"] == addon_slug
    ]
    assert events[:4] == [
        {
            "stage": None,
            "progress": 0,
            "done": False,
        },
        {
            "stage": None,
            "progress": 0.1,
            "done": False,
        },
        {
            "stage": None,
            "progress": 1.7,
            "done": False,
        },
        {
            "stage": None,
            "progress": 4.0,
            "done": False,
        },
    ]
    assert events[-5:] == [
        {
            "stage": None,
            "progress": 98.2,
            "done": False,
        },
        {
            "stage": None,
            "progress": 98.3,
            "done": False,
        },
        {
            "stage": None,
            "progress": 99.3,
            "done": False,
        },
        {
            "stage": None,
            "progress": 100,
            "done": False,
        },
        {
            "stage": None,
            "progress": 100,
            "done": True,
        },
    ]
