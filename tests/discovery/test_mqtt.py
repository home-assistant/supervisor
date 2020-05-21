"""Test MQTT discovery."""

import pytest
import voluptuous as vol

from supervisor.discovery.validate import valid_discovery_config


def test_good_config():
    """Test good mqtt config."""

    valid_discovery_config(
        "mqtt", {"host": "test", "port": 3812, "username": "bla", "ssl": True}
    )


def test_bad_config():
    """Test good mqtt config."""

    with pytest.raises(vol.Invalid):
        valid_discovery_config("mqtt", {"host": "test", "username": "bla", "ssl": True})
