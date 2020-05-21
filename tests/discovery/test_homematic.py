"""Test HomeMatic discovery."""

import pytest
import voluptuous as vol

from supervisor.discovery.validate import valid_discovery_config


def test_good_config():
    """Test good homematic config."""

    valid_discovery_config(
        "homematic",
        {"ip": {"host": "test", "port": 3812}, "rf": {"host": "test", "port": 3712}},
    )


def test_bad_config():
    """Test good homematic config."""

    with pytest.raises(vol.Invalid):
        valid_discovery_config("homematic", {"test": {"bla": "test", "port": 8080}})
