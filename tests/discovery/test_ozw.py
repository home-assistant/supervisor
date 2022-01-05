"""Test OpenZwave MQTT discovery."""

import pytest
import voluptuous as vol

from supervisor.discovery.validate import valid_discovery_config


def test_good_config():
    """Test good zwave mqtt config."""

    valid_discovery_config(
        "ozw",
        {"host": "test", "port": 3812, "username": "bla", "password": "test"},
    )


def test_bad_config():
    """Test bad zwave mqtt config."""

    with pytest.raises(vol.Invalid):
        valid_discovery_config("ozw", {"host": "test", "username": "bla", "ssl": True})
