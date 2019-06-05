"""Test adguard discovery."""

import voluptuous as vol
import pytest

from hassio.discovery.validate import valid_discovery_config


def test_good_config():
    """Test good deconz config."""

    valid_discovery_config("adguard", {"host": "test", "port": 3812})


def test_bad_config():
    """Test good adguard config."""

    with pytest.raises(vol.Invalid):
        valid_discovery_config("adguard", {"host": "test"})
