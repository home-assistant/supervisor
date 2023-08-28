"""Test the condition decorators."""

import asyncio
from unittest.mock import ANY

import pytest

# pylint: disable=protected-access,import-error
from supervisor.coresys import CoreSys
from supervisor.exceptions import JobStartException

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

    with pytest.raises(JobStartException):
        with job.start():
            pass


async def test_job_start_bad_parent(coresys: CoreSys):
    """Test job cannot be started outside of parent."""
    job = coresys.jobs.new_job(TEST_JOB)
    job2 = coresys.jobs.new_job(f"{TEST_JOB}_2")

    with job.start():
        with pytest.raises(JobStartException):
            with job2.start():
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

    with pytest.raises(ValueError):
        job.progress = 110

    with pytest.raises(ValueError):
        job.progress = -10


async def test_notify_on_change(coresys: CoreSys):
    """Test jobs notify Home Assistant on changes."""
    job = coresys.jobs.new_job(TEST_JOB)

    job.progress = 50
    await asyncio.sleep(0)
    coresys.homeassistant.websocket._client.async_send_command.assert_called_with(
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
                },
            },
        }
    )

    job.stage = "test"
    await asyncio.sleep(0)
    coresys.homeassistant.websocket._client.async_send_command.assert_called_with(
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
                },
            },
        }
    )

    job.reference = "test"
    await asyncio.sleep(0)
    coresys.homeassistant.websocket._client.async_send_command.assert_called_with(
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
                },
            },
        }
    )

    with job.start():
        await asyncio.sleep(0)
        coresys.homeassistant.websocket._client.async_send_command.assert_called_with(
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
                    },
                },
            }
        )

    await asyncio.sleep(0)
    coresys.homeassistant.websocket._client.async_send_command.assert_called_with(
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
                    "done": True,
                    "parent_id": None,
                },
            },
        }
    )
