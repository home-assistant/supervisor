"""Test Home Assistant core."""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, PropertyMock, patch

from awesomeversion import AwesomeVersion
from docker.errors import APIError, DockerException, ImageNotFound, NotFound
import pytest
from time_machine import travel

from supervisor.const import CpuArch
from supervisor.coresys import CoreSys
from supervisor.docker.homeassistant import DockerHomeAssistant
from supervisor.docker.interface import DockerInterface
from supervisor.docker.manager import DockerAPI
from supervisor.exceptions import (
    AudioUpdateError,
    DockerError,
    HomeAssistantCrashError,
    HomeAssistantError,
    HomeAssistantJobError,
)
from supervisor.homeassistant.api import APIState
from supervisor.homeassistant.core import HomeAssistantCore
from supervisor.homeassistant.module import HomeAssistant
from supervisor.updater import Updater


async def test_update_fails_if_out_of_date(coresys: CoreSys):
    """Test update of Home Assistant fails when supervisor or plugin is out of date."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    with (
        patch.object(
            type(coresys.supervisor), "need_update", new=PropertyMock(return_value=True)
        ),
        pytest.raises(HomeAssistantJobError),
    ):
        await coresys.homeassistant.core.update()

    with (
        patch.object(
            type(coresys.plugins.audio),
            "need_update",
            new=PropertyMock(return_value=True),
        ),
        patch.object(
            type(coresys.plugins.audio), "update", side_effect=AudioUpdateError
        ),
        pytest.raises(HomeAssistantJobError),
    ):
        await coresys.homeassistant.core.update()


async def test_install_landingpage_docker_error(
    coresys: CoreSys, capture_exception: Mock, caplog: pytest.LogCaptureFixture
):
    """Test install landing page fails due to docker error."""
    coresys.security.force = True
    with (
        patch.object(DockerHomeAssistant, "attach", side_effect=DockerError),
        patch.object(
            Updater,
            "image_homeassistant",
            new=PropertyMock(return_value="homeassistant"),
        ),
        patch.object(
            DockerInterface, "arch", new=PropertyMock(return_value=CpuArch.AMD64)
        ),
        patch("supervisor.homeassistant.core.asyncio.sleep") as sleep,
    ):
        coresys.docker.images.pull.side_effect = [APIError("fail"), MagicMock()]
        await coresys.homeassistant.core.install_landingpage()
        sleep.assert_awaited_once_with(30)

    assert "Failed to install landingpage, retrying after 30sec" in caplog.text
    capture_exception.assert_not_called()


async def test_install_landingpage_other_error(
    coresys: CoreSys, capture_exception: Mock, caplog: pytest.LogCaptureFixture
):
    """Test install landing page fails due to other error."""
    coresys.docker.images.pull.side_effect = [(err := OSError()), MagicMock()]

    with (
        patch.object(DockerHomeAssistant, "attach", side_effect=DockerError),
        patch.object(
            Updater,
            "image_homeassistant",
            new=PropertyMock(return_value="homeassistant"),
        ),
        patch.object(
            DockerInterface, "arch", new=PropertyMock(return_value=CpuArch.AMD64)
        ),
        patch("supervisor.homeassistant.core.asyncio.sleep") as sleep,
    ):
        await coresys.homeassistant.core.install_landingpage()
        sleep.assert_awaited_once_with(30)

    assert "Failed to install landingpage, retrying after 30sec" in caplog.text
    capture_exception.assert_called_once_with(err)


async def test_install_docker_error(
    coresys: CoreSys, capture_exception: Mock, caplog: pytest.LogCaptureFixture
):
    """Test install fails due to docker error."""
    coresys.security.force = True
    with (
        patch.object(HomeAssistantCore, "start"),
        patch.object(DockerHomeAssistant, "cleanup"),
        patch.object(
            Updater,
            "image_homeassistant",
            new=PropertyMock(return_value="homeassistant"),
        ),
        patch.object(
            Updater, "version_homeassistant", new=PropertyMock(return_value="2022.7.3")
        ),
        patch.object(
            DockerInterface, "arch", new=PropertyMock(return_value=CpuArch.AMD64)
        ),
        patch("supervisor.homeassistant.core.asyncio.sleep") as sleep,
    ):
        coresys.docker.images.pull.side_effect = [APIError("fail"), MagicMock()]
        await coresys.homeassistant.core.install()
        sleep.assert_awaited_once_with(30)

    assert "Error on Home Assistant installation. Retrying in 30sec" in caplog.text
    capture_exception.assert_not_called()


async def test_install_other_error(
    coresys: CoreSys, capture_exception: Mock, caplog: pytest.LogCaptureFixture
):
    """Test install fails due to other error."""
    coresys.docker.images.pull.side_effect = [(err := OSError()), MagicMock()]

    with (
        patch.object(HomeAssistantCore, "start"),
        patch.object(DockerHomeAssistant, "cleanup"),
        patch.object(
            Updater,
            "image_homeassistant",
            new=PropertyMock(return_value="homeassistant"),
        ),
        patch.object(
            Updater, "version_homeassistant", new=PropertyMock(return_value="2022.7.3")
        ),
        patch.object(
            DockerInterface, "arch", new=PropertyMock(return_value=CpuArch.AMD64)
        ),
        patch("supervisor.homeassistant.core.asyncio.sleep") as sleep,
    ):
        await coresys.homeassistant.core.install()
        sleep.assert_awaited_once_with(30)

    assert "Error on Home Assistant installation. Retrying in 30sec" in caplog.text
    capture_exception.assert_called_once_with(err)


@pytest.mark.parametrize(
    "container_exists,image_exists", [(False, True), (True, False), (True, True)]
)
async def test_start(
    coresys: CoreSys, container_exists: bool, image_exists: bool, path_extern
):
    """Test starting Home Assistant."""
    if image_exists:
        coresys.docker.images.get.return_value.id = "123"
    else:
        coresys.docker.images.get.side_effect = ImageNotFound("missing")

    if container_exists:
        coresys.docker.containers.get.return_value.image.id = "123"
    else:
        coresys.docker.containers.get.side_effect = NotFound("missing")

    with (
        patch.object(
            HomeAssistant,
            "version",
            new=PropertyMock(return_value=AwesomeVersion("2023.7.0")),
        ),
        patch.object(DockerAPI, "run") as run,
        patch.object(HomeAssistantCore, "_block_till_run") as block_till_run,
    ):
        await coresys.homeassistant.core.start()

        block_till_run.assert_called_once()
        run.assert_called_once()
        assert (
            run.call_args.args[0] == "ghcr.io/home-assistant/qemux86-64-homeassistant"
        )
        assert run.call_args.kwargs["tag"] == AwesomeVersion("2023.7.0")
        assert run.call_args.kwargs["name"] == "homeassistant"
        assert run.call_args.kwargs["hostname"] == "homeassistant"

    coresys.docker.containers.get.return_value.stop.assert_not_called()
    if container_exists:
        coresys.docker.containers.get.return_value.remove.assert_called_once_with(
            force=True
        )
    else:
        coresys.docker.containers.get.return_value.remove.assert_not_called()


async def test_start_existing_container(coresys: CoreSys, path_extern):
    """Test starting Home Assistant when container exists and is viable."""
    coresys.docker.images.get.return_value.id = "123"
    coresys.docker.containers.get.return_value.image.id = "123"
    coresys.docker.containers.get.return_value.status = "exited"

    with (
        patch.object(
            HomeAssistant,
            "version",
            new=PropertyMock(return_value=AwesomeVersion("2023.7.0")),
        ),
        patch.object(HomeAssistantCore, "_block_till_run") as block_till_run,
    ):
        await coresys.homeassistant.core.start()
        block_till_run.assert_called_once()

    coresys.docker.containers.get.return_value.start.assert_called_once()
    coresys.docker.containers.get.return_value.stop.assert_not_called()
    coresys.docker.containers.get.return_value.remove.assert_not_called()
    coresys.docker.containers.get.return_value.run.assert_not_called()


@pytest.mark.parametrize("exists", [True, False])
async def test_stop(coresys: CoreSys, exists: bool):
    """Test stoppping Home Assistant."""
    if exists:
        coresys.docker.containers.get.return_value.status = "running"
    else:
        coresys.docker.containers.get.side_effect = NotFound("missing")

    await coresys.homeassistant.core.stop()

    coresys.docker.containers.get.return_value.remove.assert_not_called()
    if exists:
        coresys.docker.containers.get.return_value.stop.assert_called_once_with(
            timeout=260
        )
    else:
        coresys.docker.containers.get.return_value.stop.assert_not_called()


async def test_restart(coresys: CoreSys):
    """Test restarting Home Assistant."""
    with patch.object(HomeAssistantCore, "_block_till_run") as block_till_run:
        await coresys.homeassistant.core.restart()
        block_till_run.assert_called_once()

    coresys.docker.containers.get.return_value.restart.assert_called_once_with(
        timeout=260
    )
    coresys.docker.containers.get.return_value.stop.assert_not_called()


@pytest.mark.parametrize("get_error", [NotFound("missing"), DockerException(), None])
async def test_restart_failures(coresys: CoreSys, get_error: DockerException | None):
    """Test restart fails when container missing or can't be restarted."""
    coresys.docker.containers.get.return_value.restart.side_effect = DockerException()
    if get_error:
        coresys.docker.containers.get.side_effect = get_error

    with pytest.raises(HomeAssistantError):
        await coresys.homeassistant.core.restart()


