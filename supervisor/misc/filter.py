"""Filter tools."""

import ipaddress
import os
import re
from typing import cast

from aiohttp import hdrs
import attr
from sentry_sdk.types import Event, Hint

from ..const import DOCKER_NETWORK_MASK, HEADER_TOKEN, HEADER_TOKEN_OLD, CoreState
from ..coresys import CoreSys
from ..exceptions import AddonConfigurationError

RE_URL: re.Pattern = re.compile(r"(\w+:\/\/)(.*\.\w+)(.*)")


def sanitize_host(host: str) -> str:
    """Return a sanitized host."""
    try:
        # Allow internal URLs
        ip = ipaddress.ip_address(host)
        if ip in ipaddress.ip_network(DOCKER_NETWORK_MASK):
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


def filter_data(coresys: CoreSys, event: Event, hint: Hint) -> Event | None:
    """Filter event data before sending to sentry."""
    # Ignore some  exceptions
    if "exc_info" in hint:
        _, exc_value, _ = hint["exc_info"]
        if isinstance(exc_value, (AddonConfigurationError)):
            return None

    # Ignore issue if system is not supported or diagnostics is disabled
    if not coresys.config.diagnostics or not coresys.core.supported or coresys.dev:
        return None

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
        return event

    # List installed addons
    installed_addons = [
        {"slug": addon.slug, "repository": addon.repository, "name": addon.name}
        for addon in coresys.addons.installed
    ]

    # Update information
    event.setdefault("contexts", {}).update(
        {
            "supervisor": {
                "channel": coresys.updater.channel,
                "installed_addons": installed_addons,
            },
            "host": {
                "arch": coresys.arch.default,
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
            "resolution": {
                "issues": [attr.asdict(issue) for issue in coresys.resolution.issues],
                "suggestions": [
                    attr.asdict(suggestion)
                    for suggestion in coresys.resolution.suggestions
                ],
                "unhealthy": coresys.resolution.unhealthy,
            },
            "store": {
                "repositories": coresys.store.repository_urls,
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
