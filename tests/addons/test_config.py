"""Validate Add-on configs."""

import pytest
import voluptuous as vol

from supervisor.addons import validate as vd
from supervisor.addons.const import AddonBackupMode

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
    assert not valid_config["host_uts"]

    assert not valid_config["hassio_api"]
    assert not valid_config["homeassistant_api"]
    assert not valid_config["docker_api"]


def test_migration_startup():
    """Migrate Startup Type."""
    config = load_json_fixture("basic-addon-config.json")

    config["startup"] = "before"

    valid_config = vd.SCHEMA_ADDON_CONFIG(config)

    assert valid_config["startup"] == "services"

    config["startup"] = "after"

    valid_config = vd.SCHEMA_ADDON_CONFIG(config)

    assert valid_config["startup"] == "application"


def test_migration_auto_uart():
    """Migrate auto uart Type."""
    config = load_json_fixture("basic-addon-config.json")

    config["auto_uart"] = True

    valid_config = vd.SCHEMA_ADDON_CONFIG(config)

    assert valid_config["uart"]
    assert "auto_uart" not in valid_config


def test_migration_devices():
    """Migrate devices Type."""
    config = load_json_fixture("basic-addon-config.json")

    config["devices"] = ["test:test:rw", "bla"]

    valid_config = vd.SCHEMA_ADDON_CONFIG(config)

    assert valid_config["devices"] == ["test", "bla"]


def test_migration_tmpfs():
    """Migrate tmpfs Type."""
    config = load_json_fixture("basic-addon-config.json")

    config["tmpfs"] = "test:test:rw"

    valid_config = vd.SCHEMA_ADDON_CONFIG(config)

    assert valid_config["tmpfs"]


def test_migration_backup():
    """Migrate snapshot to backup."""
    config = load_json_fixture("basic-addon-config.json")

    config["snapshot"] = AddonBackupMode.HOT
    config["snapshot_pre"] = "pre_command"
    config["snapshot_post"] = "post_command"
    config["snapshot_exclude"] = ["excludeed"]

    valid_config = vd.SCHEMA_ADDON_CONFIG(config)

    assert valid_config.get("snapshot") is None
    assert valid_config.get("snapshot_pre") is None
    assert valid_config.get("snapshot_post") is None
    assert valid_config.get("snapshot_exclude") is None

    assert valid_config["backup"] == AddonBackupMode.HOT
    assert valid_config["backup_pre"] == "pre_command"
    assert valid_config["backup_post"] == "post_command"
    assert valid_config["backup_exclude"] == ["excludeed"]


def test_invalid_repository():
    """Validate basic config with invalid repositories."""
    config = load_json_fixture("basic-addon-config.json")

    config["image"] = "-invalid-something"
    with pytest.raises(vol.Invalid):
        vd.SCHEMA_ADDON_CONFIG(config)

    config["image"] = "ghcr.io/home-assistant/no-valid-repo:no-tag-allow"
    with pytest.raises(vol.Invalid):
        vd.SCHEMA_ADDON_CONFIG(config)

    config["image"] = (
        "registry.gitlab.com/company/add-ons/test-example/text-example:no-tag-allow"
    )
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


def test_malformed_map_entries():
    """Test that malformed map entries are handled gracefully (issue #6124)."""
    config = load_json_fixture("basic-addon-config.json")

    # Test case 1: Empty dict in map (should be skipped with warning)
    config["map"] = [{}]
    valid_config = vd.SCHEMA_ADDON_CONFIG(config)
    assert valid_config["map"] == []

    # Test case 2: Dict missing required 'type' field (should be skipped with warning)
    config["map"] = [{"read_only": False, "path": "/custom"}]
    valid_config = vd.SCHEMA_ADDON_CONFIG(config)
    assert valid_config["map"] == []

    # Test case 3: Invalid string format that doesn't match regex
    config["map"] = ["invalid_format", "not:a:valid:mapping", "share:invalid_mode"]
    valid_config = vd.SCHEMA_ADDON_CONFIG(config)
    assert valid_config["map"] == []

    # Test case 4: Mix of valid and invalid entries (invalid should be filtered out)
    config["map"] = [
        "share:rw",  # Valid string format
        "invalid_string",  # Invalid string format
        {},  # Invalid empty dict
        {"type": "config", "read_only": True},  # Valid dict format
        {"read_only": False},  # Invalid - missing type
    ]
    valid_config = vd.SCHEMA_ADDON_CONFIG(config)
    # Should only keep the valid entries
    assert len(valid_config["map"]) == 2
    assert any(entry["type"] == "share" for entry in valid_config["map"])
    assert any(entry["type"] == "config" for entry in valid_config["map"])

    # Test case 5: The specific case from the UplandJacob repo (malformed YAML format)
    # This simulates what YAML "- addon_config: rw" creates
    config["map"] = [{"addon_config": "rw"}]  # Wrong structure, missing 'type' key
    valid_config = vd.SCHEMA_ADDON_CONFIG(config)
    assert valid_config["map"] == []


