"""Schedule for HassIO."""
import logging

_LOGGER = logging.getLogger(__name__)

SEC = 'seconds'
REPEAT = 'repeat'
CALL = 'callback'
TASK = 'task'


class Scheduler(object):
    """Schedule task inside HassIO."""

    def __init__(self, loop):
        """Initialize task schedule."""
        self.loop = loop
        self._data = {}
        self._stop = False

    def stop(self):
        """Stop to execute tasks in scheduler."""
        self._stop = True

    def register_task(self, coro_callback, seconds, repeat=True,
                      now=False):
        """Schedule a coroutine.

        The coroutien need to be a callback without arguments.
        """
        idx = hash(coro_callback)

        # generate data
        opts = {
            CALL: coro_callback,
            SEC: seconds,
            REPEAT: repeat,
        }
        self._data[idx] = opts

        # schedule task
        if now:
            self._run_task(idx)
        else:
            task = self.loop.call_later(seconds, self._run_task, idx)
            self._data[idx][TASK] = task

        return idx

    def _run_task(self, idx):
        """Run a scheduled task."""
        data = self._data.pop(idx)

        # stop execute tasks
        if self._stop:
            return

        self.loop.create_task(data[CALL]())

        if data[REPEAT]:
            task = self.loop.call_later(data[SEC], self._run_task, idx)
            data[TASK] = task
            self._data[idx] = data
