"""Filter tools."""
import os
import re

from aiohttp import hdrs

from ..const import ENV_SUPERVISOR_DEV, HEADER_TOKEN_OLD, CoreStates
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
    dev_env: bool = bool(os.environ.get(ENV_SUPERVISOR_DEV, 0))

    # Ignore some  exceptions
    if "exc_info" in hint:
        _, exc_value, _ = hint["exc_info"]
        if isinstance(exc_value, (AddonConfigurationError)):
            return None

    # Ignore issue if system is not supported or diagnostics is disabled
    if not coresys.config.diagnostics or not coresys.supported or dev_env:
        return None

    # Not full startup - missing information
    if coresys.core.state in (CoreStates.INITIALIZE, CoreStates.SETUP):
        return event

    # Update information
    event.setdefault("extra", {}).update(
        {
            "supervisor": {
                "machine": coresys.machine,
                "arch": coresys.arch.default,
                "docker": coresys.docker.info.version,
                "channel": coresys.updater.channel,
                "supervisor": coresys.supervisor.version,
            },
            "host": {
                "disk_free_space": coresys.host.info.free_space,
                "deployment": coresys.host.info.deployment,
                "os": coresys.hassos.version,
                "host": coresys.host.info.operating_system,
                "kernel": coresys.host.info.kernel,
            },
            "versions": {
                "core": coresys.homeassistant.version,
                "audio": coresys.plugins.audio.version,
                "dns": coresys.plugins.dns.version,
                "multicast": coresys.plugins.multicast.version,
                "cli": coresys.plugins.cli.version,
            },
        }
    )
    event.setdefault("tags", []).extend(
        [
            ["installation_type", "os" if coresys.hassos.available else "supervised"],
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
