"""Filter tools."""

from dataclasses import asdict
import ipaddress
import logging
import os
import re
from typing import cast

from aiohttp import hdrs
from sentry_sdk.types import Event, Hint

from ..const import DOCKER_IPV4_NETWORK_MASK, HEADER_TOKEN, HEADER_TOKEN_OLD, CoreState
from ..coresys import CoreSys
from ..exceptions import APITooManyRequests, AppConfigurationError
from ..utils import check_exception_chain

_LOGGER: logging.Logger = logging.getLogger(__name__)

RE_URL: re.Pattern = re.compile(r"(\w+:\/\/)(.*\.\w+)(.*)")
RE_URL_CREDENTIALS: re.Pattern = re.compile(r"(?<=://)[^/@\s]+@")


def sanitize_host(host: str) -> str:
    """Return a sanitized host."""
    try:
        # Allow internal URLs
        ip = ipaddress.ip_address(host)
        if ip in ipaddress.ip_network(DOCKER_IPV4_NETWORK_MASK):
            return host
    except ValueError:
        pass

    return "sanitized-host.invalid"


def sanitize_url(url: str) -> str:
    """Return a sanitized url."""
    match = re.match(RE_URL, url)
    if not match:
        # Not a URL, just return it back
        return url

    host = sanitize_host(match.group(2))

    return f"{match.group(1)}{host}{match.group(3)}"


def sanitize_url_credentials(text: str) -> str:
    """Return text with userinfo credentials removed from any URLs."""
    return RE_URL_CREDENTIALS.sub("", text)


def filter_data(coresys: CoreSys, event: Event, hint: Hint) -> Event | None:
    """Filter event data before sending to sentry."""
    # Ignore some exceptions. check_exception_chain walks __cause__ so
    # wrapped rate limits (e.g. DockerHubRateLimitExceeded wrapped in
    # SupervisorUpdateError via `raise X from err`) are also dropped.
    if "exc_info" in hint:
        _, exc_value, _ = hint["exc_info"]
        if exc_value is not None and check_exception_chain(
            exc_value, (AppConfigurationError, APITooManyRequests)
        ):
            _LOGGER.debug("Skipping Sentry event for %s", type(exc_value).__name__)
            return None

    # Ignore issue if system is not supported or diagnostics is disabled
    if not coresys.config.diagnostics or not coresys.core.supported or coresys.dev:
        return None

    # Repository URLs can contain user-supplied credentials for private
    # repositories. Remove credentials from event strings which can contain
    # such URLs: exception messages (including git stderr in GitPython
    # exceptions), log messages and breadcrumbs.
    for exc_entry in cast(dict, event.get("exception", {})).get("values", []):
        if exc_entry.get("value"):
            exc_entry["value"] = sanitize_url_credentials(exc_entry["value"])

    if logentry := cast(dict, event.get("logentry", {})):
        if logentry.get("message"):
            logentry["message"] = sanitize_url_credentials(logentry["message"])
        if params := logentry.get("params"):
            logentry["params"] = [
                sanitize_url_credentials(param) if isinstance(param, str) else param
                for param in params
            ]

    for crumb in cast(dict, event.get("breadcrumbs", {})).get("values", []):
        if crumb.get("message"):
            crumb["message"] = sanitize_url_credentials(crumb["message"])

    event.setdefault("extra", {}).update({"os.environ": dict(os.environ)})
    event.setdefault("user", {}).update({"id": coresys.machine_id})
    if coresys.machine:
        event.setdefault("tags", {}).update(
            {
                "machine": coresys.machine,
            }
        )

    # Not full startup - missing information
    if coresys.core.state in (CoreState.INITIALIZE, CoreState.SETUP):
        # During SETUP, we have basic system info available for better debugging
        if coresys.core.state == CoreState.SETUP:
            event.setdefault("contexts", {}).update(
                {
                    "versions": {
                        "docker": coresys.docker.info.version,
                        "supervisor": coresys.supervisor.version,
                    },
                    "docker": {
                        "storage_driver": coresys.docker.info.storage,
                    },
                    "host": {
                        "machine": coresys.machine,
                    },
                }
            )
        return event

    # List installed apps
    installed_apps = [
        {"slug": app.slug, "repository": app.repository, "name": app.name}
        for app in coresys.apps.installed
    ]

    # Update information
    event.setdefault("contexts", {}).update(
        {
            "supervisor": {
                "channel": coresys.updater.channel,
                "installed_addons": installed_apps,
            },
            "host": {
                "arch": str(coresys.arch.default),
                "board": coresys.os.board,
                "deployment": coresys.host.info.deployment,
                "disk_free_space": coresys.hardware.disk.get_disk_free_space(
                    coresys.config.path_supervisor
                ),
                "host": coresys.host.info.operating_system,
                "kernel": coresys.host.info.kernel,
                "machine": coresys.machine,
                "images": list(coresys.resolution.evaluate.cached_images),
            },
            "versions": {
                "core": coresys.homeassistant.version,
                "os": coresys.os.version,
                "agent": coresys.dbus.agent.version,
                "docker": coresys.docker.info.version,
                "supervisor": coresys.supervisor.version,
            },
            "docker": {
                "storage_driver": coresys.docker.info.storage,
            },
            "resolution": {
                "issues": [asdict(issue) for issue in coresys.resolution.issues],
                "suggestions": [
                    asdict(suggestion) for suggestion in coresys.resolution.suggestions
                ],
                "unhealthy": sorted(coresys.resolution.unhealthy),
            },
            "store": {
                "repositories": [
                    sanitize_url_credentials(url)
                    for url in coresys.store.repository_urls
                ],
            },
            "misc": {
                "fallback_dns": coresys.plugins.dns.fallback,
            },
        }
    )

    event["contexts"]["versions"].update(
        {plugin.slug: plugin.version for plugin in coresys.plugins.all_plugins}
    )

    event["tags"].update(
        {
            "installation_type": "os" if coresys.os.available else "supervised",
        }
    )

    if request := event.get("request"):
        if request.get("url"):
            request["url"] = sanitize_url(cast(str, request["url"]))

        if headers := cast(dict, request.get("headers")):
            if hdrs.REFERER in headers:
                headers[hdrs.REFERER] = sanitize_url(headers[hdrs.REFERER])
            if HEADER_TOKEN in headers:
                headers[HEADER_TOKEN] = "XXXXXXXXXXXXXXXXXXX"
            if HEADER_TOKEN_OLD in headers:
                headers[HEADER_TOKEN_OLD] = "XXXXXXXXXXXXXXXXXXX"
            if hdrs.HOST in headers:
                headers[hdrs.HOST] = sanitize_host(headers[hdrs.HOST])
            if hdrs.X_FORWARDED_HOST in headers:
                headers[hdrs.X_FORWARDED_HOST] = sanitize_host(
                    headers[hdrs.X_FORWARDED_HOST]
                )

    return event
