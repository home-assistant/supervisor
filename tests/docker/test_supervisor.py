"""Test Supervisor Docker container timeout handling."""

from awesomeversion import AwesomeVersion
import pytest

from supervisor.coresys import CoreSys
from supervisor.exceptions import DockerTimeoutError


async def test_supervisor_attach_get_timeout(coresys: CoreSys):
    """Test DockerSupervisor.attach raises DockerTimeoutError when containers.get times out."""
    coresys.docker.containers.get.side_effect = TimeoutError()
    with pytest.raises(
        DockerTimeoutError, match="Timeout getting supervisor container"
    ):
        await coresys.supervisor.instance.attach(
            coresys.supervisor.version or AwesomeVersion("2025.1.0")
        )


async def test_supervisor_retag_get_timeout(coresys: CoreSys):
    """Test DockerSupervisor.retag raises DockerTimeoutError when containers.get times out."""
    coresys.docker.containers.get.side_effect = TimeoutError()
    with pytest.raises(
        DockerTimeoutError, match="Timeout getting Supervisor container for retag"
    ):
        await coresys.supervisor.instance.retag()


async def test_supervisor_retag_tag_timeout(coresys: CoreSys):
    """Test DockerSupervisor.retag raises DockerTimeoutError when images.tag times out."""
    # Attach first to initialize metadata via the public API.
    coresys.docker.containers.get.return_value.show.return_value = {
        "ImageID": "sha256:abc123",
        "Image": "sha256:abc123",
        "Config": {
            "Image": "ghcr.io/home-assistant/amd64-hassio-supervisor:latest",
            "Labels": {"io.hass.version": "2025.1.0"},
        },
    }
    await coresys.supervisor.instance.attach(AwesomeVersion("2025.1.0"))

    coresys.docker.images.tag.side_effect = TimeoutError()
    with pytest.raises(
        DockerTimeoutError, match="Timeout retagging Supervisor version"
    ):
        await coresys.supervisor.instance.retag()


async def test_supervisor_update_start_tag_get_timeout(coresys: CoreSys):
    """Test update_start_tag raises DockerTimeoutError when containers.get times out."""
    coresys.docker.containers.get.side_effect = TimeoutError()
    with pytest.raises(
        DockerTimeoutError, match="Timeout getting container to fix start tag"
    ):
        await coresys.supervisor.instance.update_start_tag(
            "ghcr.io/home-assistant/amd64-hassio-supervisor",
            AwesomeVersion("2025.1.0"),
        )


async def test_supervisor_update_start_tag_inspect_timeout(coresys: CoreSys):
    """Test update_start_tag raises DockerTimeoutError when images.inspect times out."""
    coresys.docker.images.inspect.side_effect = TimeoutError()
    with pytest.raises(
        DockerTimeoutError, match="Timeout getting image metadata to fix start tag"
    ):
        await coresys.supervisor.instance.update_start_tag(
            "ghcr.io/home-assistant/amd64-hassio-supervisor",
            AwesomeVersion("2025.1.0"),
        )
