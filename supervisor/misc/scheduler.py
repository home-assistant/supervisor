"""Schedule for Supervisor."""
from datetime import date, datetime, time, timedelta
import logging

from ..const import CoreStates
from ..coresys import CoreSys, CoreSysAttributes

_LOGGER: logging.Logger = logging.getLogger(__name__)

INTERVAL = "interval"
REPEAT = "repeat"
CALL = "callback"
TASK = "task"


class Scheduler(CoreSysAttributes):
    """Schedule task inside Supervisor."""

    def __init__(self, coresys: CoreSys):
        """Initialize task schedule."""
        self.coresys: CoreSys = coresys
        self._data = {}

    def register_task(self, coro_callback, interval, repeat=True):
        """Schedule a coroutine.

        The coroutine need to be a callback without arguments.
        """
        task_id = hash(coro_callback)

        # Generate data
        opts = {CALL: coro_callback, INTERVAL: interval, REPEAT: repeat}

        # Schedule task
        self._data[task_id] = opts
        self._schedule_task(interval, task_id)

        return task_id

    def _run_task(self, task_id):
        """Run a scheduled task."""
        data = self._data[task_id]

        if self.sys_core.state == CoreStates.RUNNING:
            self.sys_loop.create_task(data[CALL]())

        if data[REPEAT]:
            self._schedule_task(data[INTERVAL], task_id)
        else:
            self._data.pop(task_id)

    def _schedule_task(self, interval, task_id):
        """Schedule a task on loop."""
        if isinstance(interval, (int, float)):
            job = self.sys_loop.call_later(interval, self._run_task, task_id)
        elif isinstance(interval, time):
            today = datetime.combine(date.today(), interval)
            tomorrow = datetime.combine(date.today() + timedelta(days=1), interval)

            # Check if we run it today or next day
            if today > datetime.today():
                calc = today
            else:
                calc = tomorrow

            job = self.sys_loop.call_at(calc.timestamp(), self._run_task, task_id)
        else:
            _LOGGER.critical(
                "Unknown interval %s (type: %s) for scheduler %s",
                interval,
                type(interval),
                task_id,
            )

        # Store job
        self._data[task_id][TASK] = job