def test_valid_basic_build():
    """Validate basic build config."""
    config = load_json_fixture("basic-build-config.json")

    vd.SCHEMA_BUILD_CONFIG(config)


async def test_valid_manifest_build():
    """Validate build config with manifest build from."""
    config = load_json_fixture("build-config-manifest.json")

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
        "raspberrypi5-64",
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
        "!raspberrypi5-64",
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
        "raspberrypi5-64",
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


def test_valid_slug():
    """Test valid and invalid addon slugs."""
    config = load_json_fixture("basic-addon-config.json")

    # All examples pulled from https://analytics.home-assistant.io/addons.json
    config["slug"] = "uptime-kuma"
    assert vd.SCHEMA_ADDON_CONFIG(config)

    config["slug"] = "hassio_google_drive_backup"
    assert vd.SCHEMA_ADDON_CONFIG(config)

    config["slug"] = "paradox_alarm_interface_3.x"
    assert vd.SCHEMA_ADDON_CONFIG(config)

    config["slug"] = "Lupusec2Mqtt"
    assert vd.SCHEMA_ADDON_CONFIG(config)

    # No whitespace
    config["slug"] = "my addon"
    with pytest.raises(vol.Invalid):
        assert vd.SCHEMA_ADDON_CONFIG(config)

    # No url control chars (or other non-word ascii characters)
    config["slug"] = "a/b_&_c\\d_@ddon$:_test=#2?"
    with pytest.raises(vol.Invalid):
        assert vd.SCHEMA_ADDON_CONFIG(config)

    # No unicode
    config["slug"] = "complemento telefónico"
    with pytest.raises(vol.Invalid):
        assert vd.SCHEMA_ADDON_CONFIG(config)


def test_valid_schema():
    """Test valid and invalid addon slugs."""
    config = load_json_fixture("basic-addon-config.json")

    # Basic types
    config["schema"] = {
        "bool_basic": "bool",
        "mail_basic": "email",
        "url_basic": "url",
        "port_basic": "port",
        "match_basic": "match(.*@.*)",
        "list_basic": "list(option1|option2|option3)",
        # device
        "device_basic": "device",
        "device_filter": "device(subsystem=tty)",
        # str
        "str_basic": "str",
        "str_basic2": "str(,)",
        "str_min": "str(5,)",
        "str_max": "str(,10)",
        "str_minmax": "str(5,10)",
        # password
        "password_basic": "password",
        "password_basic2": "password(,)",
        "password_min": "password(5,)",
        "password_max": "password(,10)",
        "password_minmax": "password(5,10)",
        # int
        "int_basic": "int",
        "int_basic2": "int(,)",
        "int_min": "int(5,)",
        "int_max": "int(,10)",
        "int_minmax": "int(5,10)",
        # float
        "float_basic": "float",
        "float_basic2": "float(,)",
        "float_min": "float(5,)",
        "float_max": "float(,10)",
        "float_minmax": "float(5,10)",
    }
    assert vd.SCHEMA_ADDON_CONFIG(config)

    # Different valid ways of nesting dicts and lists
    config["schema"] = {
        "str_list": ["str"],
        "dict_in_list": [
            {
                "required": "str",
                "optional": "str?",
            }
        ],
        "dict": {
            "required": "str",
            "optional": "str?",
            "str_list_in_dict": ["str"],
            "dict_in_list_in_dict": [
                {
                    "required": "str",
                    "optional": "str?",
                    "str_list_in_dict_in_list_in_dict": ["str"],
                }
            ],
            "dict_in_dict": {
                "str_list_in_dict_in_dict": ["str"],
                "dict_in_list_in_dict_in_dict": [
                    {
                        "required": "str",
                        "optional": "str?",
                    }
                ],
                "dict_in_dict_in_dict": {
                    "required": "str",
                    "optional": "str",
                },
            },
        },
    }
    assert vd.SCHEMA_ADDON_CONFIG(config)

    # List nested within dict within list
    config["schema"] = {"field": [{"subfield": ["str"]}]}
    assert vd.SCHEMA_ADDON_CONFIG(config)

    # No lists directly nested within each other
    config["schema"] = {"field": [["str"]]}
    with pytest.raises(vol.Invalid):
        assert vd.SCHEMA_ADDON_CONFIG(config)

    # Field types must be valid
    config["schema"] = {"field": "invalid"}
    with pytest.raises(vol.Invalid):
        assert vd.SCHEMA_ADDON_CONFIG(config)
