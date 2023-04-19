"""Test wyoming discovery."""

import pytest
import voluptuous as vol

from supervisor.discovery.validate import valid_discovery_config


def test_good_config():
    """Test good wyoming config."""

    valid_discovery_config("wyoming", {"host": "test", "port": 3812})


def test_bad_config():
    """Test bad wyoming config."""

    with pytest.raises(vol.Invalid):
        valid_discovery_config("wyoming", {"host": "test"})
