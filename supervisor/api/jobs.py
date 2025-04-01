"""Init file for Supervisor Jobs RESTful API."""

import logging
from typing import Any

from aiohttp import web
import voluptuous as vol

from ..coresys import CoreSysAttributes
from ..exceptions import APIError, APINotFound, JobNotFound
from ..jobs import SupervisorJob
from ..jobs.const import ATTR_IGNORE_CONDITIONS, JobCondition
from .const import ATTR_JOBS
from .utils import api_process, api_validate

_LOGGER: logging.Logger = logging.getLogger(__name__)

SCHEMA_OPTIONS = vol.Schema(
    {vol.Optional(ATTR_IGNORE_CONDITIONS): [vol.Coerce(JobCondition)]}
)


class APIJobs(CoreSysAttributes):
    """Handle RESTful API for OS functions."""

    def _extract_job(self, request: web.Request) -> SupervisorJob:
        """Extract job from request or raise."""
        try:
            return self.sys_jobs.get_job(request.match_info["uuid"])
        except JobNotFound:
            raise APINotFound("Job does not exist") from None

    def _list_jobs(self, start: SupervisorJob | None = None) -> list[dict[str, Any]]:
        """Return current job tree.

        Jobs are added to cache as they are created so by default they are in oldest to newest.
        This is correct ordering for child jobs as it makes logical sense to present those in
        the order they occurred within the parent. For the list as a whole, sort from newest
        to oldest as its likely any client is most interested in the newer ones.
        """
        # Initially sort oldest to newest so all child lists end up in correct order
        jobs_by_parent: dict[str | None, list[SupervisorJob]] = {}
        for job in sorted(self.sys_jobs.jobs):
            if job.internal:
                continue

            if job.parent_id not in jobs_by_parent:
                jobs_by_parent[job.parent_id] = [job]
            else:
                jobs_by_parent[job.parent_id].append(job)

        # After parent-child organization, sort the root jobs only from newest to oldest
        job_list: list[dict[str, Any]] = []
        queue: list[tuple[list[dict[str, Any]], SupervisorJob]] = (
            [(job_list, start)]
            if start
            else [
                (job_list, job)
                for job in sorted(jobs_by_parent.get(None, []), reverse=True)
            ]
        )

        while queue:
            (current_list, current_job) = queue.pop(0)
            child_jobs: list[dict[str, Any]] = []

            # We remove parent_id and instead use that info to represent jobs as a tree
            job_dict = current_job.as_dict() | {"child_jobs": child_jobs}
            job_dict.pop("parent_id")
            current_list.append(job_dict)

            if current_job.uuid in jobs_by_parent:
                queue.extend(
                    [
                        (child_jobs, job)
                        for job in jobs_by_parent.get(current_job.uuid, [])
                    ]
                )

        return job_list

    @api_process
    async def info(self, request: web.Request) -> dict[str, Any]:
        """Return JobManager information."""
        return {
            ATTR_IGNORE_CONDITIONS: self.sys_jobs.ignore_conditions,
            ATTR_JOBS: self._list_jobs(),
        }

    @api_process
    async def options(self, request: web.Request) -> None:
        """Set options for JobManager."""
        body = await api_validate(SCHEMA_OPTIONS, request)

        if ATTR_IGNORE_CONDITIONS in body:
            self.sys_jobs.ignore_conditions = body[ATTR_IGNORE_CONDITIONS]

        await self.sys_jobs.save_data()

        await self.sys_resolution.evaluate.evaluate_system()

    @api_process
    async def reset(self, request: web.Request) -> None:
        """Reset options for JobManager."""
        await self.sys_jobs.reset_data()

    @api_process
    async def job_info(self, request: web.Request) -> dict[str, Any]:
        """Get details of a job by ID."""
        job = self._extract_job(request)
        return self._list_jobs(job)[0]

    @api_process
    async def remove_job(self, request: web.Request) -> None:
        """Remove a completed job."""
        job = self._extract_job(request)

        if not job.done:
            raise APIError(f"Job {job.uuid} is not done!")

        self.sys_jobs.remove_job(job)
