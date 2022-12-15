"""Test OTBR discovery."""

import pytest
import voluptuous as vol

from supervisor.discovery.validate import valid_discovery_config


def test_good_config():
    """Test good OTBR config."""

    valid_discovery_config(
        "otbr",
        {"host": "test", "rest_port": 3812},
    )


def test_bad_config():
    """Test bad OTBR config."""

    with pytest.raises(vol.Invalid):
        valid_discovery_config("otbr", {"host": "test"})
