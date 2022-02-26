"""Test Docker interface."""
from unittest.mock import Mock, PropertyMock, call, patch

from awesomeversion import AwesomeVersion
import pytest

from supervisor.coresys import CoreSys
from supervisor.docker.interface import DockerInterface


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
        ("armv7", "linux/arm/v7"),
        ("armhf", "linux/arm/v6"),
        ("aarch64", "linux/arm64"),
        ("i386", "linux/386"),
        ("amd64", "linux/amd64"),
    ],
)
async def test_docker_image_platform(coresys: CoreSys, cpu_arch: str, platform: str):
    """Test platform set correctly from arch."""
    with patch.object(
        coresys.docker.images, "pull", return_value=Mock(id="test:1.2.3")
    ) as pull:
        instance = DockerInterface(coresys)
        await instance.install(AwesomeVersion("1.2.3"), "test", arch=cpu_arch)
        assert pull.call_count == 1
        assert pull.call_args == call("test:1.2.3", platform=platform)


async def test_docker_image_default_platform(coresys: CoreSys):
    """Test platform set using supervisor arch when omitted."""
    with patch.object(
        type(coresys.supervisor), "arch", PropertyMock(return_value="i386")
    ), patch.object(
        coresys.docker.images, "pull", return_value=Mock(id="test:1.2.3")
    ) as pull:
        instance = DockerInterface(coresys)
        await instance.install(AwesomeVersion("1.2.3"), "test")
        assert pull.call_count == 1
        assert pull.call_args == call("test:1.2.3", platform="linux/386")
