"""Test addon manager."""

import asyncio
from collections.abc import AsyncGenerator, Generator
from copy import deepcopy
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, PropertyMock, patch

from awesomeversion import AwesomeVersion
import pytest

from supervisor.addons.addon import Addon
from supervisor.arch import CpuArch
from supervisor.config import CoreConfig
from supervisor.const import AddonBoot, AddonStartup, AddonState, BusEvent
from supervisor.coresys import CoreSys
from supervisor.docker.addon import DockerAddon
from supervisor.docker.const import ContainerState
from supervisor.docker.interface import DockerInterface
from supervisor.docker.manager import DockerAPI
from supervisor.docker.monitor import DockerContainerStateEvent
from supervisor.exceptions import (
    AddonConfigurationError,
    AddonsError,
    DockerAPIError,
    DockerNotFound,
)
from supervisor.plugins.dns import PluginDns
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue, Suggestion
from supervisor.store.addon import AddonStore
from supervisor.store.repository import Repository
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
        patch.object(CpuArch, "supported", new=PropertyMock(return_value=["amd64"])),
    ):
        yield


@pytest.fixture(autouse=True)
async def fixture_remove_wait_boot(coresys: CoreSys) -> AsyncGenerator[None]:
    """Remove default wait boot time for tests."""
    coresys.config.wait_boot = 0


@pytest.fixture(name="install_addon_example_image")
async def fixture_install_addon_example_image(
    coresys: CoreSys, repository
) -> Generator[Addon]:
    """Install local_example add-on with image."""
    store = coresys.addons.store["local_example_image"]
    await coresys.addons.data.install(store)
    # pylint: disable-next=protected-access
    coresys.addons.data._data = coresys.addons.data._schema(coresys.addons.data._data)

    addon = Addon(coresys, store.slug)
    coresys.addons.local[addon.slug] = addon
    yield addon


async def test_image_added_removed_on_update(
    coresys: CoreSys, install_addon_ssh: Addon
):
    """Test image added or removed from addon config on update."""
    assert install_addon_ssh.need_update is False
    with patch(
        "supervisor.store.data.read_json_or_yaml_file",
        return_value=load_json_fixture("addon-config-add-image.json"),
    ):
        await coresys.store.data.update()

    assert install_addon_ssh.need_update is True
    assert install_addon_ssh.image == "local/amd64-addon-ssh"
    assert coresys.addons.store.get(TEST_ADDON_SLUG).image == "test/amd64-my-ssh-addon"

    with (
        patch.object(DockerInterface, "install") as install,
        patch.object(DockerAddon, "_build") as build,
    ):
        await coresys.addons.update(TEST_ADDON_SLUG)
        build.assert_not_called()
        install.assert_called_once_with(
            AwesomeVersion("10.0.0"), "test/amd64-my-ssh-addon", False, "amd64"
        )

    assert install_addon_ssh.need_update is False
    with patch(
        "supervisor.store.data.read_json_or_yaml_file",
        return_value=load_json_fixture("addon-config-remove-image.json"),
    ):
        await coresys.store.data.update()

    assert install_addon_ssh.need_update is True
    assert install_addon_ssh.image == "test/amd64-my-ssh-addon"
    assert coresys.addons.store.get(TEST_ADDON_SLUG).image == "local/amd64-addon-ssh"

    with (
        patch.object(DockerInterface, "install") as install,
        patch.object(DockerAddon, "_build") as build,
    ):
        await coresys.addons.update(TEST_ADDON_SLUG)
        build.assert_called_once_with(AwesomeVersion("11.0.0"), "local/amd64-addon-ssh")
        install.assert_not_called()


@pytest.mark.parametrize("err", [DockerAPIError, DockerNotFound])
async def test_addon_boot_system_error(
    coresys: CoreSys, install_addon_ssh: Addon, capture_exception: Mock, err
):
    """Test system errors during addon boot."""
    install_addon_ssh.boot = AddonBoot.AUTO
    assert coresys.resolution.issues == []
    assert coresys.resolution.suggestions == []
    with (
        patch.object(Addon, "write_options"),
        patch.object(DockerAddon, "run", side_effect=err),
    ):
        await coresys.addons.boot(AddonStartup.APPLICATION)

    capture_exception.assert_not_called()
    assert coresys.resolution.issues == [BOOT_FAIL_ISSUE]
    assert coresys.resolution.suggestions == BOOT_FAIL_SUGGESTIONS


