"""Test the condition decorators."""
# pylint: disable=protected-access,import-error
from supervisor.coresys import CoreSys

TEST_JOB = "test"


async def test_add_job(coresys: CoreSys):
    """Test adding jobs."""
    job = coresys.job.get_job(TEST_JOB)

    assert job.name in coresys.job.jobs


async def test_remove_job_directly(coresys: CoreSys):
    """Test removing jobs  from manager."""
    job = coresys.job.get_job(TEST_JOB)

    assert job.name in coresys.job.jobs
    coresys.job.remove_job(job)
    assert job.name not in coresys.job.jobs


async def test_remove_job_with_progress(coresys: CoreSys):
    """Test removing jobs by setting progress to 100."""
    job = coresys.job.get_job(TEST_JOB)

    assert job.name in coresys.job.jobs
    await job.update(progress=100)
    assert job.name not in coresys.job.jobs


async def test_update_job(coresys: CoreSys):
    """Test updating jobs."""
    job = coresys.job.get_job(TEST_JOB)

    await job.update(progress=50, stage="stage")
    assert job.progress == 50
    assert job.stage == "stage"
