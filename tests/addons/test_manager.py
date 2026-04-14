"""Test app manager."""

import asyncio
from collections.abc import AsyncGenerator, Generator
from copy import deepcopy
from pathlib import Path
from unittest.mock import AsyncMock, Mock, PropertyMock, call, patch

from aiodocker.containers import DockerContainer
from awesomeversion import AwesomeVersion
import pytest

from supervisor.addons.addon import App
from supervisor.arch import CpuArchManager
from supervisor.config import CoreConfig
from supervisor.const import ATTR_INGRESS, AppBoot, AppStartup, AppState, BusEvent
from supervisor.coresys import CoreSys
from supervisor.docker.addon import DockerApp
from supervisor.docker.const import ContainerState
from supervisor.docker.interface import DockerInterface
from supervisor.docker.manager import DockerAPI
from supervisor.docker.monitor import DockerContainerStateEvent
from supervisor.exceptions import (
    AppConfigurationError,
    AppsError,
    DockerAPIError,
    DockerNotFound,
)
from supervisor.plugins.dns import PluginDns
from supervisor.resolution.const import (
    ContextType,
    IssueType,
    SuggestionType,
    UnhealthyReason,
)
from supervisor.resolution.data import Issue, Suggestion
from supervisor.store.addon import AppStore
from supervisor.store.repository import RepositoryLocal
from supervisor.utils import check_exception_chain
from supervisor.utils.common import write_json_file

from tests.common import load_json_fixture
from tests.const import TEST_ADDON_SLUG

BOOT_FAIL_ISSUE = Issue(
    IssueType.BOOT_FAIL, ContextType.ADDON, reference=TEST_ADDON_SLUG
)
BOOT_FAIL_SUGGESTIONS = [
    Suggestion(
        SuggestionType.EXECUTE_START, ContextType.ADDON, reference=TEST_ADDON_SLUG
    ),
    Suggestion(
        SuggestionType.DISABLE_BOOT, ContextType.ADDON, reference=TEST_ADDON_SLUG
    ),
]


@pytest.fixture(autouse=True)
async def fixture_mock_arch_disk() -> AsyncGenerator[None]:
    """Mock supported arch and disk space."""
    with (
        patch("shutil.disk_usage", return_value=(42, 42, 2 * (1024.0**3))),
        patch.object(
            CpuArchManager, "supported", new=PropertyMock(return_value=["amd64"])
        ),
    ):
        yield


@pytest.fixture(autouse=True)
async def fixture_remove_wait_boot(coresys: CoreSys) -> AsyncGenerator[None]:
    """Remove default wait boot time for tests."""
    coresys.config.wait_boot = 0


@pytest.fixture(name="install_app_example_image")
async def fixture_install_app_example_image(
    coresys: CoreSys, test_repository
) -> Generator[App]:
    """Install local_example app with image."""
    store = coresys.apps.store["local_example_image"]
    await coresys.apps.data.install(store)
    # pylint: disable-next=protected-access
    coresys.apps.data._data = coresys.apps.data._schema(coresys.apps.data._data)

    app = App(coresys, store.slug)
    coresys.apps.local[app.slug] = app
    yield app


async def test_image_added_removed_on_update(coresys: CoreSys, install_app_ssh: App):
    """Test image added or removed from app config on update."""
    assert install_app_ssh.need_update is False
    with patch(
        "supervisor.store.data.read_json_or_yaml_file",
        return_value=load_json_fixture("addon-config-add-image.json"),
    ):
        await coresys.store.data.update()

    assert install_app_ssh.need_update is True
    assert install_app_ssh.image == "local/amd64-addon-ssh"
    assert coresys.apps.store.get(TEST_ADDON_SLUG).image == "test/amd64-my-ssh-addon"

    with (
        patch.object(DockerInterface, "install") as install,
        patch.object(DockerApp, "_build") as build,
    ):
        await coresys.apps.update(TEST_ADDON_SLUG)
        build.assert_not_called()
        install.assert_called_once_with(
            AwesomeVersion("10.0.0"), "test/amd64-my-ssh-addon", False, "amd64"
        )

    assert install_app_ssh.need_update is False
    with patch(
        "supervisor.store.data.read_json_or_yaml_file",
        return_value=load_json_fixture("addon-config-remove-image.json"),
    ):
        await coresys.store.data.update()

    assert install_app_ssh.need_update is True
    assert install_app_ssh.image == "test/amd64-my-ssh-addon"
    assert coresys.apps.store.get(TEST_ADDON_SLUG).image == "local/amd64-addon-ssh"

    with (
        patch.object(DockerInterface, "install") as install,
        patch.object(DockerApp, "_build") as build,
    ):
        await coresys.apps.update(TEST_ADDON_SLUG)
        build.assert_called_once_with(AwesomeVersion("11.0.0"), "local/amd64-addon-ssh")
        install.assert_not_called()