async def test_addon_boot_user_error(
    coresys: CoreSys, install_addon_ssh: Addon, capture_exception: Mock
):
    """Test user error during addon boot."""
    install_addon_ssh.boot = AddonBoot.AUTO
    with patch.object(Addon, "write_options", side_effect=AddonConfigurationError):
        await coresys.addons.boot(AddonStartup.APPLICATION)

    capture_exception.assert_not_called()
    assert coresys.resolution.issues == [BOOT_FAIL_ISSUE]
    assert coresys.resolution.suggestions == BOOT_FAIL_SUGGESTIONS


async def test_addon_boot_other_error(
    coresys: CoreSys, install_addon_ssh: Addon, capture_exception: Mock
):
    """Test other errors captured during addon boot."""
    install_addon_ssh.boot = AddonBoot.AUTO
    err = OSError()
    with (
        patch.object(Addon, "write_options"),
        patch.object(DockerAddon, "run", side_effect=err),
    ):
        await coresys.addons.boot(AddonStartup.APPLICATION)

    capture_exception.assert_called_once_with(err)
    assert coresys.resolution.issues == [BOOT_FAIL_ISSUE]
    assert coresys.resolution.suggestions == BOOT_FAIL_SUGGESTIONS


async def test_addon_shutdown_error(
    coresys: CoreSys, install_addon_ssh: Addon, capture_exception: Mock
):
    """Test errors captured during addon shutdown."""
    install_addon_ssh.state = AddonState.STARTED
    with patch.object(DockerAddon, "stop", side_effect=DockerNotFound()):
        await coresys.addons.shutdown(AddonStartup.APPLICATION)

    assert install_addon_ssh.state == AddonState.ERROR
    capture_exception.assert_called_once()
    assert check_exception_chain(
        capture_exception.call_args[0][0], (AddonsError, DockerNotFound)
    )


async def test_addon_uninstall_removes_discovery(
    coresys: CoreSys, install_addon_ssh: Addon, websession: MagicMock
):
    """Test discovery messages removed when addon uninstalled."""
    assert coresys.discovery.list_messages == []

    message = await coresys.discovery.send(
        install_addon_ssh, "mqtt", {"host": "localhost", "port": 1883}
    )
    assert message.addon == TEST_ADDON_SLUG
    assert message.service == "mqtt"
    assert coresys.discovery.list_messages == [message]

    coresys.homeassistant.api.ensure_access_token = AsyncMock()

    await coresys.addons.uninstall(TEST_ADDON_SLUG)
    await asyncio.sleep(0)
    coresys.websession.delete.assert_called_once()
    assert (
        coresys.websession.delete.call_args.args[0]
        == f"http://172.30.32.1:8123/api/hassio_push/discovery/{message.uuid}"
    )
    assert coresys.websession.delete.call_args.kwargs["json"] == {
        "addon": TEST_ADDON_SLUG,
        "service": "mqtt",
        "uuid": message.uuid,
    }

    assert coresys.addons.installed == []
    assert coresys.discovery.list_messages == []


async def test_load(
    coresys: CoreSys, install_addon_ssh: Addon, caplog: pytest.LogCaptureFixture
):
    """Test addon manager load."""
    caplog.clear()

    with (
        patch.object(DockerInterface, "attach") as attach,
        patch.object(PluginDns, "write_hosts") as write_hosts,
    ):
        await coresys.addons.load()

        attach.assert_called_once_with(version=AwesomeVersion("9.2.1"))
        write_hosts.assert_called_once()

    assert "Found 1 installed add-ons" in caplog.text


async def test_boot_waits_for_addons(
    coresys: CoreSys,
    install_addon_ssh: Addon,
    container,
    tmp_supervisor_data,
    path_extern,
):
    """Test addon manager boot waits for addons."""
    install_addon_ssh.path_data.mkdir()
    await install_addon_ssh.load()
    await asyncio.sleep(0)
    assert install_addon_ssh.state == AddonState.STOPPED

    addon_state: AddonState | None = None

    async def fire_container_event(*args, **kwargs):
        nonlocal addon_state

        addon_state = install_addon_ssh.state
        coresys.bus.fire_event(
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
            DockerContainerStateEvent(
                name=f"addon_{TEST_ADDON_SLUG}",
                state=ContainerState.RUNNING,
                id="abc123",
                time=1,
            ),
        )

    with patch.object(DockerAddon, "run", new=fire_container_event):
        await coresys.addons.boot(AddonStartup.APPLICATION)

    assert addon_state == AddonState.STOPPED
    assert install_addon_ssh.state == AddonState.STARTED


