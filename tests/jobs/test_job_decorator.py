"""Test the condition decorators."""

import asyncio
from datetime import datetime, timedelta
from unittest.mock import ANY, AsyncMock, Mock, PropertyMock, patch
from uuid import uuid4

from aiohttp.client_exceptions import ClientError
import pytest
import time_machine

from supervisor.const import BusEvent, CoreState
from supervisor.coresys import CoreSys
from supervisor.exceptions import (
    AudioUpdateError,
    HassioError,
    JobException,
    PluginJobError,
)
from supervisor.host.const import HostFeature
from supervisor.host.manager import HostManager
from supervisor.jobs import JobSchedulerOptions, SupervisorJob
from supervisor.jobs.const import JobConcurrency, JobThrottle
from supervisor.jobs.decorator import Job, JobCondition
from supervisor.jobs.job_group import JobGroup
from supervisor.os.manager import OSManager
from supervisor.plugins.audio import PluginAudio
from supervisor.resolution.const import UnhealthyReason, UnsupportedReason
from supervisor.supervisor import Supervisor
from supervisor.utils.dt import utcnow

from tests.common import reset_last_call


async def test_healthy(coresys: CoreSys, caplog: pytest.LogCaptureFixture):
    """Test the healty decorator."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys

        @Job(name="test_healthy_execute", conditions=[JobCondition.HEALTHY])
        async def execute(self):
            """Execute the class method."""
            return True

    test = TestClass(coresys)
    assert await test.execute()

    coresys.resolution.add_unhealthy_reason(UnhealthyReason.DOCKER)
    assert not await test.execute()
    assert "blocked from execution, system is not healthy - docker" in caplog.text

    coresys.jobs.ignore_conditions = [JobCondition.HEALTHY]
    assert await test.execute()


@pytest.mark.parametrize(
    "connectivity,head_side_effect,host_result,system_result",
    [
        (4, None, True, True),
        (4, ClientError(), True, None),
        (0, None, None, True),
        (0, ClientError(), None, None),
    ],
)
async def test_internet(
    coresys: CoreSys,
    connectivity: int,
    head_side_effect: Exception | None,
    host_result: bool | None,
    system_result: bool | None,
):
    """Test the internet decorator."""
    await coresys.core.set_state(CoreState.RUNNING)
    reset_last_call(Supervisor.check_connectivity)

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys

        @Job(
            name=f"test_internet_execute_host_{uuid4().hex}",
            conditions=[JobCondition.INTERNET_HOST],
        )
        async def execute_host(self):
            """Execute the class method."""
            return True

        @Job(
            name=f"test_internet_execute_system_{uuid4().hex}",
            conditions=[JobCondition.INTERNET_SYSTEM],
        )
        async def execute_system(self):
            """Execute the class method."""
            return True

    test = TestClass(coresys)

    mock_websession = AsyncMock()
    mock_websession.head.side_effect = head_side_effect
    coresys.supervisor.connectivity = None
    with (
        patch("supervisor.utils.dbus.DBus.call_dbus", return_value=connectivity),
        patch.object(
            CoreSys, "websession", new=PropertyMock(return_value=mock_websession)
        ),
    ):
        assert await test.execute_host() is host_result
        assert await test.execute_system() is system_result

        coresys.jobs.ignore_conditions = [
            JobCondition.INTERNET_HOST,
            JobCondition.INTERNET_SYSTEM,
        ]
        assert await test.execute_host()
        assert await test.execute_system()


async def test_free_space(coresys: CoreSys):
    """Test the free_space decorator."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys

        @Job(name="test_free_space_execute", conditions=[JobCondition.FREE_SPACE])
        async def execute(self):
            """Execute the class method."""
            return True

    test = TestClass(coresys)
    with patch("shutil.disk_usage", return_value=(42, 42, (1024.0**3))):
        assert await test.execute()

    with patch("shutil.disk_usage", return_value=(42, 42, (512.0**3))):
        assert not await test.execute()

        coresys.jobs.ignore_conditions = [JobCondition.FREE_SPACE]
        assert await test.execute()