async def test_app_boot_skip_host_network_gateway_unprotected(
    coresys: CoreSys, install_app_ssh: App
):
    """Test host network apps are skipped when gateway is unprotected."""
    install_app_ssh.boot = AppBoot.AUTO
    coresys.resolution.add_unhealthy_reason(UnhealthyReason.DOCKER_GATEWAY_UNPROTECTED)
    with (
        patch.object(
            type(install_app_ssh), "host_network", new=PropertyMock(return_value=True)
        ),
        patch.object(App, "start") as start,
    ):
        await coresys.apps.boot(AppStartup.APPLICATION)
        start.assert_not_called()


async def test_app_boot_host_network_gateway_protected(
    coresys: CoreSys, install_app_ssh: App
):
    """Test host network apps boot normally when gateway is protected."""
    install_app_ssh.boot = AppBoot.AUTO
    assert (
        UnhealthyReason.DOCKER_GATEWAY_UNPROTECTED not in coresys.resolution.unhealthy
    )
    with (
        patch.object(
            type(install_app_ssh), "host_network", new=PropertyMock(return_value=True)
        ),
        patch.object(App, "start", return_value=asyncio.Future()) as start,
    ):
        start.return_value.set_result(None)
        await coresys.apps.boot(AppStartup.APPLICATION)
        start.assert_called_once()


@pytest.mark.parametrize("err", [DockerAPIError, DockerNotFound])
async def test_app_boot_system_error(
    coresys: CoreSys, install_app_ssh: App, capture_exception: Mock, err
):
    """Test system errors during app boot."""
    install_app_ssh.boot = AppBoot.AUTO
    assert coresys.resolution.issues == []
    assert coresys.resolution.suggestions == []
    with (
        patch.object(App, "write_options"),
        patch.object(DockerApp, "run", side_effect=err),
    ):
        await coresys.apps.boot(AppStartup.APPLICATION)

    capture_exception.assert_not_called()
    assert coresys.resolution.issues == [BOOT_FAIL_ISSUE]
    assert coresys.resolution.suggestions == BOOT_FAIL_SUGGESTIONS


async def test_app_boot_user_error(
    coresys: CoreSys, install_app_ssh: App, capture_exception: Mock
):
    """Test user error during app boot."""
    install_app_ssh.boot = AppBoot.AUTO
    with patch.object(App, "write_options", side_effect=AppConfigurationError):
        await coresys.apps.boot(AppStartup.APPLICATION)

    capture_exception.assert_not_called()
    assert coresys.resolution.issues == [BOOT_FAIL_ISSUE]
    assert coresys.resolution.suggestions == BOOT_FAIL_SUGGESTIONS


async def test_app_boot_other_error(
    coresys: CoreSys, install_app_ssh: App, capture_exception: Mock
):
    """Test other errors captured during app boot."""
    install_app_ssh.boot = AppBoot.AUTO
    err = OSError()
    with (
        patch.object(App, "write_options"),
        patch.object(DockerApp, "run", side_effect=err),
    ):
        await coresys.apps.boot(AppStartup.APPLICATION)

    capture_exception.assert_called_once_with(err)
    assert coresys.resolution.issues == [BOOT_FAIL_ISSUE]
    assert coresys.resolution.suggestions == BOOT_FAIL_SUGGESTIONS


