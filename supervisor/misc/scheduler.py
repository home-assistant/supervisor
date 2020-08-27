"""Schedule for Supervisor."""
import asyncio
from datetime import date, datetime, time, timedelta
import logging
from typing import Awaitable, Callable, List, Optional, Union
from uuid import UUID, uuid4

import async_timeout
import attr

from ..const import CoreState
from ..coresys import CoreSys, CoreSysAttributes

_LOGGER: logging.Logger = logging.getLogger(__name__)


@attr.s(slots=True)
class _Task:
    """Task object."""

    id: UUID = attr.ib()
    coro_callback: Callable[..., Awaitable[None]] = attr.ib(eq=False)
    interval: Union[float, time] = attr.ib(eq=False)
    repeat: bool = attr.ib(eq=False)
    job: Optional[asyncio.tasks.Task] = attr.ib(eq=False)
    next: Optional[asyncio.TimerHandle] = attr.ib(eq=False)


class Scheduler(CoreSysAttributes):
    """Schedule task inside Supervisor."""

    def __init__(self, coresys: CoreSys):
        """Initialize task schedule."""
        self.coresys: CoreSys = coresys
        self._tasks: List[_Task] = []

    def register_task(
        self,
        coro_callback: Callable[..., Awaitable[None]],
        interval: Union[float, time],
        repeat: bool = True,
    ) -> UUID:
        """Schedule a coroutine.

        The coroutine need to be a callback without arguments.
        """
        task = _Task(uuid4(), coro_callback, interval, repeat, None, None)

        # Schedule task
        self._tasks.append(task)
        self._schedule_task(task)

        return task.id

    def _run_task(self, task: _Task) -> None:
        """Run a scheduled task."""

        async def _wrap_task():
            """Run schedule task and reschedule."""
            try:
                if self.sys_core.state == CoreState.RUNNING:
                    await task.coro_callback()
            finally:
                if task.repeat and self.sys_core.state != CoreState.STOPPING:
                    self._schedule_task(task)
                else:
                    self._tasks.remove(task)

        task.job = self.sys_create_task(_wrap_task())

    def _schedule_task(self, task: _Task) -> None:
        """Schedule a task on loop."""
        if isinstance(task.interval, (int, float)):
            task.next = self.sys_loop.call_later(task.interval, self._run_task, task)
        elif isinstance(task.interval, time):
            today = datetime.combine(date.today(), task.interval)
            tomorrow = datetime.combine(date.today() + timedelta(days=1), task.interval)

            # Check if we run it today or next day
            if today > datetime.today():
                calc = today
            else:
                calc = tomorrow

            task.next = self.sys_loop.call_at(calc.timestamp(), self._run_task, task)
        else:
            _LOGGER.critical(
                "Unknown interval %s (type: %s) for scheduler %s",
                task.interval,
                type(task.interval),
                task.id,
            )

    async def shutdown(self, timeout=10) -> None:
        """Shutdown all task inside the scheduler."""
        running: List[asyncio.tasks.Task] = []

        # Cancel next task / get running list
        _LOGGER.info("Shutdown scheduled tasks")
        for task in self._tasks:
            if task.next:
                task.next.cancel()
            if not task.job or task.job.done():
                continue
            running.append(task.job)
            task.job.cancel()

        if not running:
            return

        # Wait until all are shutdown
        try:
            async with async_timeout.timeout(timeout):
                await asyncio.wait(running)
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout while waiting for jobs shutdown")
