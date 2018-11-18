"""Validate Add-on configs."""

import voluptuous as vol
import pytest

from hassio.addons import validate as vd

from ..common import load_json_fixture


def test_basic_config():
    """Validate basic config and check the default values."""
    config = load_json_fixture("basic-addon-config.json")

    valid_config = vd.SCHEMA_ADDON_CONFIG(config)

    assert valid_config['name'] == "Test Add-on"
    assert valid_config['image'] == "test/{arch}-my-custom-addon"

    # Check defaults
    assert not valid_config['host_network']
    assert not valid_config['host_ipc']
    assert not valid_config['host_dbus']
    assert not valid_config['host_pid']

    assert not valid_config['hassio_api']
    assert not valid_config['homeassistant_api']
    assert not valid_config['docker_api']


def test_invalid_repository():
    """Validate basic config with invalid repository."""
    config = load_json_fixture("basic-addon-config.json")

    config['image'] = "home-assistant/no-valid-repo"
    with pytest.raises(vol.Invalid):
        vd.SCHEMA_ADDON_CONFIG(config)

    config['image'] = "homeassistant/no-valid-repo:no-tag-allow"
    with pytest.raises(vol.Invalid):
        vd.SCHEMA_ADDON_CONFIG(config)
