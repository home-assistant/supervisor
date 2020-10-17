"""Monitoring class for Supervisor jobs."""
import asyncio
from contextlib import suppress

from ..exceptions import HomeAssistantAPIError


class JobMonitor:
    """Monitoring class."""

    def __init__(self, api):
        self._api = api

    def send_progress(self, name, progress, buffer=None):
        """Send job progress to core in background task."""
        self._schedule_send("progress", {
            "name": name,
            "progress": progress,
            "buffer": buffer,
        })

    def _schedule_send(self, event, json, timeout=2):
        asyncio.run_coroutine_threadsafe(
            self._async_send(event, json, timeout),
            self._api.sys_loop,
        )

    async def _async_send(self, event, json, timeout) -> None:
        with suppress(HomeAssistantAPIError):
            async with self._api.sys_homeassistant.api.make_request(
                    "post", "api/events/hassio_" + event, json=json, timeout=timeout,
            ):
                pass
