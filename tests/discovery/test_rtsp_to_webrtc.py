"""Test rtsp_to_webrtc discovery."""

import pytest
import voluptuous as vol

from supervisor.discovery.validate import valid_discovery_config

SERVICE = "rtsp_to_webrtc"


def test_good_config():
    """Test good config."""

    valid_discovery_config(SERVICE, {"host": "test", "port": 3812})


def test_bad_config():
    """Test bad config."""

    with pytest.raises(vol.Invalid):
        valid_discovery_config(SERVICE, {"host": "test"})
