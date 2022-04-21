"""Test DNS plugin."""
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from supervisor.coresys import CoreSys
from supervisor.docker.interface import DockerInterface


@pytest.fixture(name="docker_interface")
async def fixture_docker_interface() -> tuple[AsyncMock, AsyncMock]:
    """Mock docker interface methods."""
    # with patch("supervisor.docker.interface.DockerInterface.run"), patch("supervisor.docker.interface.DockerInterface.restart")
    with patch.object(DockerInterface, "run") as run, patch.object(
        DockerInterface, "restart"
    ) as restart:
        yield (run, restart)


@pytest.fixture(name="write_json")
async def fixture_write_json() -> Mock:
    """Mock json file writer."""
    with patch("supervisor.plugins.dns.write_json_file") as write_json_file:
        yield write_json_file


@pytest.mark.parametrize("start", [True, False])
async def test_config_write(
    coresys: CoreSys,
    docker_interface: tuple[AsyncMock, AsyncMock],
    write_json: Mock,
    start: bool,
):
    """Test config write on DNS start and restart."""
    assert coresys.plugins.dns.locals == ["dns://192.168.30.1"]
    coresys.plugins.dns.servers = ["dns://1.1.1.1", "dns://8.8.8.8"]

    if start:
        await coresys.plugins.dns.start()
        docker_interface[0].assert_called_once()
        docker_interface[1].assert_not_called()
    else:
        await coresys.plugins.dns.restart()
        docker_interface[0].assert_not_called()
        docker_interface[1].assert_called_once()

    write_json.assert_called_once_with(
        Path("/data/dns/coredns.json"),
        {
            "servers": ["dns://1.1.1.1", "dns://8.8.8.8"],
            "locals": ["dns://192.168.30.1"],
            "debug": False,
        },
    )
