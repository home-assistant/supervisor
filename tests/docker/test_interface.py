"""Test Docker interface."""

import asyncio
from typing import Any
from unittest.mock import MagicMock, Mock, PropertyMock, call, patch

from awesomeversion import AwesomeVersion
from docker.errors import DockerException, NotFound
from docker.models.containers import Container
from docker.models.images import Image
import pytest
from requests import RequestException

from supervisor.addons.manager import Addon
from supervisor.const import BusEvent, CpuArch
from supervisor.coresys import CoreSys
from supervisor.docker.const import ContainerState
from supervisor.docker.interface import DockerInterface
from supervisor.docker.monitor import DockerContainerStateEvent
from supervisor.exceptions import (
    DockerAPIError,
    DockerError,
    DockerNotFound,
    DockerRequestError,
)


@pytest.fixture(autouse=True)
def mock_verify_content(coresys: CoreSys):
    """Mock verify_content utility during tests."""
    with patch.object(
        coresys.security, "verify_content", return_value=None
    ) as verify_content:
        yield verify_content


@pytest.mark.parametrize(
    "cpu_arch, platform",
    [
        (CpuArch.ARMV7, "linux/arm/v7"),
        (CpuArch.ARMHF, "linux/arm/v6"),
        (CpuArch.AARCH64, "linux/arm64"),
        (CpuArch.I386, "linux/386"),
        (CpuArch.AMD64, "linux/amd64"),
    ],
)
async def test_docker_image_platform(
    coresys: CoreSys,
    test_docker_interface: DockerInterface,
    cpu_arch: str,
    platform: str,
):
    """Test platform set correctly from arch."""
    with patch.object(
        coresys.docker.images, "pull", return_value=Mock(id="test:1.2.3")
    ) as pull:
        await test_docker_interface.install(
            AwesomeVersion("1.2.3"), "test", arch=cpu_arch
        )
        assert pull.call_count == 1
        assert pull.call_args == call("test:1.2.3", platform=platform)


async def test_docker_image_default_platform(
    coresys: CoreSys, test_docker_interface: DockerInterface
):
    """Test platform set using supervisor arch when omitted."""
    with (
        patch.object(
            type(coresys.supervisor), "arch", PropertyMock(return_value="i386")
        ),
        patch.object(
            coresys.docker.images, "pull", return_value=Mock(id="test:1.2.3")
        ) as pull,
    ):
        await test_docker_interface.install(AwesomeVersion("1.2.3"), "test")
        assert pull.call_count == 1
        assert pull.call_args == call("test:1.2.3", platform="linux/386")


@pytest.mark.parametrize(
    "attrs,expected",
    [
        ({"State": {"Status": "running"}}, ContainerState.RUNNING),
        ({"State": {"Status": "exited", "ExitCode": 0}}, ContainerState.STOPPED),
        ({"State": {"Status": "exited", "ExitCode": 137}}, ContainerState.FAILED),
        (
            {"State": {"Status": "running", "Health": {"Status": "healthy"}}},
            ContainerState.HEALTHY,
        ),
        (
            {"State": {"Status": "running", "Health": {"Status": "unhealthy"}}},
            ContainerState.UNHEALTHY,
        ),
    ],
)
async def test_current_state(
    coresys: CoreSys, attrs: dict[str, Any], expected: ContainerState
):
    """Test current state for container."""
    container_collection = MagicMock()
    container_collection.get.return_value = Container(attrs)
    with patch(
        "supervisor.docker.manager.DockerAPI.containers",
        new=PropertyMock(return_value=container_collection),
    ):
        assert await coresys.homeassistant.core.instance.current_state() == expected


async def test_current_state_failures(coresys: CoreSys):
    """Test failure states for current state."""
    container_collection = MagicMock()
    with patch(
        "supervisor.docker.manager.DockerAPI.containers",
        new=PropertyMock(return_value=container_collection),
    ):
        container_collection.get.side_effect = NotFound("dne")
        assert (
            await coresys.homeassistant.core.instance.current_state()
            == ContainerState.UNKNOWN
        )

        container_collection.get.side_effect = DockerException()
        with pytest.raises(DockerAPIError):
            await coresys.homeassistant.core.instance.current_state()

        container_collection.get.side_effect = RequestException()
        with pytest.raises(DockerRequestError):
            await coresys.homeassistant.core.instance.current_state()


