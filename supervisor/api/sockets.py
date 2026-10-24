"""Unix sockets the Supervisor API listens on."""

import logging
import os
from pathlib import PurePath

from aiohttp import web

from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import (
    APISocketAlreadyRegisteredError,
    APISocketListenError,
    APISocketPrepareError,
)
from ..jobs.const import JobConcurrency
from ..jobs.decorator import Job
from ..jobs.job_group import JobGroup
from ..utils.sockets import prepare_socket_dir

_LOGGER: logging.Logger = logging.getLogger(__name__)


def _socket_path(request: web.BaseRequest) -> str | None:
    """Return the path of the Unix socket a request arrived on."""
    if request.transport is None:
        return None
    # A Unix listener reports its bound path, a TCP listener a host/port tuple
    sockname = request.transport.get_extra_info("sockname")
    return sockname if isinstance(sockname, str) else None


def is_unix_socket_request(request: web.BaseRequest) -> bool:
    """Return True if the request arrived on a Unix socket."""
    return _socket_path(request) is not None


class SocketRegistry(JobGroup):
    """Unix sockets the API listens on, each identifying one principal."""

    def __init__(self, coresys: CoreSys, runner: web.BaseRunner) -> None:
        """Initialize the socket registry."""
        super().__init__(coresys, "api_sockets")
        self._runner: web.BaseRunner = runner
        self._sites: dict[str, web.UnixSite] = {}
        self._principals: dict[str, CoreSysAttributes] = {}

    @property
    def paths(self) -> list[str]:
        """Return paths of all registered sockets."""
        return list(self._sites)

    @Job(
        name="api_sockets_register",
        concurrency=JobConcurrency.GROUP_QUEUE,
        internal=True,
    )
    async def register(
        self,
        principal: CoreSysAttributes,
        path: PurePath,
        runner: web.BaseRunner | None = None,
    ) -> None:
        """Listen on a Unix socket and identify every request on it as principal."""
        key = path.as_posix()
        if key in self._sites:
            raise APISocketAlreadyRegisteredError(path=key)

        try:
            await self.sys_run_in_executor(prepare_socket_dir, path)
        except OSError as err:
            _LOGGER.error("Can't prepare path for API socket %s: %s", key, err)
            raise APISocketPrepareError(path=key) from err

        site = web.UnixSite(runner or self._runner, key)
        try:
            await site.start()
            # Mounts decide who can reach it, keep the mode strict like Core's
            await self.sys_run_in_executor(os.chmod, key, 0o600)
        except OSError as err:
            # The runner keeps a site whose start failed, drop it so a retry is clean
            await site.stop()
            _LOGGER.error("Can't listen on API socket %s: %s", key, err)
            raise APISocketListenError(path=key) from err

        self._sites[key] = site
        self._principals[key] = principal

    @Job(
        name="api_sockets_unregister",
        concurrency=JobConcurrency.GROUP_QUEUE,
        internal=True,
    )
    async def unregister(self, path: PurePath) -> None:
        """Stop listening on a Unix socket and remove its file."""
        key = path.as_posix()
        # Drop the principal first so lingering connections are rejected
        self._principals.pop(key, None)
        if site := self._sites.pop(key, None):
            await site.stop()

    def principal_for(self, request: web.BaseRequest) -> CoreSysAttributes | None:
        """Return the principal of the socket a request arrived on.

        None for a request on the TCP site or on a socket no longer registered.
        """
        if (path := _socket_path(request)) is None:
            return None
        return self._principals.get(path)

    @Job(
        name="api_sockets_stop_all",
        concurrency=JobConcurrency.GROUP_QUEUE,
        internal=True,
    )
    async def stop_all(self) -> None:
        """Stop listening on all registered sockets."""
        # One at a time, the group lock only passes down to one child job
        for key in self.paths:
            await self.unregister(PurePath(key))
