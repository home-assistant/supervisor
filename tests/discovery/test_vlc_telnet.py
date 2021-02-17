"""Test VLC Telnet discovery."""

import pytest
import voluptuous as vol

from supervisor.discovery.validate import valid_discovery_config


def test_good_config():
    """Test good vlc telnet config."""

    valid_discovery_config(
        "vlc_telnet",
        {"host": "test", "port": 3812, "password": "darksideofthemoon"},
    )


def test_bad_config():
    """Test bad vlc telnet config."""

    with pytest.raises(vol.Invalid):
        valid_discovery_config("vlc_telnet", {"host": "test", "port": 8283})
