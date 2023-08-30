"""Test the condition decorators."""
# pylint: disable=protected-access,import-error
import asyncio
from datetime import timedelta
from unittest.mock import ANY, AsyncMock, Mock, PropertyMock, patch
from uuid import uuid4

from aiohttp.client_exceptions import ClientError
import pytest
import time_machine

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.exceptions import (
    AudioUpdateError,
    HassioError,
    JobException,
    PluginJobError,
)
from supervisor.host.const import HostFeature
from supervisor.host.manager import HostManager
from supervisor.jobs import SupervisorJob
from supervisor.jobs.const import JobExecutionLimit
from supervisor.jobs.decorator import Job, JobCondition
from supervisor.jobs.job_group import JobGroup
from supervisor.plugins.audio import PluginAudio
from supervisor.resolution.const import UnhealthyReason
from supervisor.utils.dt import utcnow


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

    coresys.resolution.unhealthy = UnhealthyReason.DOCKER
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
    coresys.core.state = CoreState.RUNNING

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
    with patch(
        "supervisor.utils.dbus.DBus.call_dbus", return_value=connectivity
    ), patch.object(
        CoreSys, "websession", new=PropertyMock(return_value=mock_websession)
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
    coresys.os._available = True
    assert await test.execute()

    coresys.os._available = False
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

    coresys.core.state = CoreState.RUNNING
    assert await test.execute()

    coresys.core.state = CoreState.FREEZE
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

    coresys.core.state = CoreState.RUNNING
    assert await test.execute()

    coresys.core.state = CoreState.FREEZE
    with pytest.raises(HassioError):
        await test.execute()


async def test_execution_limit_single_wait(
    coresys: CoreSys, loop: asyncio.BaseEventLoop
):
    """Test the single wait job execution limit."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys
            self.run = asyncio.Lock()

        @Job(
            name="test_execution_limit_single_wait_execute",
            limit=JobExecutionLimit.SINGLE_WAIT,
        )
        async def execute(self, sleep: float):
            """Execute the class method."""
            assert not self.run.locked()
            async with self.run:
                await asyncio.sleep(sleep)

    test = TestClass(coresys)

    await asyncio.gather(*[test.execute(0.1), test.execute(0.1), test.execute(0.1)])


async def test_execution_limit_throttle_wait(
    coresys: CoreSys, loop: asyncio.BaseEventLoop
):
    """Test the throttle wait job execution limit."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys
            self.run = asyncio.Lock()
            self.call = 0

        @Job(
            name="test_execution_limit_throttle_wait_execute",
            limit=JobExecutionLimit.THROTTLE_WAIT,
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
async def test_execution_limit_throttle_rate_limit(
    coresys: CoreSys, loop: asyncio.BaseEventLoop, error: JobException | None
):
    """Test the throttle wait job execution limit."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys
            self.run = asyncio.Lock()
            self.call = 0

        @Job(
            name=f"test_execution_limit_throttle_rate_limit_execute_{uuid4().hex}",
            limit=JobExecutionLimit.THROTTLE_RATE_LIMIT,
            throttle_period=timedelta(hours=1),
            throttle_max_calls=2,
            on_condition=error,
        )
        async def execute(self):
            """Execute the class method."""
            self.call += 1

    test = TestClass(coresys)

    await asyncio.gather(*[test.execute(), test.execute()])
    assert test.call == 2

    with pytest.raises(JobException if error is None else error):
        await test.execute()

    assert test.call == 2

    with time_machine.travel(utcnow() + timedelta(hours=1)):
        await test.execute()

    assert test.call == 3


async def test_execution_limit_throttle(coresys: CoreSys, loop: asyncio.BaseEventLoop):
    """Test the ignore conditions decorator."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys
            self.run = asyncio.Lock()
            self.call = 0

        @Job(
            name="test_execution_limit_throttle_execute",
            limit=JobExecutionLimit.THROTTLE,
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


async def test_execution_limit_once(coresys: CoreSys, loop: asyncio.BaseEventLoop):
    """Test the ignore conditions decorator."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys
            self.run = asyncio.Lock()

        @Job(
            name="test_execution_limit_once_execute",
            limit=JobExecutionLimit.ONCE,
            on_condition=JobException,
        )
        async def execute(self, sleep: float):
            """Execute the class method."""
            assert not self.run.locked()
            async with self.run:
                await asyncio.sleep(sleep)

    test = TestClass(coresys)
    run_task = loop.create_task(test.execute(0.3))

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
    assert 0 == len(
        [plugin.slug for plugin in coresys.plugins.all_plugins if plugin.need_update]
    )
    assert await test.execute()

    with patch.object(
        PluginAudio, "need_update", new=PropertyMock(return_value=True)
    ), patch.object(
        PluginAudio, "update", side_effect=[AudioUpdateError, None, AudioUpdateError]
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


async def test_job_group_once(coresys: CoreSys, loop: asyncio.BaseEventLoop):
    """Test job group once execution limitation."""

    class TestClass(JobGroup):
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            super().__init__(coresys, "TestClass")
            self.event = asyncio.Event()

        @Job(
            name="test_job_group_once_inner_execute",
            limit=JobExecutionLimit.GROUP_ONCE,
            on_condition=JobException,
        )
        async def inner_execute(self) -> bool:
            """Inner class method called by execute, group level lock allows this."""
            await self.event.wait()
            return True

        @Job(
            name="test_job_group_once_execute",
            limit=JobExecutionLimit.GROUP_ONCE,
            on_condition=JobException,
        )
        async def execute(self) -> bool:
            """Execute the class method."""
            return await self.inner_execute()

        @Job(
            name="test_job_group_once_separate_execute",
            limit=JobExecutionLimit.GROUP_ONCE,
            on_condition=JobException,
        )
        async def separate_execute(self) -> bool:
            """Alternate execute method that shares group lock."""
            return True

        @Job(
            name="test_job_group_once_unrelated",
            limit=JobExecutionLimit.ONCE,
            on_condition=JobException,
        )
        async def unrelated_method(self) -> bool:
            """Unrelated method, sparate job with separate lock."""
            return True

    test = TestClass(coresys)
    run_task = loop.create_task(test.execute())
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


async def test_job_group_wait(coresys: CoreSys, loop: asyncio.BaseEventLoop):
    """Test job group wait execution limitation."""

    class TestClass(JobGroup):
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            super().__init__(coresys, "TestClass")
            self.execute_count = 0
            self.other_count = 0
            self.event = asyncio.Event()

        @Job(
            name="test_job_group_wait_inner_execute",
            limit=JobExecutionLimit.GROUP_WAIT,
            on_condition=JobException,
        )
        async def inner_execute(self) -> None:
            """Inner class method called by execute, group level lock allows this."""
            self.execute_count += 1
            await self.event.wait()

        @Job(
            name="test_job_group_wait_execute",
            limit=JobExecutionLimit.GROUP_WAIT,
            on_condition=JobException,
        )
        async def execute(self) -> None:
            """Execute the class method."""
            await self.inner_execute()

        @Job(
            name="test_job_group_wait_separate_execute",
            limit=JobExecutionLimit.GROUP_WAIT,
            on_condition=JobException,
        )
        async def separate_execute(self) -> None:
            """Alternate execute method that shares group lock."""
            self.other_count += 1

    test = TestClass(coresys)
    run_task = loop.create_task(test.execute())
    await asyncio.sleep(0)

    repeat_task = loop.create_task(test.execute())
    other_task = loop.create_task(test.separate_execute())
    await asyncio.sleep(0)

    assert test.execute_count == 1
    assert test.other_count == 0

    test.event.set()
    await run_task
    await repeat_task
    await other_task

    assert test.execute_count == 2
    assert test.other_count == 1


async def test_job_cleanup(coresys: CoreSys, loop: asyncio.BaseEventLoop):
    """Test job is cleaned up."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys
            self.event = asyncio.Event()
            self.job: SupervisorJob | None = None

        @Job(name="test_job_cleanup_execute", limit=JobExecutionLimit.ONCE)
        async def execute(self):
            """Execute the class method."""
            self.job = coresys.jobs.current
            await self.event.wait()
            return True

    test = TestClass(coresys)
    run_task = loop.create_task(test.execute())
    await asyncio.sleep(0)

    assert coresys.jobs.jobs == [test.job]
    assert not test.job.done

    test.event.set()
    assert await run_task

    assert coresys.jobs.jobs == []
    assert test.job.done


async def test_job_skip_cleanup(coresys: CoreSys, loop: asyncio.BaseEventLoop):
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
            limit=JobExecutionLimit.ONCE,
            cleanup=False,
        )
        async def execute(self):
            """Execute the class method."""
            self.job = coresys.jobs.current
            await self.event.wait()
            return True

    test = TestClass(coresys)
    run_task = loop.create_task(test.execute())
    await asyncio.sleep(0)

    assert coresys.jobs.jobs == [test.job]
    assert not test.job.done

    test.event.set()
    assert await run_task

    assert coresys.jobs.jobs == [test.job]
    assert test.job.done


async def test_execution_limit_group_throttle(
    coresys: CoreSys, loop: asyncio.BaseEventLoop
):
    """Test the group throttle execution limit."""

    class TestClass(JobGroup):
        """Test class."""

        def __init__(self, coresys: CoreSys, reference: str):
            """Initialize the test class."""
            super().__init__(coresys, f"test_class_{reference}", reference)
            self.run = asyncio.Lock()
            self.call = 0

        @Job(
            name="test_execution_limit_group_throttle_execute",
            limit=JobExecutionLimit.GROUP_THROTTLE,
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

    # One call of each should work. The subsequent calls will be silently throttled due to period
    await asyncio.gather(
        test1.execute(0), test1.execute(0), test2.execute(0), test2.execute(0)
    )
    assert test1.call == 1
    assert test2.call == 1

    # First call to each will work again since period cleared. Second throttled once more as they don't wait
    with time_machine.travel(utcnow() + timedelta(milliseconds=100)):
        await asyncio.gather(
            test1.execute(0.1),
            test1.execute(0.1),
            test2.execute(0.1),
            test2.execute(0.1),
        )

    assert test1.call == 2
    assert test2.call == 2


async def test_execution_limit_group_throttle_wait(
    coresys: CoreSys, loop: asyncio.BaseEventLoop
):
    """Test the group throttle wait job execution limit."""

    class TestClass(JobGroup):
        """Test class."""

        def __init__(self, coresys: CoreSys, reference: str):
            """Initialize the test class."""
            super().__init__(coresys, f"test_class_{reference}", reference)
            self.run = asyncio.Lock()
            self.call = 0

        @Job(
            name="test_execution_limit_group_throttle_wait_execute",
            limit=JobExecutionLimit.GROUP_THROTTLE_WAIT,
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

    # One call of each should work. The subsequent calls will be silently throttled after waiting due to period
    await asyncio.gather(
        *[test1.execute(0), test1.execute(0), test2.execute(0), test2.execute(0)]
    )
    assert test1.call == 1
    assert test2.call == 1

    # All calls should work as we cleared the period. And tasks take longer then period and are queued
    with time_machine.travel(utcnow() + timedelta(milliseconds=100)):
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
async def test_execution_limit_group_throttle_rate_limit(
    coresys: CoreSys, loop: asyncio.BaseEventLoop, error: JobException | None
):
    """Test the group throttle rate limit job execution limit."""

    class TestClass(JobGroup):
        """Test class."""

        def __init__(self, coresys: CoreSys, reference: str):
            """Initialize the test class."""
            super().__init__(coresys, f"test_class_{reference}", reference)
            self.run = asyncio.Lock()
            self.call = 0

        @Job(
            name=f"test_execution_limit_group_throttle_rate_limit_execute_{uuid4().hex}",
            limit=JobExecutionLimit.GROUP_THROTTLE_RATE_LIMIT,
            throttle_period=timedelta(hours=1),
            throttle_max_calls=2,
            on_condition=error,
        )
        async def execute(self):
            """Execute the class method."""
            self.call += 1

    test1 = TestClass(coresys, "test1")
    test2 = TestClass(coresys, "test2")

    await asyncio.gather(
        *[test1.execute(), test1.execute(), test2.execute(), test2.execute()]
    )
    assert test1.call == 2
    assert test2.call == 2

    with pytest.raises(JobException if error is None else error):
        await test1.execute()
    with pytest.raises(JobException if error is None else error):
        await test2.execute()

    assert test1.call == 2
    assert test2.call == 2

    with time_machine.travel(utcnow() + timedelta(hours=1)):
        await test1.execute()
        await test2.execute()

    assert test1.call == 3
    assert test2.call == 3


async def test_internal_jobs_no_notify(coresys: CoreSys):
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
    client = coresys.homeassistant.websocket._client
    client.async_send_command.reset_mock()

    await test1.execute_internal()
    await asyncio.sleep(0)
    client.async_send_command.assert_not_called()

    await test1.execute_default()
    await asyncio.sleep(0)
    client.async_send_command.call_count == 2
    client.async_send_command.assert_called_with(
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
                },
            },
        }
    )
