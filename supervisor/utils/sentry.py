"""Utilities for sentry."""

import asyncio
from functools import partial
import logging

from aiohttp.web_exceptions import HTTPBadGateway, HTTPServiceUnavailable
import sentry_sdk
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from sentry_sdk.integrations.atexit import AtexitIntegration
from sentry_sdk.integrations.dedupe import DedupeIntegration
from sentry_sdk.integrations.excepthook import ExcepthookIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.threading import ThreadingIntegration
from sentry_sdk.scrubber import DEFAULT_DENYLIST, EventScrubber

from ..const import SUPERVISOR_VERSION
from ..coresys import CoreSys
from ..misc.filter import filter_data

_LOGGER: logging.Logger = logging.getLogger(__name__)

only_once_events: set[str] = set()


def init_sentry(coresys: CoreSys) -> None:
    """Initialize sentry client."""
    if not sentry_sdk.is_initialized():
        _LOGGER.info("Initializing Supervisor Sentry")
        denylist = DEFAULT_DENYLIST + ["psk", "ssid"]
        # Don't use AsyncioIntegration(). We commonly handle task exceptions
        # outside of tasks. This would cause exception we gracefully handle to
        # be captured by sentry.
        sentry_sdk.init(
            dsn="https://9c6ea70f49234442b4746e447b24747e@o427061.ingest.sentry.io/5370612",
            before_send=partial(filter_data, coresys),
            auto_enabling_integrations=False,
            default_integrations=False,
            event_scrubber=EventScrubber(denylist=denylist),
            integrations=[
                AioHttpIntegration(
                    failed_request_status_codes=frozenset(range(500, 600))
                    - set(
                        {
                            HTTPBadGateway.status_code,
                            HTTPServiceUnavailable.status_code,
                        }
                    )
                ),
                ExcepthookIntegration(),
                DedupeIntegration(),
                AtexitIntegration(),
                ThreadingIntegration(),
                LoggingIntegration(level=logging.INFO, event_level=logging.CRITICAL),
            ],
            release=SUPERVISOR_VERSION,
            max_breadcrumbs=30,
        )


def capture_exception(err: BaseException) -> None:
    """Capture an exception and send to sentry.

    Must be called in executor.
    """
    if sentry_sdk.is_initialized():
        sentry_sdk.capture_exception(err)


async def async_capture_exception(err: BaseException) -> None:
    """Capture an exception and send to sentry.

    Safe to call in event loop.
    """
    if sentry_sdk.is_initialized():
        await asyncio.get_running_loop().run_in_executor(
            None, sentry_sdk.capture_exception, err
        )


def close_sentry() -> None:
    """Close the current sentry client.

    This method is irreversible. A new client will have to be initialized to re-open connetion.
    """
    if sentry_sdk.is_initialized():
        _LOGGER.info("Closing connection to Supervisor Sentry")
        sentry_sdk.get_client().close()