@pytest.mark.parametrize(
    "attrs,expected,fired_when_skip_down",
    [
        ({"State": {"Status": "running"}}, ContainerState.RUNNING, True),
        ({"State": {"Status": "exited", "ExitCode": 0}}, ContainerState.STOPPED, False),
        (
            {"State": {"Status": "exited", "ExitCode": 137}},
            ContainerState.FAILED,
            False,
        ),
        (
            {"State": {"Status": "running", "Health": {"Status": "healthy"}}},
            ContainerState.HEALTHY,
            True,
        ),
        (
            {"State": {"Status": "running", "Health": {"Status": "unhealthy"}}},
            ContainerState.UNHEALTHY,
            True,
        ),
    ],
)
async def test_attach_existing_container(
    coresys: CoreSys,
    attrs: dict[str, Any],
    expected: ContainerState,
    fired_when_skip_down: bool,
):
    """Test attaching to existing container."""
    attrs["Id"] = "abc123"
    attrs["Config"] = {}
    container_collection = MagicMock()
    container_collection.get.return_value = Container(attrs)
    with (
        patch(
            "supervisor.docker.manager.DockerAPI.containers",
            new=PropertyMock(return_value=container_collection),
        ),
        patch.object(type(coresys.bus), "fire_event") as fire_event,
        patch("supervisor.docker.interface.time", return_value=1),
    ):
        await coresys.homeassistant.core.instance.attach(AwesomeVersion("2022.7.3"))
        await asyncio.sleep(0)
        assert [
            event
            for event in fire_event.call_args_list
            if event.args[0] == BusEvent.DOCKER_CONTAINER_STATE_CHANGE
        ] == [
            call(
                BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
                DockerContainerStateEvent("homeassistant", expected, "abc123", 1),
            )
        ]

        fire_event.reset_mock()
        await coresys.homeassistant.core.instance.attach(
            AwesomeVersion("2022.7.3"), skip_state_event_if_down=True
        )
        await asyncio.sleep(0)
        docker_events = [
            event
            for event in fire_event.call_args_list
            if event.args[0] == BusEvent.DOCKER_CONTAINER_STATE_CHANGE
        ]
        if fired_when_skip_down:
            assert docker_events == [
                call(
                    BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
                    DockerContainerStateEvent("homeassistant", expected, "abc123", 1),
                )
            ]
        else:
            assert not docker_events


async def test_attach_container_failure(coresys: CoreSys):
    """Test attach fails to find container but finds image."""
    container_collection = MagicMock()
    container_collection.get.side_effect = DockerException()
    image_collection = MagicMock()
    image_config = {"Image": "sha256:abc123"}
    image_collection.get.return_value = Image({"Config": image_config})
    with (
        patch(
            "supervisor.docker.manager.DockerAPI.containers",
            new=PropertyMock(return_value=container_collection),
        ),
        patch(
            "supervisor.docker.manager.DockerAPI.images",
            new=PropertyMock(return_value=image_collection),
        ),
        patch.object(type(coresys.bus), "fire_event") as fire_event,
    ):
        await coresys.homeassistant.core.instance.attach(AwesomeVersion("2022.7.3"))
        assert not [
            event
            for event in fire_event.call_args_list
            if event.args[0] == BusEvent.DOCKER_CONTAINER_STATE_CHANGE
        ]
        assert coresys.homeassistant.core.instance.meta_config == image_config


async def test_attach_total_failure(coresys: CoreSys):
    """Test attach fails to find container or image."""
    container_collection = MagicMock()
    container_collection.get.side_effect = DockerException()
    image_collection = MagicMock()
    image_collection.get.side_effect = DockerException()
    with (
        patch(
            "supervisor.docker.manager.DockerAPI.containers",
            new=PropertyMock(return_value=container_collection),
        ),
        patch(
            "supervisor.docker.manager.DockerAPI.images",
            new=PropertyMock(return_value=image_collection),
        ),
        pytest.raises(DockerError),
    ):
        await coresys.homeassistant.core.instance.attach(AwesomeVersion("2022.7.3"))


@pytest.mark.parametrize("err", [DockerException(), RequestException()])
async def test_image_pull_fail(
    coresys: CoreSys, capture_exception: Mock, err: Exception
):
    """Test failure to pull image."""
    coresys.docker.images.pull.side_effect = err
    with pytest.raises(DockerError):
        await coresys.homeassistant.core.instance.install(
            AwesomeVersion("2022.7.3"), arch=CpuArch.AMD64
        )

    capture_exception.assert_called_once_with(err)


async def test_run_missing_image(
    coresys: CoreSys,
    install_addon_ssh: Addon,
    container: MagicMock,
    capture_exception: Mock,
    path_extern,
):
    """Test run captures the exception when image is missing."""
    coresys.docker.containers.create.side_effect = [NotFound("missing"), MagicMock()]
    container.status = "stopped"
    install_addon_ssh.data["image"] = "test_image"

    with pytest.raises(DockerNotFound):
        await install_addon_ssh.instance.run()

    capture_exception.assert_called_once()
