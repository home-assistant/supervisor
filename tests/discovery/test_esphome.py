"""Test ESPHome Dashboard discovery."""

import pytest
import voluptuous as vol

from supervisor.discovery.validate import valid_discovery_config


def test_good_config():
    """Test good ESPHome config."""

    valid_discovery_config("esphome", {"host": "test", "port": 6052})


def test_bad_config():
    """Test bad ESPHome config."""

    with pytest.raises(vol.Invalid):
        valid_discovery_config("esphome", {"host": "test"})

    with pytest.raises(vol.Invalid):
        valid_discovery_config("esphome", {"port": 6052})

    with pytest.raises(vol.Invalid):
        valid_discovery_config("esphome", {"port": -1})