async def test_haos(coresys: CoreSys):
    """Test the haos decorator."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys

        @Job(name="test_haos_execute", conditions=[JobCondition.HAOS])
        async def execute(self):
            """Execute the class method."""
            return True

    test = TestClass(coresys)
    with patch.object(OSManager, "available", new=PropertyMock(return_value=True)):
        assert await test.execute()

    with patch.object(OSManager, "available", new=PropertyMock(return_value=False)):
        assert not await test.execute()

    coresys.jobs.ignore_conditions = [JobCondition.HAOS]
    assert await test.execute()


async def test_exception(coresys: CoreSys, capture_exception: Mock):
    """Test handled exception."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys

        @Job(name="test_exception_execute", conditions=[JobCondition.HEALTHY])
        async def execute(self):
            """Execute the class method."""
            raise HassioError()

    test = TestClass(coresys)

    with pytest.raises(HassioError):
        assert await test.execute()

    capture_exception.assert_not_called()


async def test_exception_not_handle(coresys: CoreSys, capture_exception: Mock):
    """Test unhandled exception."""
    err = Exception()

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys

        @Job(
            name="test_exception_not_handle_execute", conditions=[JobCondition.HEALTHY]
        )
        async def execute(self):
            """Execute the class method."""
            raise err

    test = TestClass(coresys)

    with pytest.raises(JobException):
        assert await test.execute()

    capture_exception.assert_called_once_with(err)


async def test_running(coresys: CoreSys):
    """Test the running decorator."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys

        @Job(name="test_running_execute", conditions=[JobCondition.RUNNING])
        async def execute(self):
            """Execute the class method."""
            return True

    test = TestClass(coresys)

    await coresys.core.set_state(CoreState.RUNNING)
    assert await test.execute()

    await coresys.core.set_state(CoreState.FREEZE)
    assert not await test.execute()

    coresys.jobs.ignore_conditions = [JobCondition.RUNNING]
    assert await test.execute()


async def test_exception_conditions(coresys: CoreSys):
    """Test the on condition decorator."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys

        @Job(
            name="test_exception_conditions_execute",
            conditions=[JobCondition.RUNNING],
            on_condition=HassioError,
        )
        async def execute(self):
            """Execute the class method."""
            return True

    test = TestClass(coresys)

    await coresys.core.set_state(CoreState.RUNNING)
    assert await test.execute()

    await coresys.core.set_state(CoreState.FREEZE)
    with pytest.raises(HassioError):
        await test.execute()


async def test_concurrency_queue(coresys: CoreSys):
    """Test the queue job concurrency."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys
            self.run = asyncio.Lock()

        @Job(
            name="test_concurrency_queue_execute",
            concurrency=JobConcurrency.QUEUE,
        )
        async def execute(self, sleep: float):
            """Execute the class method."""
            assert not self.run.locked()
            async with self.run:
                await asyncio.sleep(sleep)

    test = TestClass(coresys)

    await asyncio.gather(*[test.execute(0.1), test.execute(0.1), test.execute(0.1)])


async def test_concurrency_queue_with_throttle(coresys: CoreSys):
    """Test the queue concurrency with throttle."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys
            self.run = asyncio.Lock()
            self.call = 0

        @Job(
            name="test_concurrency_queue_with_throttle_execute",
            concurrency=JobConcurrency.QUEUE,
            throttle=JobThrottle.THROTTLE,
            throttle_period=timedelta(hours=1),
        )
        async def execute(self, sleep: float):
            """Execute the class method."""
            assert not self.run.locked()
            async with self.run:
                await asyncio.sleep(sleep)
            self.call += 1

    test = TestClass(coresys)

    await asyncio.gather(*[test.execute(0.1), test.execute(0.1), test.execute(0.1)])
    assert test.call == 1

    await asyncio.gather(*[test.execute(0.1)])
    assert test.call == 1


@pytest.mark.parametrize("error", [None, PluginJobError])
async def test_throttle_rate_limit(coresys: CoreSys, error: JobException | None):
    """Test the throttle rate limit."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys
            self.run = asyncio.Lock()
            self.call = 0

        @Job(
            name=f"test_throttle_rate_limit_execute_{uuid4().hex}",
            throttle=JobThrottle.RATE_LIMIT,
            throttle_period=timedelta(hours=1),
            throttle_max_calls=2,
            on_condition=error,
        )
        async def execute(self):
            """Execute the class method."""
            self.call += 1

    test = TestClass(coresys)

    start = utcnow()

    with time_machine.travel(start):
        await asyncio.gather(*[test.execute(), test.execute()])
    assert test.call == 2

    with (
        time_machine.travel(start + timedelta(milliseconds=1)),
        pytest.raises(JobException if error is None else error),
    ):
        await test.execute()

    assert test.call == 2

    with time_machine.travel(start + timedelta(hours=1, milliseconds=1)):
        await test.execute()

    assert test.call == 3


async def test_throttle_basic(coresys: CoreSys):
    """Test the basic throttle functionality."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys
            self.run = asyncio.Lock()
            self.call = 0

        @Job(
            name="test_throttle_basic_execute",
            throttle=JobThrottle.THROTTLE,
            throttle_period=timedelta(hours=1),
        )
        async def execute(self, sleep: float):
            """Execute the class method."""
            assert not self.run.locked()
            async with self.run:
                await asyncio.sleep(sleep)
            self.call += 1

    test = TestClass(coresys)

    await asyncio.gather(*[test.execute(0.1), test.execute(0.1), test.execute(0.1)])
    assert test.call == 1

    await asyncio.gather(*[test.execute(0.1)])
    assert test.call == 1


