"""Test supervisor object."""

import asyncio
import errno
from unittest.mock import AsyncMock, MagicMock, Mock, patch

from aiohttp import ClientTimeout
from aiohttp.client_exceptions import ClientError
from awesomeversion import AwesomeVersion
import pytest

from supervisor.const import BusEvent, UpdateChannel
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

from tests.common import MockResponse, wait_for_task_by_name


@pytest.mark.parametrize(
    "side_effect,connectivity", [(ClientError(), False), (None, True)]
)
async def test_connectivity_check(
    coresys: CoreSys,
    websession: MagicMock,
    side_effect: Exception | None,
    connectivity: bool,
):
    """Test connectivity check updates state based on probe outcome."""
    assert coresys.supervisor.connectivity is True

    websession.head = AsyncMock(side_effect=side_effect)
    await coresys.supervisor.check_and_update_connectivity(force=True)

    assert coresys.supervisor.connectivity is connectivity


async def test_connectivity_check_min_interval_when_connected(
    coresys: CoreSys, websession: MagicMock
):
    """Non-forced checks within the min-interval use the cached state."""
    websession.head = AsyncMock()

    # First call runs the probe.
    await coresys.supervisor.check_and_update_connectivity()
    assert websession.head.call_count == 1

    # Second call within the (10 min) window should not hit the network.
    await coresys.supervisor.check_and_update_connectivity()
    assert websession.head.call_count == 1


async def test_connectivity_check_force_bypasses_min_interval(
    coresys: CoreSys, websession: MagicMock
):
    """force=True skips the min-interval short-circuit."""
    websession.head = AsyncMock()

    await coresys.supervisor.check_and_update_connectivity()
    assert websession.head.call_count == 1

    await coresys.supervisor.check_and_update_connectivity(force=True)
    assert websession.head.call_count == 2


async def test_connectivity_check_coalesces_concurrent_callers(
    coresys: CoreSys, websession: MagicMock
):
    """Concurrent callers await the same in-flight probe instead of each firing one."""
    probe_started = asyncio.Event()
    probe_release = asyncio.Event()

    async def slow_head(*args, **kwargs):
        probe_started.set()
        await probe_release.wait()

    websession.head = AsyncMock(side_effect=slow_head)

    first = asyncio.create_task(
        coresys.supervisor.check_and_update_connectivity(force=True)
    )
    await probe_started.wait()

    # Kick off a pile of additional callers while the first probe is in flight.
    concurrent = [
        asyncio.create_task(coresys.supervisor.check_and_update_connectivity())
        for _ in range(5)
    ]
    # Let them all reach the in-flight await.
    await asyncio.sleep(0)

    probe_release.set()
    await asyncio.gather(first, *concurrent)

    assert websession.head.call_count == 1


async def test_connectivity_check_force_during_in_flight_triggers_rerun(
    coresys: CoreSys, websession: MagicMock
):
    """A force signal arriving while a probe is in flight queues exactly one rerun."""
    probe_started = asyncio.Event()
    probe_release = asyncio.Event()

    async def first_then_fast(*args, **kwargs):
        if websession.head.call_count == 1:
            probe_started.set()
            await probe_release.wait()

    websession.head = AsyncMock(side_effect=first_then_fast)

    first = asyncio.create_task(
        coresys.supervisor.check_and_update_connectivity(force=True)
    )
    await probe_started.wait()

    # Forced call while a probe is in flight should set the rerun flag.
    forced = asyncio.create_task(
        coresys.supervisor.check_and_update_connectivity(force=True)
    )
    # Non-forced calls must NOT queue a rerun.
    cheap = asyncio.create_task(coresys.supervisor.check_and_update_connectivity())
    await asyncio.sleep(0)

    probe_release.set()
    await asyncio.gather(first, forced, cheap)

    assert websession.head.call_count == 2


async def test_connectivity_check_owner_cancellation_cancels_probe(
    coresys: CoreSys, websession: MagicMock
):
    """Owner cancellation propagates to the probe and skips updating last-check."""
    probe_started = asyncio.Event()
    probe_release = asyncio.Event()

    async def slow_head(*args, **kwargs):
        probe_started.set()
        await probe_release.wait()

    websession.head = AsyncMock(side_effect=slow_head)
    last_check_before = coresys.supervisor._connectivity_last_check  # pylint: disable=protected-access

    owner = asyncio.create_task(
        coresys.supervisor.check_and_update_connectivity(force=True)
    )
    await probe_started.wait()

    owner.cancel()
    with pytest.raises(asyncio.CancelledError):
        await owner

    # Owner cancellation must cancel the spawned probe, not orphan it,
    # and the cached last-check timestamp must NOT advance.
    assert coresys.supervisor._connectivity_check is None  # pylint: disable=protected-access
    assert coresys.supervisor._connectivity_last_check == last_check_before  # pylint: disable=protected-access

    # A subsequent non-forced call must therefore still run a probe.
    websession.head = AsyncMock()
    await coresys.supervisor.check_and_update_connectivity()
    assert websession.head.call_count == 1


async def test_update_connectivity_fires_event_on_change(coresys: CoreSys):
    """SUPERVISOR_CONNECTIVITY_CHANGE fires only when the cached value changes."""
    events: list[bool] = []

    async def listener(state: bool) -> None:
        events.append(state)

    coresys.bus.register_event(BusEvent.SUPERVISOR_CONNECTIVITY_CHANGE, listener)

    # Same value: no event.
    coresys.supervisor._update_connectivity(True)  # pylint: disable=protected-access
    # Change to False: one event.
    coresys.supervisor._update_connectivity(False)  # pylint: disable=protected-access
    # Change back to True: another event.
    coresys.supervisor._update_connectivity(True)  # pylint: disable=protected-access
    await asyncio.sleep(0)

    assert events == [False, True]


async def test_request_connectivity_check_is_fire_and_forget(
    coresys: CoreSys, websession: MagicMock
):
    """request_connectivity_check schedules a check that runs asynchronously."""
    websession.head = AsyncMock()

    # Synchronous call must return without awaiting the HTTP probe.
    result = coresys.supervisor.request_connectivity_check(force=True)
    assert result is None

    # Wait for the scheduled background check to finish.
    await wait_for_task_by_name(coresys, "Supervisor.check_and_update_connectivity")

    assert websession.head.call_count == 1


async def test_update_failed(coresys: CoreSys, capture_exception: Mock):
    """Test update failure."""
    # pylint: disable-next=protected-access
    coresys.updater._data.setdefault("image", {})["supervisor"] = (
        "ghcr.io/home-assistant/aarch64-hassio-supervisor"
    )
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
