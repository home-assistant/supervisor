"""Test the condition decorators."""

import asyncio
import gc
from unittest.mock import ANY, AsyncMock, patch

import pytest

from supervisor.coresys import CoreSys
from supervisor.exceptions import HassioError, JobStartException
from supervisor.jobs import JobSchedulerOptions
from supervisor.jobs.decorator import Job

TEST_JOB = "test"


async def test_add_job(coresys: CoreSys):
    """Test adding jobs."""
    job = coresys.jobs.new_job(TEST_JOB)

    assert job in coresys.jobs.jobs


async def test_remove_job_directly(coresys: CoreSys, caplog: pytest.LogCaptureFixture):
    """Test removing jobs  from manager."""
    job = coresys.jobs.new_job(TEST_JOB)
    assert job in coresys.jobs.jobs

    coresys.jobs.remove_job(job)
    assert job not in coresys.jobs.jobs
    assert f"Removing incomplete job {job.name}" not in caplog.text

    job = coresys.jobs.new_job(TEST_JOB)
    assert job in coresys.jobs.jobs

    with job.start():
        coresys.jobs.remove_job(job)
        assert job not in coresys.jobs.jobs
        assert f"Removing incomplete job {job.name}" in caplog.text


async def test_job_done(coresys: CoreSys):
    """Test done set correctly with jobs."""
    job = coresys.jobs.new_job(TEST_JOB)
    assert not job.done
    assert not coresys.jobs.is_job

    with job.start():
        assert coresys.jobs.is_job
        assert coresys.jobs.current == job
        assert not job.done

    assert not coresys.jobs.is_job
    assert job.done

    with pytest.raises(JobStartException), job.start():
        pass


async def test_job_start_bad_parent(coresys: CoreSys):
    """Test job cannot be started outside of parent."""
    job = coresys.jobs.new_job(TEST_JOB)
    job2 = coresys.jobs.new_job(f"{TEST_JOB}_2")

    with job.start(), pytest.raises(JobStartException), job2.start():
        pass

    with job2.start():
        assert coresys.jobs.current == job2


async def test_update_job(coresys: CoreSys):
    """Test updating jobs."""
    job = coresys.jobs.new_job(TEST_JOB)

    job.progress = 50
    assert job.progress == 50

    job.stage = "stage"
    assert job.stage == "stage"

    with pytest.raises(ValueError, match="must be <= 100"):
        job.progress = 110

    with pytest.raises(ValueError, match="must be >= 0"):
        job.progress = -10


async def test_notify_on_change(coresys: CoreSys, ha_ws_client: AsyncMock):
    """Test jobs notify Home Assistant on changes."""
    job = coresys.jobs.new_job(TEST_JOB)

    job.progress = 50
    await asyncio.sleep(0)
    # pylint: disable=protected-access
    ha_ws_client.async_send_command.assert_called_with(
        {
            "type": "supervisor/event",
            "data": {
                "event": "job",
                "data": {
                    "name": TEST_JOB,
                    "reference": None,
                    "uuid": ANY,
                    "progress": 50,
                    "stage": None,
                    "done": None,
                    "parent_id": None,
                    "errors": [],
                    "created": ANY,
                    "extra": None,
                },
            },
        }
    )

    job.stage = "test"
    await asyncio.sleep(0)
    ha_ws_client.async_send_command.assert_called_with(
        {
            "type": "supervisor/event",
            "data": {
                "event": "job",
                "data": {
                    "name": TEST_JOB,
                    "reference": None,
                    "uuid": ANY,
                    "progress": 50,
                    "stage": "test",
                    "done": None,
                    "parent_id": None,
                    "errors": [],
                    "created": ANY,
                    "extra": None,
                },
            },
        }
    )

    job.reference = "test"
    await asyncio.sleep(0)
    ha_ws_client.async_send_command.assert_called_with(
        {
            "type": "supervisor/event",
            "data": {
                "event": "job",
                "data": {
                    "name": TEST_JOB,
                    "reference": "test",
                    "uuid": ANY,
                    "progress": 50,
                    "stage": "test",
                    "done": None,
                    "parent_id": None,
                    "errors": [],
                    "created": ANY,
                    "extra": None,
                },
            },
        }
    )

    with job.start():
        await asyncio.sleep(0)
        ha_ws_client.async_send_command.assert_called_with(
            {
                "type": "supervisor/event",
                "data": {
                    "event": "job",
                    "data": {
                        "name": TEST_JOB,
                        "reference": "test",
                        "uuid": ANY,
                        "progress": 50,
                        "stage": "test",
                        "done": False,
                        "parent_id": None,
                        "errors": [],
                        "created": ANY,
                        "extra": None,
                    },
                },
            }
        )

        job.capture_error()
        await asyncio.sleep(0)
        ha_ws_client.async_send_command.assert_called_with(
            {
                "type": "supervisor/event",
                "data": {
                    "event": "job",
                    "data": {
                        "name": TEST_JOB,
                        "reference": "test",
                        "uuid": ANY,
                        "progress": 50,
                        "stage": "test",
                        "done": False,
                        "parent_id": None,
                        "errors": [
                            {
                                "type": "HassioError",
                                "message": "Unknown error, see Supervisor logs",
                                "stage": "test",
                                "error_key": None,
                                "extra_fields": None,
                            }
                        ],
                        "created": ANY,
                        "extra": None,
                    },
                },
            }
        )

    await asyncio.sleep(0)
    ha_ws_client.async_send_command.assert_called_with(
        {
            "type": "supervisor/event",
            "data": {
                "event": "job",
                "data": {
                    "name": TEST_JOB,
                    "reference": "test",
                    "uuid": ANY,
                    "progress": 100,
                    "stage": "test",
                    "done": True,
                    "parent_id": None,
                    "errors": [
                        {
                            "type": "HassioError",
                            "message": "Unknown error, see Supervisor logs",
                            "stage": "test",
                            "error_key": None,
                            "extra_fields": None,
                        }
                    ],
                    "created": ANY,
                    "extra": None,
                },
            },
        }
    )
    # pylint: enable=protected-access


async def test_schedule_job_unawaited_error_is_retrieved(
    coresys: CoreSys, caplog: pytest.LogCaptureFixture
):
    """Test a failed scheduled task nobody awaits is logged once, not reported by asyncio."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys

        @Job(name="test_schedule_job_unawaited_error_is_retrieved_execute")
        async def execute(self) -> None:
            """Execute the class method."""
            raise HassioError("boom")

    test = TestClass(coresys)
    with patch("asyncio.base_events.logger") as asyncio_logger:
        job, task = coresys.jobs.schedule_job(test.execute, JobSchedulerOptions())
        await asyncio.sleep(0)
        assert task.done()
        # The done callback runs on the next loop iteration
        await asyncio.sleep(0)
        del task
        gc.collect()

    asyncio_logger.error.assert_not_called()
    assert job.done
    assert (
        "Scheduled job test_schedule_job_unawaited_error_is_retrieved_execute failed: boom"
        in caplog.text
    )


async def test_schedule_job_awaited_error_is_raised(coresys: CoreSys):
    """Test a caller awaiting a scheduled task still receives the exception."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys

        @Job(name="test_schedule_job_awaited_error_is_raised_execute")
        async def execute(self) -> None:
            """Execute the class method."""
            raise HassioError("boom")

    test = TestClass(coresys)
    _, task = coresys.jobs.schedule_job(test.execute, JobSchedulerOptions())
    with pytest.raises(HassioError, match="boom"):
        await task