async def test_concurrency_reject(coresys: CoreSys):
    """Test the reject concurrency."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys
            self.run = asyncio.Lock()

        @Job(
            name="test_concurrency_reject_execute",
            concurrency=JobConcurrency.REJECT,
            on_condition=JobException,
        )
        async def execute(self, sleep: float):
            """Execute the class method."""
            assert not self.run.locked()
            async with self.run:
                await asyncio.sleep(sleep)

    test = TestClass(coresys)
    run_task = asyncio.get_running_loop().create_task(test.execute(0.3))

    await asyncio.sleep(0.1)
    with pytest.raises(JobException):
        await test.execute(0.1)

    await run_task


async def test_supervisor_updated(coresys: CoreSys):
    """Test the supervisor updated decorator."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys

        @Job(
            name="test_supervisor_updated_execute",
            conditions=[JobCondition.SUPERVISOR_UPDATED],
        )
        async def execute(self) -> bool:
            """Execute the class method."""
            return True

    test = TestClass(coresys)
    assert not coresys.supervisor.need_update
    assert await test.execute()

    with patch.object(
        type(coresys.supervisor), "need_update", new=PropertyMock(return_value=True)
    ):
        assert not await test.execute()

        coresys.jobs.ignore_conditions = [JobCondition.SUPERVISOR_UPDATED]
        assert await test.execute()


async def test_plugins_updated(coresys: CoreSys):
    """Test the plugins updated decorator."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys

        @Job(
            name="test_plugins_updated_execute",
            conditions=[JobCondition.PLUGINS_UPDATED],
        )
        async def execute(self) -> bool:
            """Execute the class method."""
            return True

    test = TestClass(coresys)
    assert (
        len(
            [
                plugin.slug
                for plugin in coresys.plugins.all_plugins
                if plugin.need_update
            ]
        )
        == 0
    )
    assert await test.execute()

    with (
        patch.object(PluginAudio, "need_update", new=PropertyMock(return_value=True)),
        patch.object(
            PluginAudio,
            "update",
            side_effect=[AudioUpdateError, None, AudioUpdateError],
        ),
    ):
        assert not await test.execute()
        assert await test.execute()

        coresys.jobs.ignore_conditions = [JobCondition.PLUGINS_UPDATED]
        assert await test.execute()


async def test_auto_update(coresys: CoreSys):
    """Test the auto update decorator."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys

        @Job(name="test_auto_update_execute", conditions=[JobCondition.AUTO_UPDATE])
        async def execute(self) -> bool:
            """Execute the class method."""
            return True

    test = TestClass(coresys)
    assert coresys.updater.auto_update is True
    assert await test.execute()

    coresys.updater.auto_update = False
    assert not await test.execute()

    coresys.jobs.ignore_conditions = [JobCondition.AUTO_UPDATE]
    assert await test.execute()


async def test_os_agent(coresys: CoreSys):
    """Test the os agent decorator."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys

        @Job(name="test_os_agent_execute", conditions=[JobCondition.OS_AGENT])
        async def execute(self) -> bool:
            """Execute the class method."""
            return True

    test = TestClass(coresys)
    with patch.object(
        HostManager, "supported_features", return_value=[HostFeature.OS_AGENT]
    ):
        assert await test.execute()

    coresys.host.supported_features.cache_clear()
    with patch.object(HostManager, "supported_features", return_value=[]):
        assert not await test.execute()

        coresys.jobs.ignore_conditions = [JobCondition.OS_AGENT]
        assert await test.execute()


async def test_host_network(coresys: CoreSys):
    """Test the host network decorator."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys

        @Job(name="test_host_network_execute", conditions=[JobCondition.HOST_NETWORK])
        async def execute(self) -> bool:
            """Execute the class method."""
            return True

    test = TestClass(coresys)
    assert await test.execute()

    coresys.dbus.network.disconnect()
    assert not await test.execute()

    coresys.jobs.ignore_conditions = [JobCondition.HOST_NETWORK]
    assert await test.execute()


