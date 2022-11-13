"""Test Home Assistant core."""
from unittest.mock import MagicMock, Mock, PropertyMock, patch

import pytest

from supervisor.const import CpuArch
from supervisor.coresys import CoreSys
from supervisor.docker.homeassistant import DockerHomeAssistant
from supervisor.docker.interface import DockerInterface
from supervisor.exceptions import (
    AudioUpdateError,
    CodeNotaryError,
    DockerError,
    HomeAssistantJobError,
)
from supervisor.homeassistant.core import HomeAssistantCore
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