@pytest.mark.parametrize("status", ["running", "stopped"])
async def test_update(
    coresys: CoreSys,
    install_addon_ssh: Addon,
    container: MagicMock,
    status: str,
    tmp_supervisor_data,
    path_extern,
):
    """Test addon update."""
    container.status = status
    install_addon_ssh.path_data.mkdir()
    await install_addon_ssh.load()
    with patch(
        "supervisor.store.data.read_json_or_yaml_file",
        return_value=load_json_fixture("addon-config-add-image.json"),
    ):
        await coresys.store.data.update()

    assert install_addon_ssh.need_update is True

    with (
        patch.object(DockerInterface, "install"),
        patch.object(DockerAddon, "is_running", return_value=False),
    ):
        start_task = await coresys.addons.update(TEST_ADDON_SLUG)

    assert bool(start_task) is (status == "running")


@pytest.mark.parametrize("status", ["running", "stopped"])
async def test_rebuild(
    coresys: CoreSys,
    install_addon_ssh: Addon,
    container: MagicMock,
    status: str,
    tmp_supervisor_data,
    path_extern,
):
    """Test addon rebuild."""
    container.status = status
    install_addon_ssh.path_data.mkdir()
    await install_addon_ssh.load()

    with (
        patch.object(DockerAddon, "_build"),
        patch.object(DockerAddon, "is_running", return_value=False),
        patch.object(Addon, "need_build", new=PropertyMock(return_value=True)),
    ):
        start_task = await coresys.addons.rebuild(TEST_ADDON_SLUG)

    assert bool(start_task) is (status == "running")


async def test_start_wait_cancel_on_uninstall(
    coresys: CoreSys,
    install_addon_ssh: Addon,
    container: MagicMock,
    caplog: pytest.LogCaptureFixture,
    tmp_supervisor_data,
    path_extern,
) -> None:
    """Test the addon wait task is cancelled when addon is uninstalled."""
    install_addon_ssh.path_data.mkdir()
    container.attrs["Config"] = {"Healthcheck": "exists"}
    await install_addon_ssh.load()
    await asyncio.sleep(0)
    assert install_addon_ssh.state == AddonState.STOPPED

    start_task = await install_addon_ssh.start()
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
    assert install_addon_ssh.state == AddonState.STARTUP

    caplog.clear()
    await coresys.addons.uninstall(TEST_ADDON_SLUG)
    await asyncio.sleep(0.01)
    assert start_task.done()
    assert "Wait for addon startup task cancelled" in caplog.text


async def test_repository_file_missing(
    coresys: CoreSys, tmp_supervisor_data: Path, caplog: pytest.LogCaptureFixture
):
    """Test repository file is missing."""
    with patch.object(
        CoreConfig,
        "path_addons_git",
        new=PropertyMock(return_value=tmp_supervisor_data / "addons" / "git"),
    ):
        repo_dir = coresys.config.path_addons_git / "test"
        repo_dir.mkdir(parents=True)

        await coresys.store.data.update()

    assert f"No repository information exists at {repo_dir.as_posix()}" in caplog.text


async def test_repository_file_error(
    coresys: CoreSys, tmp_supervisor_data: Path, caplog: pytest.LogCaptureFixture
):
    """Test repository file is missing."""
    with patch.object(
        CoreConfig,
        "path_addons_git",
        new=PropertyMock(return_value=tmp_supervisor_data / "addons" / "git"),
    ):
        repo_dir = coresys.config.path_addons_git / "test"
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


async def test_store_data_changes_during_update(
    coresys: CoreSys, install_addon_ssh: Addon
):
    """Test store data changing for an addon during an update does not cause errors."""
    event = asyncio.Event()
    coresys.store.data.addons["local_ssh"]["image"] = "test_image"
    coresys.store.data.addons["local_ssh"]["version"] = AwesomeVersion("1.1.1")

    async def simulate_update():
        async def mock_update(_, version, image, *args, **kwargs):
            assert version == AwesomeVersion("1.1.1")
            assert image == "test_image"
            await event.wait()

        with (
            patch.object(DockerAddon, "update", new=mock_update),
            patch.object(DockerAPI, "cleanup_old_images") as cleanup,
        ):
            await coresys.addons.update("local_ssh")
            cleanup.assert_called_once_with(
                "test_image",
                AwesomeVersion("1.1.1"),
                {"local/amd64-addon-ssh"},
                keep_images=set(),
            )

    update_task = coresys.create_task(simulate_update())
    await asyncio.sleep(0)

    with patch.object(Repository, "update", return_value=True):
        await coresys.store.reload()

    assert "image" not in coresys.store.data.addons["local_ssh"]
    assert coresys.store.data.addons["local_ssh"]["version"] == AwesomeVersion("9.2.1")

    event.set()
    await update_task

    assert install_addon_ssh.image == "test_image"
    assert install_addon_ssh.version == AwesomeVersion("1.1.1")


