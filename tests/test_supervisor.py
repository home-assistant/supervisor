"""Test supervisor object."""

from datetime import datetime, timedelta
import errno
from unittest.mock import AsyncMock, Mock, PropertyMock, patch

from aiohttp import ClientTimeout
from awesomeversion import AwesomeVersion
import pytest
import requests
from time_machine import travel

from supervisor.const import UpdateChannel
from supervisor.coresys import CoreSys
from supervisor.docker.supervisor import DockerSupervisor
from supervisor.exceptions import (
    DockerError,
    SupervisorAppArmorError,
    SupervisorUpdateError,
)
from supervisor.host.apparmor import AppArmorControl
from supervisor.resolution.const import ContextType, IssueType
from supervisor.resolution.data import Issue
from supervisor.supervisor import Supervisor

from tests.common import reset_last_call


@pytest.fixture(name="websession", scope="function")
async def fixture_webession(coresys: CoreSys) -> AsyncMock:
    """Mock of websession."""
    mock_websession = AsyncMock()
    with patch.object(
        type(coresys), "websession", new=PropertyMock(return_value=mock_websession)
    ):
        yield mock_websession


@pytest.mark.parametrize(
    "side_effect,connectivity",
    [(requests.Timeout(), False), (requests.ConnectionError(), False), (None, True)],
)
@pytest.mark.usefixtures("no_job_throttle")
async def test_connectivity_check(
    coresys: CoreSys,
    side_effect: Exception | None,
    connectivity: bool,
):
    """Test connectivity check."""
    assert coresys.supervisor.connectivity is True

    with patch("requests.head", side_effect=side_effect):
        await coresys.supervisor.check_connectivity()

    assert coresys.supervisor.connectivity is connectivity


@pytest.mark.parametrize(
    "side_effect,call_interval,throttled",
    [
        (None, timedelta(minutes=5), True),
        (None, timedelta(minutes=15), False),
        (requests.Timeout(), timedelta(seconds=20), True),
        (requests.Timeout(), timedelta(seconds=40), False),
    ],
)
async def test_connectivity_check_throttling(
    coresys: CoreSys,
    side_effect: Exception | None,
    call_interval: timedelta,
    throttled: bool,
):
    """Test connectivity check throttled when checks succeed."""
    coresys.supervisor.connectivity = None

    with patch("requests.head", side_effect=side_effect) as mock_head:
        reset_last_call(Supervisor.check_connectivity)
        with travel(datetime.now(), tick=False) as traveller:
            await coresys.supervisor.check_connectivity()
            traveller.shift(call_interval)
            await coresys.supervisor.check_connectivity()

        assert mock_head.call_count == (1 if throttled else 2)


async def test_update_failed(coresys: CoreSys, capture_exception: Mock):
    """Test update failure."""
    err = DockerError()
    with (
        patch.object(DockerSupervisor, "install", side_effect=err),
        patch.object(type(coresys.supervisor), "update_apparmor"),
        pytest.raises(SupervisorUpdateError),
    ):
        await coresys.supervisor.update(AwesomeVersion("1.0"))

    capture_exception.assert_called_once_with(err)
    assert (
        Issue(IssueType.UPDATE_FAILED, ContextType.SUPERVISOR)
        in coresys.resolution.issues
    )


@pytest.mark.parametrize(
    "channel", [UpdateChannel.STABLE, UpdateChannel.BETA, UpdateChannel.DEV]
)
async def test_update_apparmor(
    coresys: CoreSys, channel: UpdateChannel, tmp_supervisor_data
):
    """Test updating apparmor."""
    coresys.updater.channel = channel
    with (
        patch("supervisor.coresys.aiohttp.ClientSession.get") as get,
        patch.object(AppArmorControl, "load_profile") as load_profile,
    ):
        get.return_value.__aenter__.return_value.status = 200
        get.return_value.__aenter__.return_value.text = AsyncMock(return_value="")
        await coresys.supervisor.update_apparmor()

        get.assert_called_once_with(
            f"https://version.home-assistant.io/apparmor_{channel}.txt",
            timeout=ClientTimeout(total=10),
        )
        load_profile.assert_called_once()


async def test_update_apparmor_error(coresys: CoreSys, tmp_supervisor_data):
    """Test error updating apparmor profile."""
    with (
        patch("supervisor.coresys.aiohttp.ClientSession.get") as get,
        patch.object(AppArmorControl, "load_profile"),
        patch("supervisor.supervisor.Path.write_text", side_effect=(err := OSError())),
    ):
        get.return_value.__aenter__.return_value.status = 200
        get.return_value.__aenter__.return_value.text = AsyncMock(return_value="")

        err.errno = errno.EBUSY
        with pytest.raises(SupervisorAppArmorError):
            await coresys.supervisor.update_apparmor()
        assert coresys.core.healthy is True

        err.errno = errno.EBADMSG
        with pytest.raises(SupervisorAppArmorError):
            await coresys.supervisor.update_apparmor()
        assert coresys.core.healthy is False