async def test_job_group_reject(coresys: CoreSys):
    """Test job group reject concurrency limitation."""

    class TestClass(JobGroup):
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            super().__init__(coresys, "TestClass")
            self.event = asyncio.Event()

        @Job(
            name="test_job_group_reject_inner_execute",
            concurrency=JobConcurrency.GROUP_REJECT,
            on_condition=JobException,
        )
        async def inner_execute(self) -> bool:
            """Inner class method called by execute, group level lock allows this."""
            await self.event.wait()
            return True

        @Job(
            name="test_job_group_reject_execute",
            concurrency=JobConcurrency.GROUP_REJECT,
            on_condition=JobException,
        )
        async def execute(self) -> bool:
            """Execute the class method."""
            return await self.inner_execute()

        @Job(
            name="test_job_group_reject_separate_execute",
            concurrency=JobConcurrency.GROUP_REJECT,
            on_condition=JobException,
        )
        async def separate_execute(self) -> bool:
            """Alternate execute method that shares group lock."""
            return True

        @Job(
            name="test_job_group_reject_unrelated",
            concurrency=JobConcurrency.REJECT,
            on_condition=JobException,
        )
        async def unrelated_method(self) -> bool:
            """Unrelated method, sparate job with separate lock."""
            return True

    test = TestClass(coresys)
    run_task = asyncio.get_running_loop().create_task(test.execute())
    await asyncio.sleep(0)

    # All methods with group limits should be locked
    with pytest.raises(JobException):
        await test.execute()

    with pytest.raises(JobException):
        await test.inner_execute()

    with pytest.raises(JobException):
        await test.separate_execute()

    # The once method is still callable
    assert await test.unrelated_method()

    test.event.set()
    assert await run_task


async def test_job_group_queue(coresys: CoreSys):
    """Test job group queue concurrency limitation."""

    class TestClass(JobGroup):
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            super().__init__(coresys, "TestClass")
            self.execute_count = 0
            self.other_count = 0
            self.event = asyncio.Event()

        @Job(
            name="test_job_group_queue_inner_execute",
            concurrency=JobConcurrency.GROUP_QUEUE,
            on_condition=JobException,
        )
        async def inner_execute(self) -> None:
            """Inner class method called by execute, group level lock allows this."""
            self.execute_count += 1
            await self.event.wait()

        @Job(
            name="test_job_group_queue_execute",
            concurrency=JobConcurrency.GROUP_QUEUE,
            on_condition=JobException,
        )
        async def execute(self) -> None:
            """Execute the class method."""
            await self.inner_execute()

        @Job(
            name="test_job_group_queue_separate_execute",
            concurrency=JobConcurrency.GROUP_QUEUE,
            on_condition=JobException,
        )
        async def separate_execute(self) -> None:
            """Alternate execute method that shares group lock."""
            self.other_count += 1

    test = TestClass(coresys)
    event_loop = asyncio.get_running_loop()
    run_task = event_loop.create_task(test.execute())
    await asyncio.sleep(0)

    repeat_task = event_loop.create_task(test.execute())
    other_task = event_loop.create_task(test.separate_execute())
    await asyncio.sleep(0)

    assert test.execute_count == 1
    assert test.other_count == 0

    test.event.set()
    await run_task
    await repeat_task
    await other_task

    assert test.execute_count == 2
    assert test.other_count == 1


async def test_job_cleanup(coresys: CoreSys):
    """Test job is cleaned up."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys
            self.event = asyncio.Event()
            self.job: SupervisorJob | None = None

        @Job(name="test_job_cleanup_execute", concurrency=JobConcurrency.REJECT)
        async def execute(self):
            """Execute the class method."""
            self.job = coresys.jobs.current
            await self.event.wait()
            return True

    test = TestClass(coresys)
    run_task = asyncio.get_running_loop().create_task(test.execute())
    await asyncio.sleep(0)

    assert coresys.jobs.jobs == [test.job]
    assert not test.job.done

    test.event.set()
    assert await run_task

    assert coresys.jobs.jobs == []
    assert test.job.done


async def test_job_skip_cleanup(coresys: CoreSys):
    """Test job is left in job manager when cleanup is false."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys
            self.event = asyncio.Event()
            self.job: SupervisorJob | None = None

        @Job(
            name="test_job_skip_cleanup_execute",
            concurrency=JobConcurrency.REJECT,
            cleanup=False,
        )
        async def execute(self):
            """Execute the class method."""
            self.job = coresys.jobs.current
            await self.event.wait()
            return True

    test = TestClass(coresys)
    run_task = asyncio.get_running_loop().create_task(test.execute())
    await asyncio.sleep(0)

    assert coresys.jobs.jobs == [test.job]
    assert not test.job.done

    test.event.set()
    assert await run_task

    assert coresys.jobs.jobs == [test.job]
    assert test.job.done


