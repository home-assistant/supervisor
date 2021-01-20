"""Test Zwave MQTT discovery."""

import pytest
import voluptuous as vol

from supervisor.discovery.validate import valid_discovery_config


def test_good_config():
    """Test good zwave js config."""

    valid_discovery_config(
        "zwave_js",
        {"host": "test", "port": 3812},
    )


def test_bad_config():
    """Test good zwave js config."""

    with pytest.raises(vol.Invalid):
        valid_discovery_config("zwave_js", {"host": "test"})
