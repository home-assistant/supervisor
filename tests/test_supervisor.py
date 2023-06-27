"""Test supervisor object."""

from datetime import timedelta
from unittest.mock import AsyncMock, Mock, PropertyMock, patch

from aiohttp import ClientTimeout
from aiohttp.client_exceptions import ClientError
from awesomeversion import AwesomeVersion
import pytest

from supervisor.const import UpdateChannel
from supervisor.coresys import CoreSys
from supervisor.docker.supervisor import DockerSupervisor
from supervisor.exceptions import DockerError, SupervisorUpdateError
from supervisor.host.apparmor import AppArmorControl
from supervisor.resolution.const import ContextType, IssueType
from supervisor.resolution.data import Issue
from supervisor.supervisor import Supervisor


@pytest.fixture(name="websession")
async def fixture_webession(coresys: CoreSys) -> AsyncMock:
    """Mock of websession."""
    mock_websession = AsyncMock()
    with patch.object(
        type(coresys), "websession", new=PropertyMock(return_value=mock_websession)
    ):
        yield mock_websession


@pytest.fixture(name="supervisor_unthrottled")
async def fixture_supervisor_unthrottled(coresys: CoreSys) -> Supervisor:
    """Get supervisor object with connectivity check throttle removed."""
    with patch(
        "supervisor.supervisor._check_connectivity_throttle_period",
        return_value=timedelta(),
    ):
        yield coresys.supervisor


@pytest.mark.parametrize(
    "side_effect,connectivity", [(ClientError(), False), (None, True)]
)
async def test_connectivity_check(
    supervisor_unthrottled: Supervisor,
    websession: AsyncMock,
    side_effect: Exception | None,
    connectivity: bool,
):
    """Test connectivity check."""
    assert supervisor_unthrottled.connectivity is True

    websession.head.side_effect = side_effect
    await supervisor_unthrottled.check_connectivity()

    assert supervisor_unthrottled.connectivity is connectivity


@pytest.mark.parametrize("side_effect,call_count", [(ClientError(), 3), (None, 1)])
async def test_connectivity_check_throttling(
    coresys: CoreSys,
    websession: AsyncMock,
    side_effect: Exception | None,
    call_count: int,
):
    """Test connectivity check throttled when checks succeed."""
    coresys.supervisor.connectivity = None
    websession.head.side_effect = side_effect

    for _ in range(3):
        await coresys.supervisor.check_connectivity()

    assert websession.head.call_count == call_count


async def test_update_failed(coresys: CoreSys, capture_exception: Mock):
    """Test update failure."""
    err = DockerError()
    with patch.object(DockerSupervisor, "install", side_effect=err), patch.object(
        type(coresys.supervisor), "update_apparmor"
    ), pytest.raises(SupervisorUpdateError):
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
    with patch("supervisor.coresys.aiohttp.ClientSession.get") as get, patch.object(
        AppArmorControl, "load_profile"
    ) as load_profile:
        get.return_value.__aenter__.return_value.status = 200
        get.return_value.__aenter__.return_value.text = AsyncMock(return_value="")
        await coresys.supervisor.update_apparmor()

        get.assert_called_once_with(
            f"https://version.home-assistant.io/apparmor_{channel.value}.txt",
            timeout=ClientTimeout(total=10),
        )
        load_profile.assert_called_once()