@pytest.mark.parametrize(
    "get_error,status",
    [
        (NotFound("missing"), ""),
        (DockerException(), ""),
        (None, "stopped"),
        (None, "running"),
    ],
)
async def test_stats_failures(
    coresys: CoreSys, get_error: DockerException | None, status: str
):
    """Test errors when getting stats."""
    coresys.docker.containers.get.return_value.status = status
    coresys.docker.containers.get.return_value.stats.side_effect = DockerException()
    if get_error:
        coresys.docker.containers.get.side_effect = get_error

    with pytest.raises(HomeAssistantError):
        await coresys.homeassistant.core.stats()


async def test_api_check_timeout(
    coresys: CoreSys, container: MagicMock, caplog: pytest.LogCaptureFixture
):
    """Test attempts to contact the API timeout."""
    container.status = "stopped"
    coresys.homeassistant.version = AwesomeVersion("2023.9.0")
    coresys.homeassistant.api.get_api_state.return_value = None

    async def mock_instance_start(*_):
        container.status = "running"

    with (
        patch.object(DockerHomeAssistant, "start", new=mock_instance_start),
        patch.object(DockerAPI, "container_is_initialized", return_value=True),
        travel(datetime(2023, 10, 2, 0, 0, 0), tick=False) as traveller,
    ):

        async def mock_sleep(*args):
            traveller.shift(timedelta(minutes=1))

        with (
            patch("supervisor.homeassistant.core.asyncio.sleep", new=mock_sleep),
            pytest.raises(HomeAssistantCrashError),
        ):
            await coresys.homeassistant.core.start()

    assert coresys.homeassistant.api.get_api_state.call_count == 3
    assert (
        "No Home Assistant Core response, assuming a fatal startup error" in caplog.text
    )


