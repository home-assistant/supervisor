"""Test adguard discovery."""

import pytest
import voluptuous as vol

from supervisor.discovery.validate import valid_discovery_config


def test_good_config():
    """Test good adguard config."""

    valid_discovery_config("adguard", {"host": "test", "port": 3812})


def test_bad_config():
    """Test bad adguard config."""

    with pytest.raises(vol.Invalid):
        valid_discovery_config("adguard", {"host": "test"})