async def test_group_throttle(coresys: CoreSys):
    """Test the group throttle."""

    class TestClass(JobGroup):
        """Test class."""

        def __init__(self, coresys: CoreSys, reference: str):
            """Initialize the test class."""
            super().__init__(coresys, f"test_class_{reference}", reference)
            self.run = asyncio.Lock()
            self.call = 0

        @Job(
            name="test_group_throttle_execute",
            throttle=JobThrottle.GROUP_THROTTLE,
            throttle_period=timedelta(milliseconds=95),
        )
        async def execute(self, sleep: float):
            """Execute the class method."""
            assert not self.run.locked()
            async with self.run:
                await asyncio.sleep(sleep)
            self.call += 1

    test1 = TestClass(coresys, "test1")
    test2 = TestClass(coresys, "test2")

    start = utcnow()

    # One call of each should work. The subsequent calls will be silently throttled due to period
    with time_machine.travel(start):
        await asyncio.gather(
            test1.execute(0), test1.execute(0), test2.execute(0), test2.execute(0)
        )
    assert test1.call == 1
    assert test2.call == 1

    # First call to each will work again since period cleared. Second throttled once more as they don't wait
    with time_machine.travel(start + timedelta(milliseconds=100)):
        await asyncio.gather(
            test1.execute(0.1),
            test1.execute(0.1),
            test2.execute(0.1),
            test2.execute(0.1),
        )

    assert test1.call == 2
    assert test2.call == 2


async def test_group_throttle_with_queue(coresys: CoreSys):
    """Test the group throttle with queue concurrency."""

    class TestClass(JobGroup):
        """Test class."""

        def __init__(self, coresys: CoreSys, reference: str):
            """Initialize the test class."""
            super().__init__(coresys, f"test_class_{reference}", reference)
            self.run = asyncio.Lock()
            self.call = 0

        @Job(
            name="test_group_throttle_with_queue_execute",
            concurrency=JobConcurrency.QUEUE,
            throttle=JobThrottle.GROUP_THROTTLE,
            throttle_period=timedelta(milliseconds=95),
        )
        async def execute(self, sleep: float):
            """Execute the class method."""
            assert not self.run.locked()
            async with self.run:
                await asyncio.sleep(sleep)
            self.call += 1

    test1 = TestClass(coresys, "test1")
    test2 = TestClass(coresys, "test2")

    start = utcnow()

    # One call of each should work. The subsequent calls will be silently throttled after waiting due to period
    with time_machine.travel(start):
        await asyncio.gather(
            *[test1.execute(0), test1.execute(0), test2.execute(0), test2.execute(0)]
        )
    assert test1.call == 1
    assert test2.call == 1

    # All calls should work as we cleared the period. And tasks take longer then period and are queued
    with time_machine.travel(start + timedelta(milliseconds=100)):
        await asyncio.gather(
            *[
                test1.execute(0.1),
                test1.execute(0.1),
                test2.execute(0.1),
                test2.execute(0.1),
            ]
        )

    assert test1.call == 3
    assert test2.call == 3


