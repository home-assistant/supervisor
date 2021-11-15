"""Filter tools."""
import os
import re

from aiohttp import hdrs
import attr

from ..const import HEADER_TOKEN_OLD, SupervisorState
from ..coresys import CoreSys
from ..exceptions import AddonConfigurationError

RE_URL: re.Pattern = re.compile(r"(\w+:\/\/)(.*\.\w+)(.*)")


def sanitize_url(url: str) -> str:
    """Return a sanitized url."""
    if not re.match(RE_URL, url):
        # Not a URL, just return it back
        return url

    return re.sub(RE_URL, r"\1example.com\3", url)


def filter_data(coresys: CoreSys, event: dict, hint: dict) -> dict:
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

    # Not full startup - missing information
    if coresys.core.state in (SupervisorState.INITIALIZE, SupervisorState.SETUP):
        return event

    # List installed addons
    installed_addons = [
        {"slug": addon.slug, "repository": addon.repository, "name": addon.name}
        for addon in coresys.addons.installed
    ]

    # Update information
    event.setdefault("user", {}).update({"id": coresys.machine_id})
    event.setdefault("contexts", {}).update(
        {
            "supervisor": {
                "channel": coresys.updater.channel,
                "installed_addons": installed_addons,
                "repositories": coresys.config.addons_repositories,
            },
            "host": {
                "arch": coresys.arch.default,
                "board": coresys.os.board,
                "deployment": coresys.host.info.deployment,
                "disk_free_space": coresys.host.info.free_space,
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
        }
    )

    event["contexts"]["versions"].update(
        {plugin.slug: plugin.version for plugin in coresys.plugins.all_plugins}
    )

    event.setdefault("tags", []).extend(
        [
            ["installation_type", "os" if coresys.os.available else "supervised"],
            ["machine", coresys.machine],
        ],
    )

    # Sanitize event
    for i, tag in enumerate(event.get("tags", [])):
        key, value = tag
        if key == "url":
            event["tags"][i] = [key, sanitize_url(value)]

    if event.get("request"):
        if event["request"].get("url"):
            event["request"]["url"] = sanitize_url(event["request"]["url"])

        for i, header in enumerate(event["request"].get("headers", [])):
            key, value = header
            if key == hdrs.REFERER:
                event["request"]["headers"][i] = [key, sanitize_url(value)]

            if key == HEADER_TOKEN_OLD:
                event["request"]["headers"][i] = [key, "XXXXXXXXXXXXXXXXXXX"]

            if key in [hdrs.HOST, hdrs.X_FORWARDED_HOST]:
                event["request"]["headers"][i] = [key, "example.com"]

    return event