async def test_api_check_success(
    coresys: CoreSys, container: MagicMock, caplog: pytest.LogCaptureFixture
):
    """Test attempts to contact the API timeout."""
    container.status = "stopped"
    coresys.homeassistant.version = AwesomeVersion("2023.9.0")

    async def mock_instance_start(*_):
        container.status = "running"

    with (
        patch.object(DockerHomeAssistant, "start", new=mock_instance_start),
        patch.object(DockerAPI, "container_is_initialized", return_value=True),
        travel(datetime(2023, 10, 2, 0, 0, 0), tick=False) as traveller,
    ):

        async def mock_sleep(*args):
            traveller.shift(timedelta(minutes=1))

        with patch("supervisor.homeassistant.core.asyncio.sleep", new=mock_sleep):
            await coresys.homeassistant.core.start()

    assert coresys.homeassistant.api.get_api_state.call_count == 1
    assert "Detect a running Home Assistant instance" in caplog.text


async def test_api_check_database_migration(
    coresys: CoreSys, container: MagicMock, caplog: pytest.LogCaptureFixture
):
    """Test attempts to contact the API timeout."""
    calls = []

    def mock_api_state(*args):
        calls.append(None)
        if len(calls) > 50:
            return APIState("RUNNING", False)
        else:
            return APIState("NOT_RUNNING", True)

    container.status = "stopped"
    coresys.homeassistant.version = AwesomeVersion("2023.9.0")
    coresys.homeassistant.api.get_api_state.side_effect = mock_api_state

    async def mock_instance_start(*_):
        container.status = "running"

    with (
        patch.object(DockerHomeAssistant, "start", new=mock_instance_start),
        patch.object(DockerAPI, "container_is_initialized", return_value=True),
        travel(datetime(2023, 10, 2, 0, 0, 0), tick=False) as traveller,
    ):

        async def mock_sleep(*args):
            traveller.shift(timedelta(minutes=1))

        with patch("supervisor.homeassistant.core.asyncio.sleep", new=mock_sleep):
            await coresys.homeassistant.core.start()

    assert coresys.homeassistant.api.get_api_state.call_count == 51
    assert "Detect a running Home Assistant instance" in caplog.text