async def test_app_shutdown_error(
    coresys: CoreSys, install_app_ssh: App, capture_exception: Mock
):
    """Test errors captured during app shutdown."""
    install_app_ssh.state = AppState.STARTED
    with patch.object(DockerApp, "stop", side_effect=DockerNotFound()):
        await coresys.apps.shutdown(AppStartup.APPLICATION)

    assert install_app_ssh.state == AppState.ERROR
    capture_exception.assert_called_once()
    assert check_exception_chain(
        capture_exception.call_args[0][0], (AppsError, DockerNotFound)
    )


@pytest.mark.usefixtures("websession")
async def test_app_uninstall_removes_discovery(coresys: CoreSys, install_app_ssh: App):
    """Test discovery messages removed when app uninstalled."""
    assert coresys.discovery.list_messages == []

    message = await coresys.discovery.send(
        install_app_ssh, "mqtt", {"host": "localhost", "port": 1883}
    )
    assert message.addon == TEST_ADDON_SLUG
    assert message.service == "mqtt"
    assert coresys.discovery.list_messages == [message]

    coresys.homeassistant.api.ensure_access_token = AsyncMock()

    await coresys.apps.uninstall(TEST_ADDON_SLUG)
    await asyncio.sleep(0)

    # Find the delete call among all request calls (send also uses request)
    delete_calls = [
        c for c in coresys.websession.request.call_args_list if c.args[0] == "delete"
    ]
    assert len(delete_calls) == 1
    assert (
        delete_calls[0].args[1]
        == f"http://172.30.32.1:8123/api/hassio_push/discovery/{message.uuid}"
    )
    assert delete_calls[0].kwargs["json"] == {
        "addon": TEST_ADDON_SLUG,
        "service": "mqtt",
        "uuid": message.uuid,
    }

    assert coresys.apps.installed == []
    assert coresys.discovery.list_messages == []


@pytest.mark.usefixtures("install_app_ssh")
async def test_load(coresys: CoreSys, caplog: pytest.LogCaptureFixture):
    """Test app manager load."""
    caplog.clear()

    with (
        patch.object(DockerInterface, "attach") as attach,
        patch.object(PluginDns, "write_hosts") as write_hosts,
    ):
        await coresys.apps.load()

        attach.assert_called_once_with(version=AwesomeVersion("9.2.1"))
        write_hosts.assert_called_once()

    assert "Found 1 installed apps" in caplog.text


@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
async def test_boot_waits_for_apps(coresys: CoreSys, install_app_ssh: App):
    """Test app manager boot waits for apps."""
    install_app_ssh.path_data.mkdir()
    await install_app_ssh.load()
    await asyncio.sleep(0)
    assert install_app_ssh.state == AppState.STOPPED

    app_state: AppState | None = None

    async def fire_container_event(*args, **kwargs):
        nonlocal app_state

        app_state = install_app_ssh.state
        coresys.bus.fire_event(
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
            DockerContainerStateEvent(
                name=f"addon_{TEST_ADDON_SLUG}",
                state=ContainerState.RUNNING,
                id="abc123",
                time=1,
            ),
        )

    with patch.object(DockerApp, "run", new=fire_container_event):
        await coresys.apps.boot(AppStartup.APPLICATION)

    assert app_state == AppState.STOPPED
    assert install_app_ssh.state == AppState.STARTED


@pytest.mark.parametrize("status", ["running", "stopped"])
@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
async def test_update(
    coresys: CoreSys,
    install_app_ssh: App,
    container: DockerContainer,
    status: str,
):
    """Test app update."""
    container.show.return_value["State"]["Status"] = status
    container.show.return_value["State"]["Running"] = status == "running"
    install_app_ssh.path_data.mkdir()
    await install_app_ssh.load()
    with patch(
        "supervisor.store.data.read_json_or_yaml_file",
        return_value=load_json_fixture("addon-config-add-image.json"),
    ):
        await coresys.store.data.update()

    assert install_app_ssh.need_update is True

    with (
        patch.object(DockerInterface, "install"),
        patch.object(DockerApp, "is_running", return_value=False),
    ):
        start_task = await coresys.apps.update(TEST_ADDON_SLUG)

    assert bool(start_task) is (status == "running")


