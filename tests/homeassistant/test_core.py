"""Test Home Assistant core."""
from unittest.mock import MagicMock, Mock, PropertyMock, patch

from awesomeversion import AwesomeVersion
from docker.errors import DockerException, ImageNotFound, NotFound
import pytest

from supervisor.const import CpuArch
from supervisor.coresys import CoreSys
from supervisor.docker.homeassistant import DockerHomeAssistant
from supervisor.docker.interface import DockerInterface
from supervisor.docker.manager import DockerAPI
from supervisor.exceptions import (
    AudioUpdateError,
    CodeNotaryError,
    DockerError,
    HomeAssistantError,
    HomeAssistantJobError,
)
from supervisor.homeassistant.core import HomeAssistantCore
from supervisor.homeassistant.module import HomeAssistant
from supervisor.updater import Updater


async def test_update_fails_if_out_of_date(coresys: CoreSys):
    """Test update of Home Assistant fails when supervisor or plugin is out of date."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    with patch.object(
        type(coresys.supervisor), "need_update", new=PropertyMock(return_value=True)
    ), pytest.raises(HomeAssistantJobError):
        await coresys.homeassistant.core.update()

    with patch.object(
        type(coresys.plugins.audio), "need_update", new=PropertyMock(return_value=True)
    ), patch.object(
        type(coresys.plugins.audio), "update", side_effect=AudioUpdateError
    ), pytest.raises(
        HomeAssistantJobError
    ):
        await coresys.homeassistant.core.update()


async def test_install_landingpage_docker_error(
    coresys: CoreSys, capture_exception: Mock, caplog: pytest.LogCaptureFixture
):
    """Test install landing page fails due to docker error."""
    coresys.security.force = True
    with patch.object(
        DockerHomeAssistant, "attach", side_effect=DockerError
    ), patch.object(
        Updater, "image_homeassistant", new=PropertyMock(return_value="homeassistant")
    ), patch.object(
        DockerInterface, "arch", new=PropertyMock(return_value=CpuArch.AMD64)
    ), patch(
        "supervisor.homeassistant.core.asyncio.sleep"
    ) as sleep, patch(
        "supervisor.security.module.cas_validate",
        side_effect=[CodeNotaryError, None],
    ):
        await coresys.homeassistant.core.install_landingpage()
        sleep.assert_awaited_once_with(30)

    assert "Fails install landingpage, retry after 30sec" in caplog.text
    capture_exception.assert_not_called()


async def test_install_landingpage_other_error(
    coresys: CoreSys, capture_exception: Mock, caplog: pytest.LogCaptureFixture
):
    """Test install landing page fails due to other error."""
    coresys.docker.images.pull.side_effect = [(err := OSError()), MagicMock()]

    with patch.object(
        DockerHomeAssistant, "attach", side_effect=DockerError
    ), patch.object(
        Updater, "image_homeassistant", new=PropertyMock(return_value="homeassistant")
    ), patch.object(
        DockerInterface, "arch", new=PropertyMock(return_value=CpuArch.AMD64)
    ), patch(
        "supervisor.homeassistant.core.asyncio.sleep"
    ) as sleep:
        await coresys.homeassistant.core.install_landingpage()
        sleep.assert_awaited_once_with(30)

    assert "Fails install landingpage, retry after 30sec" in caplog.text
    capture_exception.assert_called_once_with(err)


async def test_install_docker_error(
    coresys: CoreSys, capture_exception: Mock, caplog: pytest.LogCaptureFixture
):
    """Test install fails due to docker error."""
    coresys.security.force = True
    with patch.object(HomeAssistantCore, "_start"), patch.object(
        DockerHomeAssistant, "cleanup"
    ), patch.object(
        Updater, "image_homeassistant", new=PropertyMock(return_value="homeassistant")
    ), patch.object(
        Updater, "version_homeassistant", new=PropertyMock(return_value="2022.7.3")
    ), patch.object(
        DockerInterface, "arch", new=PropertyMock(return_value=CpuArch.AMD64)
    ), patch(
        "supervisor.homeassistant.core.asyncio.sleep"
    ) as sleep, patch(
        "supervisor.security.module.cas_validate",
        side_effect=[CodeNotaryError, None],
    ):
        await coresys.homeassistant.core.install()
        sleep.assert_awaited_once_with(30)

    assert "Error on Home Assistant installation. Retry in 30sec" in caplog.text
    capture_exception.assert_not_called()


async def test_install_other_error(
    coresys: CoreSys, capture_exception: Mock, caplog: pytest.LogCaptureFixture
):
    """Test install fails due to other error."""
    coresys.docker.images.pull.side_effect = [(err := OSError()), MagicMock()]

    with patch.object(HomeAssistantCore, "_start"), patch.object(
        DockerHomeAssistant, "cleanup"
    ), patch.object(
        Updater, "image_homeassistant", new=PropertyMock(return_value="homeassistant")
    ), patch.object(
        Updater, "version_homeassistant", new=PropertyMock(return_value="2022.7.3")
    ), patch.object(
        DockerInterface, "arch", new=PropertyMock(return_value=CpuArch.AMD64)
    ), patch(
        "supervisor.homeassistant.core.asyncio.sleep"
    ) as sleep:
        await coresys.homeassistant.core.install()
        sleep.assert_awaited_once_with(30)

    assert "Error on Home Assistant installation. Retry in 30sec" in caplog.text
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

    with patch.object(
        HomeAssistant,
        "version",
        new=PropertyMock(return_value=AwesomeVersion("2023.7.0")),
    ), patch.object(DockerAPI, "run") as run, patch.object(
        HomeAssistantCore, "_block_till_run"
    ) as block_till_run:
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

    with patch.object(
        HomeAssistant,
        "version",
        new=PropertyMock(return_value=AwesomeVersion("2023.7.0")),
    ), patch.object(HomeAssistantCore, "_block_till_run") as block_till_run:
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
            timeout=240
        )
    else:
        coresys.docker.containers.get.return_value.stop.assert_not_called()


async def test_restart(coresys: CoreSys):
    """Test restarting Home Assistant."""
    with patch.object(HomeAssistantCore, "_block_till_run") as block_till_run:
        await coresys.homeassistant.core.restart()
        block_till_run.assert_called_once()

    coresys.docker.containers.get.return_value.restart.assert_called_once_with(
        timeout=240
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
