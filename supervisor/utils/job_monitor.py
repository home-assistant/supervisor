"""Monitoring class for Supervisor jobs."""
import asyncio
from contextlib import suppress

from supervisor.exceptions import HomeAssistantAPIError


class JobMonitor:
    """Monitoring class."""

    def __init__(self, api):
        self._api = api

    def send_progress(self, status):
        """Send job progress to core in background task."""
        asyncio.run_coroutine_threadsafe(
            self._async_send_progress(status), self._api.sys_loop,
        )

    async def _async_send_progress(self, status) -> None:
        with suppress(HomeAssistantAPIError):
            async with self._api.sys_homeassistant.make_request(
                "post", "api/events/hassio_progress", json=status, timeout=2,
            ):
                pass