async def test_core_loads_wrong_image_for_machine(
    coresys: CoreSys, container: MagicMock
):
    """Test core is loaded with wrong image for machine."""
    coresys.homeassistant.set_image("ghcr.io/home-assistant/odroid-n2-homeassistant")
    coresys.homeassistant.version = AwesomeVersion("2024.4.0")
    container.attrs["Config"] = {"Labels": {"io.hass.version": "2024.4.0"}}

    await coresys.homeassistant.core.load()

    container.remove.assert_called_once_with(force=True)
    assert coresys.docker.images.remove.call_args_list[0].kwargs == {
        "image": "ghcr.io/home-assistant/odroid-n2-homeassistant:latest",
        "force": True,
    }
    assert coresys.docker.images.remove.call_args_list[1].kwargs == {
        "image": "ghcr.io/home-assistant/odroid-n2-homeassistant:2024.4.0",
        "force": True,
    }
    coresys.docker.images.pull.assert_called_once_with(
        "ghcr.io/home-assistant/qemux86-64-homeassistant:2024.4.0",
        platform="linux/amd64",
    )
    assert (
        coresys.homeassistant.image == "ghcr.io/home-assistant/qemux86-64-homeassistant"
    )


async def test_core_load_allows_image_override(coresys: CoreSys, container: MagicMock):
    """Test core does not change image if user overrode it."""
    coresys.homeassistant.set_image("ghcr.io/home-assistant/odroid-n2-homeassistant")
    coresys.homeassistant.version = AwesomeVersion("2024.4.0")
    container.attrs["Config"] = {"Labels": {"io.hass.version": "2024.4.0"}}

    coresys.homeassistant.override_image = True
    await coresys.homeassistant.core.load()

    container.remove.assert_not_called()
    coresys.docker.images.remove.assert_not_called()
    coresys.docker.images.pull.assert_not_called()
    assert (
        coresys.homeassistant.image == "ghcr.io/home-assistant/odroid-n2-homeassistant"
    )


async def test_core_loads_wrong_image_for_architecture(
    coresys: CoreSys, container: MagicMock
):
    """Test core is loaded with wrong image for architecture."""
    coresys.homeassistant.version = AwesomeVersion("2024.4.0")
    container.attrs["Config"] = {"Labels": {"io.hass.version": "2024.4.0"}}
    coresys.docker.images.get("ghcr.io/home-assistant/qemux86-64-homeassistant").attrs[
        "Architecture"
    ] = "arm64"

    await coresys.homeassistant.core.load()

    container.remove.assert_called_once_with(force=True)
    assert coresys.docker.images.remove.call_args_list[0].kwargs == {
        "image": "ghcr.io/home-assistant/qemux86-64-homeassistant:latest",
        "force": True,
    }
    assert coresys.docker.images.remove.call_args_list[1].kwargs == {
        "image": "ghcr.io/home-assistant/qemux86-64-homeassistant:2024.4.0",
        "force": True,
    }
    coresys.docker.images.pull.assert_called_once_with(
        "ghcr.io/home-assistant/qemux86-64-homeassistant:2024.4.0",
        platform="linux/amd64",
    )
    assert (
        coresys.homeassistant.image == "ghcr.io/home-assistant/qemux86-64-homeassistant"
    )