async def test_watchdog_runs_during_update(
    coresys: CoreSys, install_addon_ssh: Addon, container: MagicMock
):
    """Test watchdog running during a long update."""
    container.status = "running"
    install_addon_ssh.watchdog = True
    coresys.store.data.addons["local_ssh"]["image"] = "test_image"
    coresys.store.data.addons["local_ssh"]["version"] = AwesomeVersion("1.1.1")
    await install_addon_ssh.load()

    # Simulate stop firing the docker event for stopped container like it normally would
    async def mock_stop(*args, **kwargs):
        container.status = "stopped"
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
        patch.object(DockerAddon, "stop", new=mock_stop),
        patch.object(DockerAddon, "update", new=mock_update),
        patch.object(Addon, "start") as start,
        patch.object(Addon, "restart") as restart,
    ):
        await coresys.addons.update("local_ssh")
        await asyncio.sleep(0)
        start.assert_called_once()
        restart.assert_not_called()


async def test_shared_image_kept_on_uninstall(
    coresys: CoreSys, install_addon_example: Addon
):
    """Test if two addons share an image it is not removed on uninstall."""
    # Clone example to a new mock copy so two share an image
    store_data = deepcopy(coresys.addons.store["local_example"].data)
    store = AddonStore(coresys, "local_example2", store_data)
    coresys.addons.store["local_example2"] = store
    await coresys.addons.data.install(store)
    # pylint: disable-next=protected-access
    coresys.addons.data._data = coresys.addons.data._schema(coresys.addons.data._data)

    example_2 = Addon(coresys, store.slug)
    coresys.addons.local[example_2.slug] = example_2

    image = f"{install_addon_example.image}:{install_addon_example.version}"
    latest = f"{install_addon_example.image}:latest"

    await coresys.addons.uninstall("local_example2")
    coresys.docker.images.remove.assert_not_called()
    assert not coresys.addons.get("local_example2", local_only=True)

    await coresys.addons.uninstall("local_example")
    assert coresys.docker.images.remove.call_count == 2
    assert coresys.docker.images.remove.call_args_list[0].kwargs == {
        "image": latest,
        "force": True,
    }
    assert coresys.docker.images.remove.call_args_list[1].kwargs == {
        "image": image,
        "force": True,
    }
    assert not coresys.addons.get("local_example", local_only=True)


async def test_shared_image_kept_on_update(
    coresys: CoreSys, install_addon_example_image: Addon, docker: DockerAPI
):
    """Test if two addons share an image it is not removed on update."""
    # Clone example to a new mock copy so two share an image
    # But modify version in store so Supervisor sees an update
    curr_store_data = deepcopy(coresys.store.data.addons["local_example_image"])
    curr_store = AddonStore(coresys, "local_example2", curr_store_data)
    install_addon_example_image.data_store["version"] = "1.3.0"
    new_store_data = deepcopy(coresys.store.data.addons["local_example_image"])
    new_store = AddonStore(coresys, "local_example2", new_store_data)

    coresys.store.data.addons["local_example2"] = new_store_data
    coresys.addons.store["local_example2"] = new_store
    await coresys.addons.data.install(curr_store)
    # pylint: disable-next=protected-access
    coresys.addons.data._data = coresys.addons.data._schema(coresys.addons.data._data)

    example_2 = Addon(coresys, curr_store.slug)
    coresys.addons.local[example_2.slug] = example_2

    assert example_2.version == "1.2.0"
    assert install_addon_example_image.version == "1.2.0"

    image_new = MagicMock()
    image_new.id = "image_new"
    image_old = MagicMock()
    image_old.id = "image_old"
    docker.images.get.side_effect = [image_new, image_old]
    docker.images.list.return_value = [image_new, image_old]

    await coresys.addons.update("local_example2")
    docker.images.remove.assert_not_called()
    assert example_2.version == "1.3.0"

    docker.images.get.side_effect = [image_new]
    await coresys.addons.update("local_example_image")
    docker.images.remove.assert_called_once_with("image_old", force=True)
    assert install_addon_example_image.version == "1.3.0"
