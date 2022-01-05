"""Test motionEye discovery."""

import pytest
import voluptuous as vol

from supervisor.discovery.validate import valid_discovery_config


def test_good_config() -> None:
    """Test good motionEye config."""
    valid_discovery_config("motioneye", {"url": "http://example.com:1234"})


def test_bad_config() -> None:
    """Test bad motionEye config."""
    with pytest.raises(vol.Invalid):
        valid_discovery_config("motioneye", {})
