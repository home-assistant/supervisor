"""Testing handling with CoreState."""

import asyncio
from collections.abc import Callable, Coroutine
from datetime import timedelta
import gc
from unittest.mock import AsyncMock, MagicMock, patch
import weakref

from aiohttp.hdrs import USER_AGENT
import pytest

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.dbus.timedate import TimeDate
from supervisor.jobs.decorator import Job
from supervisor.utils.dt import utcnow


async def test_timezone(coresys: CoreSys):
    """Test write corestate to /run/supervisor."""
    # pylint: disable=protected-access
    coresys.host.sys_dbus._timedate = TimeDate()
    # pylint: enable=protected-access

    assert coresys.timezone == "UTC"
    assert coresys.config.timezone is None

    await coresys.dbus.timedate.connect(coresys.dbus.bus)
    assert coresys.timezone == "Etc/UTC"

    await coresys.config.set_timezone("Europe/Zurich")
    assert coresys.timezone == "Europe/Zurich"


async def test_now(coresys: CoreSys):
    """Test datetime now with local time."""
    await coresys.config.set_timezone("Europe/Zurich")

    zurich = coresys.now()
    utc = utcnow()

    assert zurich != utc
    assert zurich - utc <= timedelta(hours=2)


@pytest.mark.no_mock_init_websession
async def test_custom_user_agent(coresys: CoreSys):
    """Test custom useragent."""
    with patch(
        "supervisor.coresys.aiohttp.ClientSession", return_value=MagicMock()
    ) as mock_session:
        await coresys.init_websession()
        assert (
            "HomeAssistantSupervisor/9999.09.9.dev9999"
            in mock_session.call_args_list[0][1]["headers"][USER_AGENT]
        )


@pytest.mark.no_mock_init_websession
async def test_no_init_when_api_running(coresys: CoreSys):
    """Test ClientSession reinitialization is refused when API is running."""
    with patch("supervisor.coresys.aiohttp.ClientSession"):
        await coresys.init_websession()
        await coresys.core.set_state(CoreState.RUNNING)
        # Reinitialize websession should not be possible while running
        with pytest.raises(RuntimeError):
            await coresys.init_websession()


@pytest.mark.parametrize(
    "create",
    [
        pytest.param(CoreSys.create_task, id="task"),
        pytest.param(CoreSys.create_background_task, id="background"),
    ],
)
async def test_create_task_holds_reference_until_done(
    coresys: CoreSys,
    create: Callable[[CoreSys, Coroutine], asyncio.Task],
):
    """Test a task is kept alive while running and released once done."""
    event = asyncio.Event()
    task_ref = weakref.ref(create(coresys, event.wait()))

    gc.collect()
    assert task_ref() is not None

    event.set()
    await coresys.block_till_done(wait_background_tasks=True)
    gc.collect()
    assert task_ref() is None


async def test_create_task_eager_done_not_tracked(coresys: CoreSys):
    """Test an eagerly started task that finished immediately is not tracked."""

    async def done() -> None:
        """Finish without suspending."""

    task = coresys.create_task(done(), eager_start=True)

    assert task.done()
    # pylint: disable-next=protected-access
    assert task not in coresys._active_tasks


async def test_create_background_task_has_no_parent_job(coresys: CoreSys):
    """Test a background task does not inherit the current job."""
    in_job: bool | None = None

    async def check_job() -> None:
        """Record whether the task runs within a job."""
        nonlocal in_job
        in_job = coresys.jobs.is_job

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys

        @Job(name="test_create_background_task_has_no_parent_job_execute")
        async def execute(self) -> asyncio.Task:
            """Create a background task from within a job."""
            return self.coresys.create_background_task(check_job())

    await (await TestClass(coresys).execute())

    assert in_job is False


async def test_block_till_done_waits_for_spawned_tasks(coresys: CoreSys):
    """Test block_till_done waits for tasks created by the tasks it waits on."""
    inner_done = False

    async def inner() -> None:
        """Finish after yielding."""
        nonlocal inner_done
        await asyncio.sleep(0)
        inner_done = True

    async def outer() -> None:
        """Create another task after yielding."""
        await asyncio.sleep(0)
        coresys.create_task(inner())

    coresys.create_task(outer())
    await coresys.block_till_done()

    assert inner_done


async def test_block_till_done_background_tasks(coresys: CoreSys):
    """Test block_till_done only waits for background tasks when asked to."""
    event = asyncio.Event()
    task = coresys.create_background_task(event.wait())

    await coresys.block_till_done()
    assert not task.done()

    coresys.call_later(0.01, event.set)
    await coresys.block_till_done(wait_background_tasks=True)
    assert task.done()


async def test_block_till_done_skips_cancelling_task(coresys: CoreSys):
    """Test block_till_done does not wait for a task that is being cancelled."""
    event = asyncio.Event()

    async def ignore_cancel() -> None:
        """Keep running after being cancelled until the event is set."""
        try:
            await event.wait()
        except asyncio.CancelledError:
            await event.wait()

    task = coresys.create_task(ignore_cancel())
    await asyncio.sleep(0)
    task.cancel()

    await coresys.block_till_done()
    assert not task.done()

    event.set()
    await task


async def test_block_till_done_from_tracked_task(coresys: CoreSys):
    """Test block_till_done called from a tracked task does not wait on itself."""
    await asyncio.wait_for(coresys.create_task(coresys.block_till_done()), 1)


async def test_block_till_done_with_asyncio_sleep_patched(coresys: CoreSys):
    """Test block_till_done still yields to the loop when a test patches asyncio.sleep."""
    called = False

    def set_called() -> None:
        """Record the callback ran."""
        nonlocal called
        called = True

    with patch("asyncio.sleep", new=AsyncMock()) as mock_sleep:
        coresys.loop.call_soon(set_called)
        await coresys.block_till_done()

    assert called
    mock_sleep.assert_not_called()


async def test_block_till_done_logs_pending_tasks(
    coresys: CoreSys, caplog: pytest.LogCaptureFixture
):
    """Test block_till_done logs tasks it is still waiting on."""

    async def slow() -> None:
        """Take longer than the log interval."""
        await asyncio.sleep(0.05)

    coresys.create_task(slow())
    with patch("supervisor.coresys.BLOCK_LOG_INTERVAL", 0.01):
        await coresys.block_till_done()

    assert "Still waiting for task" in caplog.text
