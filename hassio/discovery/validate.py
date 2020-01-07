"""Validate services schema."""
from pathlib import Path
from importlib import import_module

import voluptuous as vol

from ..const import ATTR_ADDON, ATTR_CONFIG, ATTR_DISCOVERY, ATTR_SERVICE, ATTR_UUID
from ..utils.validate import schema_or
from ..validate import uuid_match


def valid_discovery_service(service):
    """Validate service name."""
    service_file = Path(__file__).parent.joinpath(f"services/{service}.py")
    if not service_file.exists():
        raise vol.Invalid(f"Service {service} not found")
    return service


def valid_discovery_config(service, config):
    """Validate service name."""
    try:
        service_mod = import_module(f".services.{service}", "hassio.discovery")
    except ImportError:
        raise vol.Invalid(f"Service {service} not found")

    return service_mod.SCHEMA(config)


SCHEMA_DISCOVERY = vol.Schema(
    [
        vol.Schema(
            {
                vol.Required(ATTR_UUID): uuid_match,
                vol.Required(ATTR_ADDON): vol.Coerce(str),
                vol.Required(ATTR_SERVICE): valid_discovery_service,
                vol.Required(ATTR_CONFIG): vol.Maybe(dict),
            },
            extra=vol.REMOVE_EXTRA,
        )
    ]
)

SCHEMA_DISCOVERY_CONFIG = vol.Schema(
    {vol.Optional(ATTR_DISCOVERY, default=list): schema_or(SCHEMA_DISCOVERY)},
    extra=vol.REMOVE_EXTRA,
)