@pytest.mark.parametrize("status", ["running", "stopped"])
@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
async def test_rebuild(
    coresys: CoreSys,
    install_app_ssh: App,
    container: DockerContainer,
    status: str,
):
    """Test app rebuild."""
    container.show.return_value["State"]["Status"] = status
    container.show.return_value["State"]["Running"] = status == "running"
    install_app_ssh.path_data.mkdir()
    await install_app_ssh.load()

    with (
        patch.object(DockerApp, "_build"),
        patch.object(DockerApp, "is_running", return_value=False),
        patch.object(App, "need_build", new=PropertyMock(return_value=True)),
    ):
        start_task = await coresys.apps.rebuild(TEST_ADDON_SLUG)

    assert bool(start_task) is (status == "running")


@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
async def test_start_wait_resolved_on_uninstall_in_startup(
    coresys: CoreSys,
    install_app_ssh: App,
    container: DockerContainer,
) -> None:
    """Test uninstall resolves the startup wait task when app is in STARTUP state."""
    install_app_ssh.path_data.mkdir()
    container.show.return_value["Config"] = {"Healthcheck": "exists"}
    await install_app_ssh.load()
    await asyncio.sleep(0)
    assert install_app_ssh.state == AppState.STOPPED

    start_task = await install_app_ssh.start()
    assert start_task

    coresys.bus.fire_event(
        BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
        DockerContainerStateEvent(
            name=f"addon_{TEST_ADDON_SLUG}",
            state=ContainerState.RUNNING,
            id="abc123",
            time=1,
        ),
    )
    await asyncio.sleep(0.01)

    assert not start_task.done()
    assert install_app_ssh.state == AppState.STARTUP

    await coresys.apps.uninstall(TEST_ADDON_SLUG)
    assert start_task.done()
    assert start_task.exception() is None


async def test_repository_file_missing(
    coresys: CoreSys, tmp_supervisor_data: Path, caplog: pytest.LogCaptureFixture
):
    """Test repository file is missing."""
    with patch.object(
        CoreConfig,
        "path_apps_git",
        new=PropertyMock(return_value=tmp_supervisor_data / "addons" / "git"),
    ):
        repo_dir = coresys.config.path_apps_git / "test"
        repo_dir.mkdir(parents=True)

        await coresys.store.data.update()

    assert f"No repository information exists at {repo_dir.as_posix()}" in caplog.text


async def test_repository_file_error(
    coresys: CoreSys, tmp_supervisor_data: Path, caplog: pytest.LogCaptureFixture
):
    """Test repository file is missing."""
    with patch.object(
        CoreConfig,
        "path_apps_git",
        new=PropertyMock(return_value=tmp_supervisor_data / "addons" / "git"),
    ):
        repo_dir = coresys.config.path_apps_git / "test"
        repo_dir.mkdir(parents=True)

        repo_file = repo_dir / "repository.json"

        with repo_file.open("w") as file:
            file.write("not json")

        await coresys.store.data.update()
        assert (
            f"Can't read repository information from {repo_file.as_posix()}"
            in caplog.text
        )

        await coresys.run_in_executor(write_json_file, repo_file, {"invalid": "bad"})
        await coresys.store.data.update()
        assert f"Repository parse error {repo_dir.as_posix()}" in caplog.text