@pytest.mark.parametrize("error", [None, PluginJobError])
async def test_group_throttle_rate_limit(coresys: CoreSys, error: JobException | None):
    """Test the group throttle rate limit."""

    class TestClass(JobGroup):
        """Test class."""

        def __init__(self, coresys: CoreSys, reference: str):
            """Initialize the test class."""
            super().__init__(coresys, f"test_class_{reference}", reference)
            self.run = asyncio.Lock()
            self.call = 0

        @Job(
            name=f"test_group_throttle_rate_limit_execute_{uuid4().hex}",
            throttle=JobThrottle.GROUP_RATE_LIMIT,
            throttle_period=timedelta(hours=1),
            throttle_max_calls=2,
            on_condition=error,
        )
        async def execute(self):
            """Execute the class method."""
            self.call += 1

    test1 = TestClass(coresys, "test1")
    test2 = TestClass(coresys, "test2")

    start = utcnow()

    with time_machine.travel(start):
        await asyncio.gather(
            *[test1.execute(), test1.execute(), test2.execute(), test2.execute()]
        )
    assert test1.call == 2
    assert test2.call == 2

    with time_machine.travel(start + timedelta(milliseconds=1)):
        with pytest.raises(JobException if error is None else error):
            await test1.execute()
        with pytest.raises(JobException if error is None else error):
            await test2.execute()

    assert test1.call == 2
    assert test2.call == 2

    with time_machine.travel(start + timedelta(hours=1, milliseconds=1)):
        await test1.execute()
        await test2.execute()

    assert test1.call == 3
    assert test2.call == 3


async def test_internal_jobs_no_notify(coresys: CoreSys, ha_ws_client: AsyncMock):
    """Test internal jobs do not send any notifications."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys

        @Job(name="test_internal_jobs_no_notify_internal", internal=True)
        async def execute_internal(self) -> bool:
            """Execute the class method."""
            return True

        @Job(name="test_internal_jobs_no_notify_default")
        async def execute_default(self) -> bool:
            """Execute the class method."""
            return True

    test1 = TestClass(coresys)

    await test1.execute_internal()
    await asyncio.sleep(0)
    ha_ws_client.async_send_command.assert_not_called()

    await test1.execute_default()
    await asyncio.sleep(0)
    assert ha_ws_client.async_send_command.call_count == 2
    ha_ws_client.async_send_command.assert_called_with(
        {
            "type": "supervisor/event",
            "data": {
                "event": "job",
                "data": {
                    "name": "test_internal_jobs_no_notify_default",
                    "reference": None,
                    "uuid": ANY,
                    "progress": 0,
                    "stage": None,
                    "done": True,
                    "parent_id": None,
                    "errors": [],
                    "created": ANY,
                    "extra": None,
                },
            },
        }
    )


async def test_job_starting_separate_task(coresys: CoreSys):
    """Test job that starts a job as a separate asyncio task."""

    class TestClass(JobGroup):
        """Test class."""

        def __init__(self, coresys: CoreSys) -> None:
            super().__init__(coresys, "test_class_locking")
            self.event = asyncio.Event()

        @Job(
            name="test_job_starting_separate_task_job_task",
            concurrency=JobConcurrency.GROUP_REJECT,
        )
        async def job_task(self):
            """Create a separate long running job task."""
            self.sys_jobs.current.stage = "launch_task"
            return self.sys_create_task(self.job_task_inner())

        @Job(name="test_job_starting_separate_task_job_task_inner")
        async def job_task_inner(self):
            """Check & update job and wait for release."""
            assert self.sys_jobs.current.parent_id is None
            self.sys_jobs.current.stage = "start"
            await self.event.wait()
            self.sys_jobs.current.stage = "end"

        @Job(name="test_job_starting_separate_task_release")
        async def job_release(self):
            """Release inner task."""
            self.event.set()

        @Job(
            name="test_job_starting_separate_task_job_await",
            concurrency=JobConcurrency.GROUP_REJECT,
        )
        async def job_await(self):
            """Await a simple job in same group to confirm lock released."""
            await self.job_await_inner()

        @Job(name="test_job_starting_separate_task_job_await_inner")
        async def job_await_inner(self):
            """Confirm there is a parent this way."""
            assert self.sys_jobs.current.parent_id is not None

    test = TestClass(coresys)

    task = await test.job_task()
    await asyncio.sleep(0)
    await test.job_await()
    await test.job_release()
    await task


async def test_job_always_removed_on_check_failure(coresys: CoreSys):
    """Test that the job instance is always removed if the condition or limit check fails."""

    class TestClass:
        """Test class."""

        event = asyncio.Event()
        limit_job: Job | None = None

        def __init__(self, coresys: CoreSys) -> None:
            """Initialize object."""
            self.coresys = coresys

        @Job(
            name="test_job_always_removed_on_check_failure_condition",
            conditions=[JobCondition.HAOS],
            on_condition=JobException,
            cleanup=False,
        )
        async def condition_check(self):
            """Job that will fail a condition check."""
            raise AssertionError("should not run")

        @Job(
            name="test_job_always_removed_on_check_failure_limit",
            concurrency=JobConcurrency.REJECT,
            cleanup=False,
        )
        async def limit_check(self):
            """Job that can fail a limit check."""
            self.limit_job = self.coresys.jobs.current
            await self.event.wait()

        def release_limit_check(self):
            """Release the limit check job."""
            self.event.set()

    test = TestClass(coresys)

    with pytest.raises(JobException):
        await test.condition_check()
    assert coresys.jobs.jobs == []

    task = coresys.create_task(test.limit_check())
    await asyncio.sleep(0)
    assert (job := test.limit_job)

    with pytest.raises(JobException):
        await test.limit_check()
    assert test.limit_job == job
    assert coresys.jobs.jobs == [job]

    test.release_limit_check()
    await task
    assert job.done
    assert coresys.jobs.jobs == [job]


async def test_job_scheduled_delay(coresys: CoreSys):
    """Test job that schedules a job to start after delay."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys) -> None:
            """Initialize object."""
            self.coresys = coresys

        @Job(name="test_job_scheduled_delay_job_scheduler")
        async def job_scheduler(self) -> tuple[SupervisorJob, asyncio.TimerHandle]:
            """Schedule a job to run after delay."""
            return self.coresys.jobs.schedule_job(
                self.job_task, JobSchedulerOptions(delayed_start=0.1)
            )

        @Job(name="test_job_scheduled_delay_job_task")
        async def job_task(self) -> None:
            """Do scheduled work."""
            self.coresys.jobs.current.stage = "work"

    test = TestClass(coresys)

    job, _ = await test.job_scheduler()
    started = False
    ended = False

    async def start_listener(evt_job: SupervisorJob):
        nonlocal started
        started = started or evt_job.uuid == job.uuid

    async def end_listener(evt_job: SupervisorJob):
        nonlocal ended
        ended = ended or evt_job.uuid == job.uuid

    coresys.bus.register_event(BusEvent.SUPERVISOR_JOB_START, start_listener)
    coresys.bus.register_event(BusEvent.SUPERVISOR_JOB_END, end_listener)

    await asyncio.sleep(0.2)

    assert started
    assert ended
    assert job.done
    assert job.name == "test_job_scheduled_delay_job_task"
    assert job.stage == "work"
    assert job.parent_id is None


