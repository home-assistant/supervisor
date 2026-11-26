"""Test cli plugin."""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, PropertyMock, patch

from awesomeversion import AwesomeVersion
import pytest

from supervisor.coresys import CoreSys
from supervisor.docker.cli import DockerCli
from supervisor.docker.manager import DockerAPI
from supervisor.exceptions import (
    CliNotRunningError,
    CliStartError,
    CliStatsTimeoutError,
    CliUnknownError,
    DockerContainerNotFoundError,
    DockerContainerNotRunningError,
    DockerError,
    DockerStatsTimeoutError,
)
from supervisor.os.manager import OSManager


async def test_stats_not_running(coresys: CoreSys):
    """Test stats raises CliNotRunningError when the container isn't running."""
    with (
        patch.object(
            DockerCli,
            "stats",
            AsyncMock(side_effect=DockerContainerNotRunningError(name="hassio_cli")),
        ),
        pytest.raises(CliNotRunningError),
    ):
        await coresys.plugins.cli.stats()

    with (
        patch.object(
            DockerCli,
            "stats",
            AsyncMock(side_effect=DockerContainerNotFoundError(name="hassio_cli")),
        ),
        pytest.raises(CliNotRunningError),
    ):
        await coresys.plugins.cli.stats()


async def test_stats_timeout(coresys: CoreSys):
    """Test stats raises CliStatsTimeoutError on timeout."""
    with (
        patch.object(
            DockerCli,
            "stats",
            AsyncMock(side_effect=DockerStatsTimeoutError(name="hassio_cli")),
        ),
        pytest.raises(CliStatsTimeoutError),
    ):
        await coresys.plugins.cli.stats()


async def test_stats_unknown_error(coresys: CoreSys):
    """Test stats raises CliUnknownError on an unexpected Docker error."""
    with (
        patch.object(DockerCli, "stats", AsyncMock(side_effect=DockerError("boom"))),
        pytest.raises(CliUnknownError),
    ):
        await coresys.plugins.cli.stats()


@pytest.fixture(name="os_version")
def fixture_os_version(request: pytest.FixtureRequest) -> None:
    """Mock HAOS at the version in the param, or no HAOS for None."""
    version = AwesomeVersion(request.param) if request.param else None
    with (
        patch.object(
            OSManager, "available", new=PropertyMock(return_value=bool(version))
        ),
        patch.object(OSManager, "version", new=PropertyMock(return_value=version)),
        patch("supervisor.plugins.cli.OS_HOST_CLI_MIN_VERSION", AwesomeVersion("18.0")),
    ):
        yield


@pytest.mark.parametrize(
    ("os_version", "enabled"),
    [
        pytest.param("18.0", False, id="haos-with-ha"),
        pytest.param("18.1.dev20270101", False, id="haos-dev-with-ha"),
        pytest.param("17.3", True, id="haos-without-ha"),
        pytest.param(None, True, id="not-haos"),
    ],
    indirect=["os_version"],
)
@pytest.mark.usefixtures("os_version")
async def test_enabled_by_os_version(coresys: CoreSys, enabled: bool):
    """Test the cli plugin is disabled on an OS that ships ha itself."""
    assert coresys.plugins.cli.enabled is enabled


@pytest.mark.parametrize("os_version", ["99.0"], indirect=True)
@pytest.mark.usefixtures("os_version")
async def test_enabled_while_os_version_unreleased(coresys: CoreSys):
    """Test the cli plugin stays enabled until the first OS with ha is set."""
    with patch("supervisor.plugins.cli.OS_HOST_CLI_MIN_VERSION", None):
        assert coresys.plugins.cli.enabled is True


@pytest.mark.parametrize("os_version", ["18.0"], indirect=True)
@pytest.mark.usefixtures("os_version")
async def test_load_with_host_cli(coresys: CoreSys):
    """Test load removes the cli container and image and drops the token."""
    cli = coresys.plugins.cli
    cli._data["access_token"] = "c_123456"  # pylint: disable=protected-access
    cli.version = AwesomeVersion("2026.11.0")

    with (
        patch.object(DockerCli, "attach") as attach,
        patch.object(DockerCli, "stop") as stop,
        patch.object(DockerAPI, "remove_image") as remove_image,
        patch.object(type(cli), "start") as start,
        patch.object(type(cli), "save_data"),
    ):
        await cli.load()

    attach.assert_not_called()
    start.assert_not_called()
    stop.assert_called_once()
    remove_image.assert_called_once_with(cli.image, AwesomeVersion("2026.11.0"))
    assert cli.version is None
    assert cli.supervisor_token is None


@pytest.mark.parametrize("os_version", ["17.3"], indirect=True)
@pytest.mark.usefixtures("os_version")
async def test_load_without_host_cli_installs(coresys: CoreSys):
    """Test load installs the cli plugin again on an OS without ha."""
    cli = coresys.plugins.cli
    cli.version = None

    with (
        patch.object(
            DockerCli,
            "get_latest_version",
            return_value=AwesomeVersion("2026.11.0"),
        ),
        patch.object(DockerCli, "attach", side_effect=DockerError()),
        patch.object(DockerCli, "is_running", return_value=False),
        patch.object(type(cli), "install") as install,
        patch.object(type(cli), "start") as start,
    ):
        await cli.load()

    install.assert_called_once()
    start.assert_called_once()


async def test_start_socket_folder_error(coresys: CoreSys, tmp_run_dir: Path):
    """Test start fails without the folder the host OS socket mount needs."""
    # A file in the way makes creating the folder fail
    await asyncio.get_running_loop().run_in_executor(
        None, (tmp_run_dir / "supervisor").write_text, ""
    )

    with (
        patch.object(DockerCli, "run") as run,
        pytest.raises(CliStartError),
    ):
        await coresys.plugins.cli.start()

    run.assert_not_called()
