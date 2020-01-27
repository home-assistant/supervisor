"""Test unifi discovery."""

import voluptuous as vol
import pytest

from hassio.discovery.validate import valid_discovery_config


def test_good_config():
    """Test good unifi config."""

    valid_discovery_config("unifi", {"host": "test", "port": 3812})


def test_bad_config():
    """Test good unifi config."""

    with pytest.raises(vol.Invalid):
        valid_discovery_config("unifi", {"host": "test"})
