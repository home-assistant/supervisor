"""Validate Add-on configs."""

import pytest
import voluptuous as vol

from supervisor.addons import validate as vd

from ..common import load_json_fixture


def test_basic_config():
    """Validate basic config and check the default values."""
    config = load_json_fixture("basic-addon-config.json")

    valid_config = vd.SCHEMA_ADDON_CONFIG(config)

    assert valid_config["name"] == "Test Add-on"
    assert valid_config["image"] == "test/{arch}-my-custom-addon"

    # Check defaults
    assert not valid_config["host_network"]
    assert not valid_config["host_ipc"]
    assert not valid_config["host_dbus"]
    assert not valid_config["host_pid"]

    assert not valid_config["hassio_api"]
    assert not valid_config["homeassistant_api"]
    assert not valid_config["docker_api"]


def test_invalid_repository():
    """Validate basic config with invalid repositories."""
    config = load_json_fixture("basic-addon-config.json")

    config["image"] = "something"
    with pytest.raises(vol.Invalid):
        vd.SCHEMA_ADDON_CONFIG(config)

    config["image"] = "homeassistant/no-valid-repo:no-tag-allow"
    with pytest.raises(vol.Invalid):
        vd.SCHEMA_ADDON_CONFIG(config)

    config[
        "image"
    ] = "registry.gitlab.com/company/add-ons/test-example/text-example:no-tag-allow"
    with pytest.raises(vol.Invalid):
        vd.SCHEMA_ADDON_CONFIG(config)


def test_valid_repository():
    """Validate basic config with different valid repositories."""
    config = load_json_fixture("basic-addon-config.json")

    custom_registry = "registry.gitlab.com/company/add-ons/core/test-example"
    config["image"] = custom_registry
    valid_config = vd.SCHEMA_ADDON_CONFIG(config)
    assert valid_config["image"] == custom_registry


def test_valid_map():
    """Validate basic config with different valid maps."""
    config = load_json_fixture("basic-addon-config.json")

    config["map"] = ["backup:rw", "ssl:ro", "config"]
    vd.SCHEMA_ADDON_CONFIG(config)


def test_valid_basic_build():
    """Validate basic build config."""
    config = load_json_fixture("basic-build-config.json")

    vd.SCHEMA_BUILD_CONFIG(config)


def test_valid_machine():
    """Validate valid machine config."""
    config = load_json_fixture("basic-addon-config.json")

    config["machine"] = [
        "intel-nuc",
        "odroid-c2",
        "odroid-n2",
        "odroid-xu",
        "qemuarm-64",
        "qemuarm",
        "qemux86-64",
        "qemux86",
        "raspberrypi",
        "raspberrypi2",
        "raspberrypi3-64",
        "raspberrypi3",
        "raspberrypi4-64",
        "raspberrypi4",
        "tinker",
    ]

    assert vd.SCHEMA_ADDON_CONFIG(config)

    config["machine"] = [
        "!intel-nuc",
        "!odroid-c2",
        "!odroid-n2",
        "!odroid-xu",
        "!qemuarm-64",
        "!qemuarm",
        "!qemux86-64",
        "!qemux86",
        "!raspberrypi",
        "!raspberrypi2",
        "!raspberrypi3-64",
        "!raspberrypi3",
        "!raspberrypi4-64",
        "!raspberrypi4",
        "!tinker",
    ]

    assert vd.SCHEMA_ADDON_CONFIG(config)

    config["machine"] = [
        "odroid-n2",
        "!odroid-xu",
        "qemuarm-64",
        "!qemuarm",
        "qemux86-64",
        "qemux86",
        "raspberrypi",
        "raspberrypi4-64",
        "raspberrypi4",
        "!tinker",
    ]

    assert vd.SCHEMA_ADDON_CONFIG(config)


def test_invalid_machine():
    """Validate invalid machine config."""
    config = load_json_fixture("basic-addon-config.json")

    config["machine"] = [
        "intel-nuc",
        "raspberrypi3",
        "raspberrypi4-64",
        "raspberrypi4",
        "tinkerxy",
    ]

    with pytest.raises(vol.Invalid):
        assert vd.SCHEMA_ADDON_CONFIG(config)

    config["machine"] = [
        "intel-nuc",
        "intel-nuc",
    ]

    with pytest.raises(vol.Invalid):
        assert vd.SCHEMA_ADDON_CONFIG(config)


def test_watchdog_url():
    """Test Valid watchdog options."""
    config = load_json_fixture("basic-addon-config.json")

    for test_options in (
        "tcp://[HOST]:[PORT:8123]",
        "http://[HOST]:[PORT:8080]/health",
        "https://[HOST]:[PORT:80]/",
    ):
        config["watchdog"] = test_options
        assert vd.SCHEMA_ADDON_CONFIG(config)
