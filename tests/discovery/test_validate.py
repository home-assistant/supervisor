"""Test validate of discovery."""

import voluptuous as vol
import pytest

from supervisor.discovery import validate


def test_valid_services():
    """Validate that service is valid."""

    for service in ("mqtt", "deconz"):
        validate.valid_discovery_service(service)


def test_invalid_services():
    """Test that validate is invalid for a service."""

    for service in ("fadsfasd", "203432"):
        with pytest.raises(vol.Invalid):
            validate.valid_discovery_service(service)
