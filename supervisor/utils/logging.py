"""Logging utilities."""

from __future__ import annotations

import logging
import logging.handlers
import queue
from typing import Any

from logging_journald import Facility, JournaldLogHandler


class AddonLoggerAdapter(logging.LoggerAdapter):
    """Logging Adapter which prepends log entries with add-on name."""

    def process(self, msg, kwargs):
        """Process the logging message by prepending the add-on name."""
        return f"[{self.extra['addon_name']}] {msg}", kwargs


class SupervisorQueueHandler(logging.handlers.QueueHandler):
    """Process the log in another thread."""

    listener: logging.handlers.QueueListener | None = None

    def prepare(self, record: logging.LogRecord) -> logging.LogRecord:
        """Prepare a record for queuing.

        This is added as a workaround for https://bugs.python.org/issue46755
        """
        record = super().prepare(record)
        record.stack_info = None
        return record

    def handle(self, record: logging.LogRecord) -> Any:
        """Conditionally emit the specified logging record.

        Depending on which filters have been added to the handler, push the new
        records onto the backing Queue.

        The default python logger Handler acquires a lock
        in the parent class which we do not need as
        SimpleQueue is already thread safe.

        See https://bugs.python.org/issue24645
        """
        return_value = self.filter(record)
        if return_value:
            self.emit(record)
        return return_value

    def close(self) -> None:
        """Tidy up any resources used by the handler.

        This adds shutdown of the QueueListener
        """
        super().close()
        if not self.listener:
            return
        self.listener.stop()
        self.listener = None


class HAOSLogHandler(JournaldLogHandler):
    """Log handler for writing logs to the Home Assistant OS Systemd Journal."""

    SYSLOG_FACILITY = Facility.LOCAL7

    def __init__(self, identifier: str | None = None) -> None:
        """Initialize the HAOS log handler."""
        super().__init__(identifier=identifier, facility=HAOSLogHandler.SYSLOG_FACILITY)
        self._container_id = self._get_container_id()

    @staticmethod
    def _get_container_id() -> str | None:
        """Get the container ID if running inside a Docker container."""
        # Currently we only have this hacky way of getting the container ID,
        # we (probably) cannot get it without having some cgroup namespaces
        # mounted in the container or passed it there using other means.
        # Not obtaining it will only result in the logs not being available
        # through `docker logs` command, so it is not a critical issue.
        with open("/proc/self/mountinfo") as f:
            for line in f:
                if "/docker/containers/" in line:
                    container_id = line.split("/docker/containers/")[-1]
                    return container_id.split("/")[0]
        return None

    @classmethod
    def is_available(cls) -> bool:
        """Check if the HAOS log handler can be used."""
        return cls.SOCKET_PATH.exists()

    def emit(self, record: logging.LogRecord) -> None:
        """Emit formatted log record to the Systemd Journal.

        If CONTAINER_ID is known, add it to the fields to make the log record
        available through `docker logs` command.
        """
        try:
            formatted = self._format_record(record)
            if self._container_id:
                # only container ID is needed for interpretation through `docker logs`
                formatted.append(("CONTAINER_ID", self._container_id))
            self.transport.send(formatted)
        except Exception:
            self._fallback(record)


def activate_log_queue_handler() -> None:
    """Migrate the existing log handlers to use the queue.

    This allows us to avoid blocking I/O and formatting messages
    in the event loop as log messages are written in another thread.
    """
    simple_queue: queue.SimpleQueue[logging.Handler] = queue.SimpleQueue()
    queue_handler = SupervisorQueueHandler(simple_queue)
    logging.root.addHandler(queue_handler)

    migrated_handlers: list[logging.Handler] = []
    for handler in logging.root.handlers[:]:
        if handler is queue_handler:
            continue
        logging.root.removeHandler(handler)
        migrated_handlers.append(handler)

    listener = logging.handlers.QueueListener(simple_queue, *migrated_handlers)
    queue_handler.listener = listener

    listener.start()
