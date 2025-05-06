"""Test supervisor object."""

from datetime import datetime, timedelta
import errno
from unittest.mock import AsyncMock, MagicMock, Mock, patch

from aiohttp import ClientTimeout
from aiohttp.client_exceptions import ClientError
from awesomeversion import AwesomeVersion
import pytest
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

from tests.common import MockResponse, reset_last_call


@pytest.mark.parametrize(
    "side_effect,connectivity", [(ClientError(), False), (None, True)]
)
@pytest.mark.usefixtures("no_job_throttle")
async def test_connectivity_check(
    coresys: CoreSys,
    websession: MagicMock,
    side_effect: Exception | None,
    connectivity: bool,
):
    """Test connectivity check."""
    assert coresys.supervisor.connectivity is True

    websession.head = AsyncMock(side_effect=side_effect)
    await coresys.supervisor.check_connectivity()

    assert coresys.supervisor.connectivity is connectivity


@pytest.mark.parametrize(
    "side_effect,call_interval,throttled",
    [
        (None, timedelta(minutes=5), True),
        (None, timedelta(minutes=15), False),
        (ClientError(), timedelta(seconds=20), True),
        (ClientError(), timedelta(seconds=40), False),
    ],
)
async def test_connectivity_check_throttling(
    coresys: CoreSys,
    websession: MagicMock,
    side_effect: Exception | None,
    call_interval: timedelta,
    throttled: bool,
):
    """Test connectivity check throttled when checks succeed."""
    coresys.supervisor.connectivity = None
    websession.head = AsyncMock(side_effect=side_effect)

    reset_last_call(Supervisor.check_connectivity)
    with travel(datetime.now(), tick=False) as traveller:
        await coresys.supervisor.check_connectivity()
        traveller.shift(call_interval)
        await coresys.supervisor.check_connectivity()

    assert websession.head.call_count == (1 if throttled else 2)


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
    coresys: CoreSys, channel: UpdateChannel, websession: MagicMock, tmp_supervisor_data
):
    """Test updating apparmor."""
    websession.get = Mock(return_value=MockResponse())
    coresys.updater.channel = channel
    with (
        patch.object(AppArmorControl, "load_profile") as load_profile,
    ):
        await coresys.supervisor.update_apparmor()

        websession.get.assert_called_once_with(
            f"https://version.home-assistant.io/apparmor_{channel}.txt",
            timeout=ClientTimeout(total=10),
        )
        load_profile.assert_called_once()


async def test_update_apparmor_error(
    coresys: CoreSys, websession: MagicMock, tmp_supervisor_data
):
    """Test error updating apparmor profile."""
    websession.get = Mock(return_value=MockResponse())
    with (
        patch.object(AppArmorControl, "load_profile"),
        patch("supervisor.supervisor.Path.write_text", side_effect=(err := OSError())),
    ):
        err.errno = errno.EBUSY
        with pytest.raises(SupervisorAppArmorError):
            await coresys.supervisor.update_apparmor()
        assert coresys.core.healthy is True

        err.errno = errno.EBADMSG
        with pytest.raises(SupervisorAppArmorError):
            await coresys.supervisor.update_apparmor()
        assert coresys.core.healthy is False
