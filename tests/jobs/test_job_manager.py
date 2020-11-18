"""Test the condition decorators."""
# pylint: disable=protected-access,import-error
from supervisor.coresys import CoreSys

TEST_JOB = "test"


async def test_add_job(coresys: CoreSys):
    """Test adding jobs."""
    job = coresys.jobs.get_job(TEST_JOB)

    assert job.name in coresys.jobs.jobs


async def test_remove_job_directly(coresys: CoreSys):
    """Test removing jobs  from manager."""
    job = coresys.jobs.get_job(TEST_JOB)

    assert job.name in coresys.jobs.jobs
    coresys.jobs.remove_job(job)
    assert job.name not in coresys.jobs.jobs


async def test_remove_job_with_progress(coresys: CoreSys):
    """Test removing jobs by setting progress to 100."""
    job = coresys.jobs.get_job(TEST_JOB)

    assert job.name in coresys.jobs.jobs
    job.update(progress=100)
    assert job.name not in coresys.jobs.jobs


async def test_update_job(coresys: CoreSys):
    """Test updating jobs."""
    job = coresys.jobs.get_job(TEST_JOB)

    job.update(progress=50, stage="stage")
    assert job.progress == 50
    assert job.stage == "stage"
