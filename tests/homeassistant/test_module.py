"""Test Homeassistant module."""

import asyncio
import errno
from pathlib import Path
from unittest.mock import AsyncMock, patch

from pytest import LogCaptureFixture, raises

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.docker.interface import DockerInterface
from supervisor.exceptions import (
    HomeAssistantBackupError,
    HomeAssistantWSConnectionError,
)
from supervisor.homeassistant.secrets import HomeAssistantSecrets
from supervisor.homeassistant.websocket import HomeAssistantWebSocket


async def test_load(
    coresys: CoreSys, tmp_supervisor_data: Path, ha_ws_client: AsyncMock
):
    """Test homeassistant module load."""
    with open(tmp_supervisor_data / "homeassistant" / "secrets.yaml", "w") as secrets:
        secrets.write("hello: world\n")

    # Unwrap read_secrets to prevent throttling between tests
    with (
        patch.object(DockerInterface, "attach") as attach,
        patch.object(DockerInterface, "check_image") as check_image,
        patch.object(
            HomeAssistantSecrets,
            "_read_secrets",
            new=HomeAssistantSecrets._read_secrets.__wrapped__,
        ),
    ):
        await coresys.homeassistant.load()

        attach.assert_called_once()
        check_image.assert_called_once()

    assert coresys.homeassistant.secrets.secrets == {"hello": "world"}

    coresys.core.state = CoreState.SETUP
    await coresys.homeassistant.websocket.async_send_message({"lorem": "ipsum"})
    ha_ws_client.async_send_command.assert_not_called()

    coresys.core.state = CoreState.RUNNING
    await asyncio.sleep(0)
    assert ha_ws_client.async_send_command.call_args_list[0][0][0] == {"lorem": "ipsum"}


async def test_get_users_none(coresys: CoreSys, ha_ws_client: AsyncMock):
    """Test get users returning none does not fail."""
    ha_ws_client.async_send_command.return_value = None
    assert [] == await coresys.homeassistant.get_users.__wrapped__(
        coresys.homeassistant
    )


def test_write_pulse_error(coresys: CoreSys, caplog: LogCaptureFixture):
    """Test errors writing pulse config."""
    with patch(
        "supervisor.homeassistant.module.Path.write_text",
        side_effect=(err := OSError()),
    ):
        err.errno = errno.EBUSY
        coresys.homeassistant.write_pulse()

        assert "can't write pulse/client.config" in caplog.text
        assert coresys.core.healthy is True

        caplog.clear()
        err.errno = errno.EBADMSG
        coresys.homeassistant.write_pulse()

        assert "can't write pulse/client.config" in caplog.text
        assert coresys.core.healthy is False


async def test_begin_backup_ws_error(coresys: CoreSys):
    """Test WS error when beginning backup."""
    # pylint: disable-next=protected-access
    coresys.homeassistant.websocket._client.async_send_command.side_effect = (
        HomeAssistantWSConnectionError
    )
    with (
        patch.object(HomeAssistantWebSocket, "_can_send", return_value=True),
        raises(
            HomeAssistantBackupError,
            match="Preparing backup of Home Assistant Core failed. Check HA Core logs.",
        ),
    ):
        await coresys.homeassistant.begin_backup()


async def test_end_backup_ws_error(coresys: CoreSys, caplog: LogCaptureFixture):
    """Test WS error when ending backup."""
    # pylint: disable-next=protected-access
    coresys.homeassistant.websocket._client.async_send_command.side_effect = (
        HomeAssistantWSConnectionError
    )
    with patch.object(HomeAssistantWebSocket, "_can_send", return_value=True):
        await coresys.homeassistant.end_backup()

    assert (
        "Error resuming normal operations after backup of Home Assistant Core. Check HA Core logs."
        in caplog.text
    )
