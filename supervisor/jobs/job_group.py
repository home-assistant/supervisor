"""Job group object."""

from asyncio import Lock

from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import JobException, JobGroupExecutionLimitExceeded
from . import SupervisorJob


class JobGroup(CoreSysAttributes):
    """Object with methods that require a common lock.

    This is used in classes like our DockerInterface class. Where each method
    requires a lock as it involves some extensive I/O with Docker. But some
    methods may need to call others as a part of processing to complete a
    higher-level task and should not need to relinquish the lock in between.
    """

    def __init__(
        self, coresys: CoreSys, group_name: str, job_reference: str | None = None
    ) -> None:
        """Initialize object."""
        self.coresys: CoreSys = coresys
        self._group_name: str = group_name
        self._lock: Lock = Lock()
        self._lock_owner: SupervisorJob | None = None
        self._parent_jobs: list[SupervisorJob] = []
        self._job_reference: str | None = job_reference

    @property
    def active_job(self) -> SupervisorJob | None:
        """Get active job ID."""
        return self._lock_owner

    @property
    def group_name(self) -> str:
        """Return group name."""
        return self._group_name

    @property
    def has_lock(self) -> bool:
        """Return true if current task has the lock on this job group."""
        if not self._lock_owner:
            return False

        if not self.sys_jobs.is_job:
            return False

        current_job = self.sys_jobs.current
        # Check if current job owns lock directly
        return current_job == self._lock_owner

    @property
    def job_reference(self) -> str | None:
        """Return value to use as reference for all jobs created for this job group."""
        return self._job_reference

    def is_locked_by(self, job: SupervisorJob) -> bool:
        """Check if this specific job owns the lock."""
        return self._lock_owner == job

    async def acquire(self, job: SupervisorJob, wait: bool = False) -> None:
        """Acquire the lock for the group for the specified job."""
        # If we already own the lock (nested call or same job chain), just update parent stack
        if self.has_lock:
            if self._lock_owner:
                self._parent_jobs.append(self._lock_owner)
            self._lock_owner = job
            return

        # If there's another job running and we're not waiting, raise
        if self._lock_owner and not wait:
            raise JobGroupExecutionLimitExceeded(
                f"Another job is running for job group {self.group_name}"
            )

        # Acquire the actual asyncio lock
        await self._lock.acquire()

        # Set ownership
        self._lock_owner = job

    def release(self, job: SupervisorJob) -> None:
        """Release the lock for the group or return it to parent."""
        if not self.is_locked_by(job):
            raise JobException(f"Job {job.uuid} does not own the lock")

        # Return to parent job if exists
        if self._parent_jobs:
            self._lock_owner = self._parent_jobs.pop()
        else:
            self._lock_owner = None
            self._lock.release()