async def test_job_scheduled_at(coresys: CoreSys):
    """Test job that schedules a job to start at a specified time."""
    dt = datetime.now()

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys) -> None:
            """Initialize object."""
            self.coresys = coresys

        @Job(name="test_job_scheduled_at_job_scheduler")
        async def job_scheduler(self) -> tuple[SupervisorJob, asyncio.TimerHandle]:
            """Schedule a job to run at specified time."""
            return self.coresys.jobs.schedule_job(
                self.job_task, JobSchedulerOptions(start_at=dt + timedelta(seconds=0.1))
            )

        @Job(name="test_job_scheduled_at_job_task")
        async def job_task(self) -> None:
            """Do scheduled work."""
            self.coresys.jobs.current.stage = "work"

    test = TestClass(coresys)
    job_started = asyncio.Event()
    job_ended = asyncio.Event()

    async def start_listener(evt_job: SupervisorJob):
        if evt_job.uuid == job.uuid:
            job_started.set()

    async def end_listener(evt_job: SupervisorJob):
        if evt_job.uuid == job.uuid:
            job_ended.set()

    async with time_machine.travel(dt):
        job, _ = await test.job_scheduler()

        coresys.bus.register_event(BusEvent.SUPERVISOR_JOB_START, start_listener)
        coresys.bus.register_event(BusEvent.SUPERVISOR_JOB_END, end_listener)

    # Advance time to exactly when job should start and wait for completion
    async with time_machine.travel(dt + timedelta(seconds=0.1)):
        await asyncio.wait_for(
            asyncio.gather(job_started.wait(), job_ended.wait()), timeout=1.0
        )

    assert job.done
    assert job.name == "test_job_scheduled_at_job_task"
    assert job.stage == "work"
    assert job.parent_id is None