async def test_store_data_changes_during_update(coresys: CoreSys, install_app_ssh: App):
    """Test store data changing for an app during an update does not cause errors."""
    event = asyncio.Event()
    coresys.store.data.apps["local_ssh"]["image"] = "test_image"
    coresys.store.data.apps["local_ssh"]["version"] = AwesomeVersion("1.1.1")

    async def simulate_update():
        async def mock_update(_, version, image, *args, **kwargs):
            assert version == AwesomeVersion("1.1.1")
            assert image == "test_image"
            await event.wait()

        with (
            patch.object(DockerApp, "update", new=mock_update),
            patch.object(DockerAPI, "cleanup_old_images") as cleanup,
        ):
            await coresys.apps.update("local_ssh")
            cleanup.assert_called_once_with(
                "test_image",
                AwesomeVersion("1.1.1"),
                {"local/amd64-addon-ssh"},
                keep_images=set(),
            )

    update_task = coresys.create_task(simulate_update())
    await asyncio.sleep(0)

    with patch.object(RepositoryLocal, "update", return_value=True):
        await coresys.store.reload()

    assert "image" not in coresys.store.data.apps["local_ssh"]
    assert coresys.store.data.apps["local_ssh"]["version"] == AwesomeVersion("9.2.1")

    event.set()
    await update_task

    assert install_app_ssh.image == "test_image"
    assert install_app_ssh.version == AwesomeVersion("1.1.1")


async def test_watchdog_runs_during_update(
    coresys: CoreSys, install_app_ssh: App, container: DockerContainer
):
    """Test watchdog running during a long update."""
    container.show.return_value["State"]["Status"] = "running"
    container.show.return_value["State"]["Running"] = True
    install_app_ssh.watchdog = True
    coresys.store.data.apps["local_ssh"]["image"] = "test_image"
    coresys.store.data.apps["local_ssh"]["version"] = AwesomeVersion("1.1.1")
    await install_app_ssh.load()

    # Simulate stop firing the docker event for stopped container like it normally would
    async def mock_stop(*args, **kwargs):
        container.show.return_value["State"]["Status"] = "stopped"
        container.show.return_value["State"]["Running"] = False
        coresys.bus.fire_event(
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
            DockerContainerStateEvent(
                name=f"addon_{TEST_ADDON_SLUG}",
                state=ContainerState.STOPPED,
                id="abc123",
                time=1,
            ),
        )

    # Mock update to just wait and let other tasks run as if it is long running
    async def mock_update(*args, **kwargs):
        await asyncio.sleep(0)

    # Start should be called exactly once by update itself. Restart should never be called
    with (
        patch.object(DockerApp, "stop", new=mock_stop),
        patch.object(DockerApp, "update", new=mock_update),
        patch.object(App, "start") as start,
        patch.object(App, "restart") as restart,
    ):
        await coresys.apps.update("local_ssh")
        await asyncio.sleep(0)
        start.assert_called_once()
        restart.assert_not_called()


async def test_shared_image_kept_on_uninstall(
    coresys: CoreSys, install_app_example: App
):
    """Test if two apps share an image it is not removed on uninstall."""
    # Clone example to a new mock copy so two share an image
    store_data = deepcopy(coresys.apps.store["local_example"].data)
    store = AppStore(coresys, "local_example2", store_data)
    coresys.apps.store["local_example2"] = store
    await coresys.apps.data.install(store)
    # pylint: disable-next=protected-access
    coresys.apps.data._data = coresys.apps.data._schema(coresys.apps.data._data)

    example_2 = App(coresys, store.slug)
    coresys.apps.local[example_2.slug] = example_2

    image = f"{install_app_example.image}:{install_app_example.version}"
    latest = f"{install_app_example.image}:latest"

    await coresys.apps.uninstall("local_example2")
    coresys.docker.images.delete.assert_not_called()
    assert not coresys.apps.get("local_example2", local_only=True)

    await coresys.apps.uninstall("local_example")
    assert coresys.docker.images.delete.call_count == 2
    assert coresys.docker.images.delete.call_args_list[0] == call(latest, force=True)
    assert coresys.docker.images.delete.call_args_list[1] == call(image, force=True)
    assert not coresys.apps.get("local_example", local_only=True)


