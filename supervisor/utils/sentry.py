"""Utilities for sentry."""

import logging

import sentry_sdk
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from sentry_sdk.integrations.atexit import AtexitIntegration
from sentry_sdk.integrations.dedupe import DedupeIntegration
from sentry_sdk.integrations.excepthook import ExcepthookIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.threading import ThreadingIntegration

from ..const import SUPERVISOR_VERSION
from ..coresys import CoreSys
from ..misc.filter import filter_data

_LOGGER: logging.Logger = logging.getLogger(__name__)


def sentry_connected() -> bool:
    """Is sentry connected."""
    return sentry_sdk.Hub.current.client and sentry_sdk.Hub.current.client.transport


def init_sentry(coresys: CoreSys) -> None:
    """Initialize sentry client."""
    if not sentry_connected():
        _LOGGER.info("Initializing Supervisor Sentry")
        sentry_sdk.init(
            dsn="https://9c6ea70f49234442b4746e447b24747e@o427061.ingest.sentry.io/5370612",
            before_send=lambda event, hint: filter_data(coresys, event, hint),
            auto_enabling_integrations=False,
            default_integrations=False,
            integrations=[
                AioHttpIntegration(),
                ExcepthookIntegration(),
                DedupeIntegration(),
                AtexitIntegration(),
                ThreadingIntegration(),
                LoggingIntegration(level=logging.WARNING, event_level=logging.CRITICAL),
            ],
            release=SUPERVISOR_VERSION,
            max_breadcrumbs=30,
        )


def capture_exception(err: Exception) -> None:
    """Capture an exception and send to sentry."""
    if sentry_connected():
        sentry_sdk.capture_exception(err)


def close_sentry() -> None:
    """Close the current sentry client.

    This method is irreversible. A new client will have to be initialized to re-open connetion.
    """
    if sentry_connected():
        sentry_sdk.Hub.current.client.close()
