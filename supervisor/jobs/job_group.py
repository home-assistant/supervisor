"""Job group object."""

from asyncio import Lock
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

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
        self._lock_owner: str | None = None
        self._parent_jobs: list[str] = []
        self._job_reference: str | None = job_reference

    @property
    def active_job_id(self) -> str | None:
        """Get active job UUID."""
        return self._lock_owner

    @property
    def active_job(self) -> SupervisorJob | None:
        """Get active job ID."""
        if self._lock_owner:
            try:
                return self.sys_jobs.get_job(self._lock_owner)
            except Exception:
                return None
        return None

    @property
    def group_name(self) -> str:
        """Return group name."""
        return self._group_name

    @property
    def has_lock(self) -> bool:
        """Return true if current task has the lock on this job group."""
        if not self._lock_owner:
            return False

        if self.sys_jobs.is_job:
            current_job = self.sys_jobs.current
            return current_job.uuid == self._lock_owner

        return False

    @property
    def job_reference(self) -> str | None:
        """Return value to use as reference for all jobs created for this job group."""
        return self._job_reference

    def is_locked_by(self, job: SupervisorJob) -> bool:
        """Check if this specific job owns the lock."""
        return self._lock_owner == job.uuid

    def can_acquire(self, job: SupervisorJob) -> bool:
        """Check if the job can acquire the lock without waiting."""
        return not self._lock_owner or self.is_locked_by(job)

    async def acquire(self, job: SupervisorJob, wait: bool = False) -> None:
        """Acquire the lock for the group for the specified job."""
        # If we already own the lock (nested call), just update parent stack
        if self.is_locked_by(job):
            if self._lock_owner:
                self._parent_jobs.append(self._lock_owner)
            self._lock_owner = job.uuid
            return

        # If there's another job running and we're not waiting, raise
        if self._lock_owner and not wait:
            raise JobGroupExecutionLimitExceeded(
                f"Another job is running for job group {self.group_name}"
            )

        # Acquire the actual asyncio lock
        await self._lock.acquire()

        # Set ownership
        self._lock_owner = job.uuid

    def release(self, job: SupervisorJob | None = None) -> None:
        """Release the lock for the group or return it to parent."""
        # Allow release by specific job UUID or current job
        if job and not self.is_locked_by(job):
            raise JobException(f"Job {job.uuid} does not own the lock")
        elif not job and not self.has_lock:
            raise JobException("Current context does not own the lock")

        # Return to parent job if exists
        if self._parent_jobs:
            self._lock_owner = self._parent_jobs.pop()
        else:
            self._lock_owner = None
            self._lock.release()

    def force_release(self) -> None:
        """Force release the lock (for cleanup/error scenarios)."""
        if self._lock.locked():
            self._lock_owner = None
            self._parent_jobs.clear()
            self._lock.release()

    @asynccontextmanager
    async def acquire_context(
        self, job: SupervisorJob, wait: bool = False
    ) -> AsyncIterator[None]:
        """Context manager for acquiring and automatically releasing the lock."""
        await self.acquire(job, wait=wait)
        try:
            yield
        finally:
            self.release(job)
