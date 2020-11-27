"""Test the job context vars."""

from supervisor.coresys import CoreSys
from supervisor.jobs.decorator import Job


async def test_job_context(coresys: CoreSys):
    """Test the job context."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys
            self.jobid = str(self.coresys.jobs.job.id)

        @Job()
        async def first(self):
            """Execute the class method."""
            await self.second()
            return True

        @Job()
        async def second(self):
            """Execute the class method."""
            return True

    test = TestClass(coresys)
    await test.first()
    assert test.jobid == coresys.jobs.job.id
    await test.second()
    assert test.jobid == coresys.jobs.job.id
