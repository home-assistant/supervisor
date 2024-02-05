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
        self._active_job: SupervisorJob | None = None
        self._parent_jobs: list[SupervisorJob] = []
        self._job_reference: str | None = job_reference

    @property
    def active_job(self) -> SupervisorJob | None:
        """Get active job ID."""
        return self._active_job

    @property
    def group_name(self) -> str:
        """Return group name."""
        return self._group_name

    @property
    def has_lock(self) -> bool:
        """Return true if current task has the lock on this job group."""
        return (
            self.active_job
            and self.sys_jobs.is_job
            and self.active_job == self.sys_jobs.current
        )

    @property
    def job_reference(self) -> str | None:
        """Return value to use as reference for all jobs created for this job group."""
        return self._job_reference

    async def acquire(self, job: SupervisorJob, wait: bool = False) -> None:
        """Acquire the lock for the group for the specified job."""
        # If there's another job running and we're not waiting, raise
        if self.active_job and not self.has_lock and not wait:
            raise JobGroupExecutionLimitExceeded(
                f"Another job is running for job group {self.group_name}"
            )

        # Else if we don't have the lock, acquire it
        if not self.has_lock:
            await self._lock.acquire()

        # Store the job ID we acquired the lock for
        if self.active_job:
            self._parent_jobs.append(self.active_job)

        self._active_job = job

    def release(self) -> None:
        """Release the lock for the group or return it to parent."""
        if not self.has_lock:
            raise JobException("Cannot release as caller does not own lock")

        if self._parent_jobs:
            self._active_job = self._parent_jobs.pop()
        else:
            self._active_job = None
            self._lock.release()
