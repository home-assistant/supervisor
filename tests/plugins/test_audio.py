"""Test audio plugin."""

import errno
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from supervisor.const import LogLevel
from supervisor.coresys import CoreSys
from supervisor.docker.audio import DockerAudio


@pytest.fixture(name="docker_interface")
async def fixture_docker_interface() -> tuple[AsyncMock, AsyncMock]:
    """Mock docker interface methods."""
    with (
        patch.object(DockerAudio, "run") as run,
        patch.object(DockerAudio, "restart") as restart,
    ):
        yield (run, restart)


@pytest.fixture(name="write_json")
async def fixture_write_json() -> Mock:
    """Mock json file writer."""
    with patch("supervisor.plugins.audio.write_json_file") as write_json_file:
        yield write_json_file


async def test_config_write(
    coresys: CoreSys,
    docker_interface: tuple[AsyncMock, AsyncMock],
    write_json: Mock,
):
    """Test config write on audio start and restart."""
    await coresys.plugins.audio.start()
    docker_interface[0].assert_called_once()
    docker_interface[1].assert_not_called()

    write_json.assert_called_once_with(
        Path("/data/audio/pulse_audio.json"),
        {
            "debug": False,
        },
    )

    docker_interface[0].reset_mock()
    write_json.reset_mock()
    coresys.config.logging = LogLevel.DEBUG

    await coresys.plugins.audio.restart()
    docker_interface[0].assert_not_called()
    docker_interface[1].assert_called_once()

    write_json.assert_called_once_with(
        Path("/data/audio/pulse_audio.json"),
        {
            "debug": True,
        },
    )


async def test_load_error(
    coresys: CoreSys, caplog: pytest.LogCaptureFixture, container
):
    """Test error reading config file during load."""
    with (
        patch(
            "supervisor.plugins.audio.Path.read_text", side_effect=(err := OSError())
        ),
        patch("supervisor.plugins.audio.shutil.copy", side_effect=err),
    ):
        err.errno = errno.EBUSY
        await coresys.plugins.audio.load()

        assert "Can't read pulse-client.tmpl" in caplog.text
        assert "Can't create default asound" in caplog.text
        assert coresys.core.healthy is True

        caplog.clear()
        err.errno = errno.EBADMSG
        await coresys.plugins.audio.load()

        assert "Can't read pulse-client.tmpl" in caplog.text
        assert "Can't create default asound" in caplog.text
        assert coresys.core.healthy is False