async def test_concurency_reject_and_throttle(coresys: CoreSys):
    """Test the concurrency rejct and throttle job execution limit."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys
            self.run = asyncio.Lock()
            self.call = 0

        @Job(
            name="test_concurency_reject_and_throttle_execute",
            concurrency=JobConcurrency.REJECT,
            throttle=JobThrottle.THROTTLE,
            throttle_period=timedelta(hours=1),
        )
        async def execute(self, sleep: float):
            """Execute the class method."""
            assert not self.run.locked()
            async with self.run:
                await asyncio.sleep(sleep)
            self.call += 1

    test = TestClass(coresys)

    results = await asyncio.gather(
        *[test.execute(0.1), test.execute(0.1), test.execute(0.1)],
        return_exceptions=True,
    )
    assert results[0] is None
    assert isinstance(results[1], JobException)
    assert isinstance(results[2], JobException)
    assert test.call == 1

    await asyncio.gather(*[test.execute(0.1)])
    assert test.call == 1


@pytest.mark.parametrize("error", [None, PluginJobError])
async def test_concurency_reject_and_rate_limit(
    coresys: CoreSys, error: JobException | None
):
    """Test the concurrency rejct and rate limit job execution limit."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys
            self.run = asyncio.Lock()
            self.call = 0

        @Job(
            name=f"test_concurency_reject_and_rate_limit_execute_{uuid4().hex}",
            concurrency=JobConcurrency.REJECT,
            throttle=JobThrottle.RATE_LIMIT,
            throttle_period=timedelta(hours=1),
            throttle_max_calls=1,
            on_condition=error,
        )
        async def execute(self, sleep: float = 0):
            """Execute the class method."""
            async with self.run:
                await asyncio.sleep(sleep)
            self.call += 1

    test = TestClass(coresys)

    start = utcnow()

    with time_machine.travel(start):
        results = await asyncio.gather(
            *[test.execute(0.1), test.execute(), test.execute()], return_exceptions=True
        )
    assert results[0] is None
    assert isinstance(results[1], JobException)
    assert isinstance(results[2], JobException)
    assert test.call == 1

    with (
        time_machine.travel(start + timedelta(milliseconds=1)),
        pytest.raises(JobException if error is None else error),
    ):
        await test.execute()

    assert test.call == 1

    with time_machine.travel(start + timedelta(hours=1, milliseconds=1)):
        await test.execute()

    assert test.call == 2


async def test_group_concurrency_with_group_throttling(coresys: CoreSys):
    """Test that group concurrency works with group throttling."""

    class TestClass(JobGroup):
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            super().__init__(coresys, "TestGroupConcurrencyThrottle")
            self.call_count = 0
            self.nested_call_count = 0

        @Job(
            name="test_group_concurrency_throttle_main",
            concurrency=JobConcurrency.GROUP_QUEUE,
            throttle=JobThrottle.GROUP_THROTTLE,
            throttle_period=timedelta(milliseconds=50),
            on_condition=JobException,
        )
        async def main_method(self) -> None:
            """Make nested call with group concurrency and throttling."""
            self.call_count += 1
            # Test nested call to ensure lock handling works
            await self.nested_method()

        @Job(
            name="test_group_concurrency_throttle_nested",
            concurrency=JobConcurrency.GROUP_QUEUE,
            throttle=JobThrottle.GROUP_THROTTLE,
            throttle_period=timedelta(milliseconds=50),
            on_condition=JobException,
        )
        async def nested_method(self) -> None:
            """Nested method with group concurrency and throttling."""
            self.nested_call_count += 1

    test = TestClass(coresys)

    start = utcnow()

    # First call should work
    with time_machine.travel(start):
        await test.main_method()
    assert test.call_count == 1
    assert test.nested_call_count == 1

    # Second call should be throttled (not execute due to throttle period)
    with time_machine.travel(start + timedelta(milliseconds=1)):
        await test.main_method()
    assert test.call_count == 1  # Still 1, throttled
    assert test.nested_call_count == 1  # Still 1, throttled

    # Wait for throttle period to pass and try again
    with time_machine.travel(start + timedelta(milliseconds=60)):
        await test.main_method()

    assert test.call_count == 2  # Should execute now
    assert test.nested_call_count == 2  # Nested call should also execute


async def test_core_supported(coresys: CoreSys, caplog: pytest.LogCaptureFixture):
    """Test the core_supported decorator."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys

        @Job(
            name="test_core_supported_execute", conditions=[JobCondition.CORE_SUPPORTED]
        )
        async def execute(self):
            """Execute the class method."""
            return True

    test = TestClass(coresys)
    assert await test.execute()

    coresys.resolution.unsupported.append(UnsupportedReason.CORE_VERSION)
    assert not await test.execute()
    assert (
        "blocked from execution, unsupported Home Assistant Core version" in caplog.text
    )

    coresys.jobs.ignore_conditions = [JobCondition.CORE_SUPPORTED]
    assert await test.execute()