@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
async def test_update_reloads_ingress_tokens(
    coresys: CoreSys,
    install_app_ssh: App,
    container: DockerContainer,
):
    """Test ingress tokens are reloaded when app gains ingress on update."""
    container.show.return_value["State"]["Status"] = "stopped"
    container.show.return_value["State"]["Running"] = False
    install_app_ssh.path_data.mkdir()

    # Simulate app was installed without ingress
    coresys.apps.data.system[install_app_ssh.slug][ATTR_INGRESS] = False
    await install_app_ssh.load()
    await coresys.ingress.reload()
    assert install_app_ssh.ingress_token not in coresys.ingress.tokens

    # Update store to version with ingress enabled
    with patch(
        "supervisor.store.data.read_json_or_yaml_file",
        return_value=load_json_fixture("addon-config-add-image.json"),
    ):
        await coresys.store.data.update()

    assert install_app_ssh.need_update is True

    with (
        patch.object(DockerInterface, "install"),
        patch.object(DockerApp, "is_running", return_value=False),
    ):
        await coresys.apps.update(TEST_ADDON_SLUG)

    # Ingress token should now be registered
    assert install_app_ssh.with_ingress is True
    assert install_app_ssh.ingress_token in coresys.ingress.tokens


@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
async def test_rebuild_reloads_ingress_tokens(
    coresys: CoreSys,
    install_app_ssh: App,
    container: DockerContainer,
):
    """Test ingress tokens are reloaded when app gains ingress on rebuild."""
    container.show.return_value["State"]["Status"] = "stopped"
    container.show.return_value["State"]["Running"] = False
    install_app_ssh.path_data.mkdir()

    # Simulate app was installed without ingress
    coresys.apps.data.system[install_app_ssh.slug][ATTR_INGRESS] = False
    await install_app_ssh.load()
    await coresys.ingress.reload()
    assert install_app_ssh.ingress_token not in coresys.ingress.tokens

    # Re-enable ingress in system data (rebuild pulls fresh store data)
    coresys.apps.data.system[install_app_ssh.slug][ATTR_INGRESS] = True

    with (
        patch.object(DockerApp, "_build"),
        patch.object(DockerApp, "is_running", return_value=False),
        patch.object(App, "need_build", new=PropertyMock(return_value=True)),
    ):
        await coresys.apps.rebuild(TEST_ADDON_SLUG)

    # Ingress token should now be registered
    assert install_app_ssh.with_ingress is True
    assert install_app_ssh.ingress_token in coresys.ingress.tokens


async def test_shared_image_kept_on_update(
    coresys: CoreSys, install_app_example_image: App, docker: DockerAPI
):
    """Test if two apps share an image it is not removed on update."""
    # Clone example to a new mock copy so two share an image
    # But modify version in store so Supervisor sees an update
    curr_store_data = deepcopy(coresys.store.data.apps["local_example_image"])
    curr_store = AppStore(coresys, "local_example2", curr_store_data)
    install_app_example_image.data_store["version"] = "1.3.0"
    new_store_data = deepcopy(coresys.store.data.apps["local_example_image"])
    new_store = AppStore(coresys, "local_example2", new_store_data)

    coresys.store.data.apps["local_example2"] = new_store_data
    coresys.apps.store["local_example2"] = new_store
    await coresys.apps.data.install(curr_store)
    # pylint: disable-next=protected-access
    coresys.apps.data._data = coresys.apps.data._schema(coresys.apps.data._data)

    example_2 = App(coresys, curr_store.slug)
    coresys.apps.local[example_2.slug] = example_2

    assert example_2.version == "1.2.0"
    assert install_app_example_image.version == "1.2.0"

    image_new = {"Id": "image_new", "RepoTags": ["image_new:latest"]}
    image_old = {"Id": "image_old", "RepoTags": ["image_old:latest"]}
    docker.images.inspect.side_effect = [image_new, image_old]
    docker.images.list.return_value = [image_new, image_old]

    with patch.object(DockerAPI, "pull_image", return_value=image_new):
        await coresys.apps.update("local_example2")
        docker.images.delete.assert_not_called()
        assert example_2.version == "1.3.0"

        docker.images.inspect.side_effect = [image_new]
        await coresys.apps.update("local_example_image")
        docker.images.delete.assert_called_once_with("image_old", force=True)
        assert install_app_example_image.version == "1.3.0"
