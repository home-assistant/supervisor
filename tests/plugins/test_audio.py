"""Test audio plugin."""

import errno
from pathlib import Path
from unittest.mock import AsyncMock, Mock, PropertyMock, patch

from awesomeversion import AwesomeVersion
import pytest

from supervisor.const import AddonState, LogLevel
from supervisor.coresys import CoreSys
from supervisor.docker.audio import DockerAudio
from supervisor.exceptions import AddonsError, JobException


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


async def test_restart_audio_addons_no_audio_addons(
    coresys: CoreSys,
    caplog: pytest.LogCaptureFixture,
):
    """Test _restart_audio_addons with no audio add-ons installed."""
    # Mock empty installed add-ons list
    with patch.object(
        type(coresys.addons), "installed", new_callable=PropertyMock
    ) as mock_installed:
        mock_installed.return_value = []
        # Should complete without errors and not attempt to restart any add-ons
        await coresys.plugins.audio._restart_audio_addons()

        # Verify the method returned successfully (no exceptions raised)


async def test_restart_audio_addons_with_audio_addons(
    coresys: CoreSys,
    caplog: pytest.LogCaptureFixture,
):
    """Test _restart_audio_addons with audio add-ons installed."""
    # Create mock audio add-ons
    audio_addon_1 = Mock()
    audio_addon_1.with_audio = True
    audio_addon_1.state = AddonState.STARTED
    audio_addon_1.slug = "audio_addon_1"
    audio_addon_1.restart = AsyncMock()

    audio_addon_2 = Mock()
    audio_addon_2.with_audio = True
    audio_addon_2.state = AddonState.STARTED
    audio_addon_2.slug = "audio_addon_2"
    audio_addon_2.restart = AsyncMock()

    # Create non-audio add-on that should be ignored
    non_audio_addon = Mock()
    non_audio_addon.with_audio = False
    non_audio_addon.state = AddonState.STARTED
    non_audio_addon.slug = "non_audio_addon"
    non_audio_addon.restart = AsyncMock()

    # Create stopped audio add-on that should be ignored
    stopped_audio_addon = Mock()
    stopped_audio_addon.with_audio = True
    stopped_audio_addon.state = AddonState.STOPPED
    stopped_audio_addon.slug = "stopped_audio_addon"
    stopped_audio_addon.restart = AsyncMock()

    mock_addons = [audio_addon_1, audio_addon_2, non_audio_addon, stopped_audio_addon]

    with patch.object(
        type(coresys.addons), "installed", new_callable=PropertyMock
    ) as mock_installed:
        mock_installed.return_value = mock_addons
        await coresys.plugins.audio._restart_audio_addons()

    # Verify only audio add-ons in STARTED state were restarted
    audio_addon_1.restart.assert_called_once()
    audio_addon_2.restart.assert_called_once()
    non_audio_addon.restart.assert_not_called()
    stopped_audio_addon.restart.assert_not_called()

    assert "Restarting 2 audio add-ons after audio plugin restart" in caplog.text
    assert "audio_addon_1" in caplog.text
    assert "audio_addon_2" in caplog.text
    assert "Restarting audio add-on: audio_addon_1" in caplog.text
    assert "Restarting audio add-on: audio_addon_2" in caplog.text


async def test_restart_audio_addons_with_error_handling(
    coresys: CoreSys,
    caplog: pytest.LogCaptureFixture,
):
    """Test _restart_audio_addons handles add-on restart errors gracefully."""
    # Create mock audio add-ons - one succeeds, one fails
    successful_addon = Mock()
    successful_addon.with_audio = True
    successful_addon.state = AddonState.STARTED
    successful_addon.slug = "successful_addon"
    successful_addon.restart = AsyncMock()

    failing_addon = Mock()
    failing_addon.with_audio = True
    failing_addon.state = AddonState.STARTED
    failing_addon.slug = "failing_addon"
    failing_addon.restart = AsyncMock(side_effect=AddonsError("Test error"))

    mock_addons = [successful_addon, failing_addon]

    with (
        patch.object(
            type(coresys.addons), "installed", new_callable=PropertyMock
        ) as mock_installed,
        patch("supervisor.plugins.audio.async_capture_exception") as mock_capture,
    ):
        mock_installed.return_value = mock_addons
        await coresys.plugins.audio._restart_audio_addons()

    # Verify both add-ons were attempted to be restarted
    successful_addon.restart.assert_called_once()
    failing_addon.restart.assert_called_once()

    # Verify error was captured and logged
    mock_capture.assert_called_once()
    assert "Failed to restart audio add-on failing_addon" in caplog.text
    assert "Restarting audio add-on: successful_addon" in caplog.text
    assert "Restarting audio add-on: failing_addon" in caplog.text


async def test_restart_calls_restart_audio_addons(
    coresys: CoreSys,
    docker_interface: tuple[AsyncMock, AsyncMock],
    write_json: Mock,
):
    """Test that restart() method calls _restart_audio_addons."""
    with patch.object(
        coresys.plugins.audio, "_restart_audio_addons"
    ) as mock_restart_addons:
        await coresys.plugins.audio.restart()

        # Verify docker restart was called
        docker_interface[1].assert_called_once()

        # Verify _restart_audio_addons was called after plugin restart
        mock_restart_addons.assert_called_once()


async def test_update_calls_restart_audio_addons(
    coresys: CoreSys,
):
    """Test that update() method calls _restart_audio_addons after successful update."""
    with (
        patch.object(
            type(coresys.plugins.audio), "latest_version", new_callable=PropertyMock
        ) as mock_latest_version,
        patch.object(
            type(coresys.plugins.audio), "version", new_callable=PropertyMock
        ) as mock_version,
        patch("supervisor.plugins.base.PluginBase.update") as mock_super_update,
        patch.object(
            coresys.plugins.audio, "_restart_audio_addons"
        ) as mock_restart_addons,
        patch("supervisor.jobs.decorator.Job.check_conditions", return_value=None),
    ):
        mock_latest_version.return_value = AwesomeVersion("1.2.3")
        mock_version.return_value = AwesomeVersion("1.2.2")
        mock_super_update.return_value = None

        await coresys.plugins.audio.update()

        # Verify super().update() was called
        mock_super_update.assert_called_once()

        # Verify _restart_audio_addons was called after successful update
        mock_restart_addons.assert_called_once()


async def test_update_does_not_restart_addons_on_failure(
    coresys: CoreSys,
):
    """Test that update() method does not call _restart_audio_addons when update fails."""

    with (
        patch.object(
            type(coresys.plugins.audio), "latest_version", new_callable=PropertyMock
        ) as mock_latest_version,
        patch.object(
            type(coresys.plugins.audio), "version", new_callable=PropertyMock
        ) as mock_version,
        patch(
            "supervisor.plugins.base.PluginBase.update",
            side_effect=Exception("Update failed"),
        ),
        patch.object(
            coresys.plugins.audio, "_restart_audio_addons"
        ) as mock_restart_addons,
        patch("supervisor.jobs.decorator.Job.check_conditions", return_value=None),
        pytest.raises(JobException),  # Job decorator wraps exceptions in JobException
    ):
        mock_latest_version.return_value = AwesomeVersion("1.2.3")
        mock_version.return_value = AwesomeVersion("1.2.2")

        await coresys.plugins.audio.update()

        # Verify _restart_audio_addons was NOT called due to update failure
        mock_restart_addons.assert_not_called()
