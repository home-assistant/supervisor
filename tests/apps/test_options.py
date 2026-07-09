"""Test apps schema to UI schema conversion."""

from pathlib import Path
import re

import pytest
import voluptuous as vol

from supervisor.apps.options import AppOptions, UiOptions, _extract_match_options
from supervisor.hardware.data import Device

MOCK_ADDON_NAME = "Mock Add-on"
MOCK_ADDON_SLUG = "mock_addon"


def test_simple_schema(coresys):
    """Test with simple schema."""
    assert AppOptions(
        coresys,
        {"name": "str", "password": "password", "fires": "bool", "alias": "str?"},
        MOCK_ADDON_NAME,
        MOCK_ADDON_SLUG,
    )({"name": "Pascal", "password": "1234", "fires": True, "alias": "test"})

    assert AppOptions(
        coresys,
        {"name": "str", "password": "password", "fires": "bool", "alias": "str?"},
        MOCK_ADDON_NAME,
        MOCK_ADDON_SLUG,
    )({"name": "Pascal", "password": "1234", "fires": True})

    with pytest.raises(vol.error.Invalid):
        AppOptions(
            coresys,
            {"name": "str", "password": "password", "fires": "bool", "alias": "str?"},
            MOCK_ADDON_NAME,
            MOCK_ADDON_SLUG,
        )({"name": "Pascal", "password": "1234", "fires": "hah"})

    with pytest.raises(vol.error.Invalid):
        AppOptions(
            coresys,
            {"name": "str", "password": "password", "fires": "bool", "alias": "str?"},
            MOCK_ADDON_NAME,
            MOCK_ADDON_SLUG,
        )({"name": "Pascal", "fires": True})


def test_simple_schema_integers(coresys):
    """Test integer limits."""
    assert AppOptions(
        coresys,
        {"name": "str", "password": "password", "pos": "int(0,10)", "neg": "int(-5,0)"},
        MOCK_ADDON_NAME,
        MOCK_ADDON_SLUG,
    )({"name": "Pascal", "password": "1234", "pos": 5, "neg": "-4"})

    with pytest.raises(vol.error.Invalid):
        assert AppOptions(
            coresys,
            {
                "name": "str",
                "password": "password",
                "pos": "int(0,10)",
                "neg": "int(-5,0)",
            },
            MOCK_ADDON_NAME,
            MOCK_ADDON_SLUG,
        )({"name": "Pascal", "password": "1234", "pos": 11, "neg": "-6"})


def test_simple_schema_floats(coresys):
    """Test float limits."""
    assert AppOptions(
        coresys,
        {
            "name": "str",
            "password": "password",
            "pos": "float(0.0,10.5)",
            "neg": "float(-5.0,-.5)",
        },
        MOCK_ADDON_NAME,
        MOCK_ADDON_SLUG,
    )({"name": "Pascal", "password": "1234", "pos": 5.0, "neg": "-4.0"})

    with pytest.raises(vol.error.Invalid):
        assert AppOptions(
            coresys,
            {
                "name": "str",
                "password": "password",
                "pos": "float(0.0,10.5)",
                "neg": "float(-5.0,-.5)",
            },
            MOCK_ADDON_NAME,
            MOCK_ADDON_SLUG,
        )({"name": "Pascal", "password": "1234", "pos": 11.0, "neg": "-6.0"})

    with pytest.raises(vol.error.Invalid):
        assert AppOptions(
            coresys,
            {"name": "str", "password": "password", "float": "float(-1.0,-.)"},
            MOCK_ADDON_NAME,
            MOCK_ADDON_SLUG,
        )({"name": "Pascal", "password": "1234", "float": "0.0"})


def test_complex_schema_list(coresys):
    """Test with complex list schema."""
    assert AppOptions(
        coresys,
        {"name": "str", "password": "password", "extend": ["str"]},
        MOCK_ADDON_NAME,
        MOCK_ADDON_SLUG,
    )({"name": "Pascal", "password": "1234", "extend": ["test", "blu"]})

    with pytest.raises(vol.error.Invalid):
        AppOptions(
            coresys,
            {"name": "str", "password": "password", "extend": ["str"]},
            MOCK_ADDON_NAME,
            MOCK_ADDON_SLUG,
        )({"name": "Pascal", "password": "1234", "extend": ["test", 1]})

    with pytest.raises(vol.error.Invalid):
        AppOptions(
            coresys,
            {"name": "str", "password": "password", "extend": ["str"]},
            MOCK_ADDON_NAME,
            MOCK_ADDON_SLUG,
        )({"name": "Pascal", "password": "1234", "extend": "test"})


def test_optional_schema_list(coresys):
    """Test with an optional list schema."""
    assert AppOptions(
        coresys,
        {"name": "str", "password": "password", "extend": ["str?"]},
        MOCK_ADDON_NAME,
        MOCK_ADDON_SLUG,
    )({"name": "Pascal", "password": "1234"})

    assert AppOptions(
        coresys,
        {"name": "str", "password": "password", "extend": ["str?"]},
        MOCK_ADDON_NAME,
        MOCK_ADDON_SLUG,
    )({"name": "Pascal", "password": "1234", "extend": []})

    with pytest.raises(vol.error.Invalid):
        AppOptions(
            coresys,
            {"name": "str", "password": "password", "extend": ["str"]},
            MOCK_ADDON_NAME,
            MOCK_ADDON_SLUG,
        )({"name": "Pascal", "password": "1234"})

    assert AppOptions(
        coresys,
        {"name": "str", "password": "password", "extend": ["str"]},
        MOCK_ADDON_NAME,
        MOCK_ADDON_SLUG,
    )({"name": "Pascal", "password": "1234", "extend": []})


def test_complex_schema_dict(coresys):
    """Test with complex dict schema."""
    assert AppOptions(
        coresys,
        {"name": "str", "password": "password", "extend": {"test": "int"}},
        MOCK_ADDON_NAME,
        MOCK_ADDON_SLUG,
    )({"name": "Pascal", "password": "1234", "extend": {"test": 1}})

    with pytest.raises(vol.error.Invalid):
        AppOptions(
            coresys,
            {"name": "str", "password": "password", "extend": {"test": "int"}},
            MOCK_ADDON_NAME,
            MOCK_ADDON_SLUG,
        )({"name": "Pascal", "password": "1234", "extend": {"wrong": 1}})

    with pytest.raises(vol.error.Invalid):
        AppOptions(
            coresys,
            {"name": "str", "password": "password", "extend": ["str"]},
            MOCK_ADDON_NAME,
            MOCK_ADDON_SLUG,
        )({"name": "Pascal", "password": "1234", "extend": "test"})


def test_complex_schema_dict_and_list(coresys):
    """Test with complex dict/list nested schema."""
    assert AppOptions(
        coresys,
        {
            "name": "str",
            "packages": [
                {
                    "name": "str",
                    "options": {"optional": "bool"},
                    "dependencies": [{"name": "str"}],
                }
            ],
        },
        MOCK_ADDON_NAME,
        MOCK_ADDON_SLUG,
    )(
        {
            "name": "Pascal",
            "packages": [
                {
                    "name": "core",
                    "options": {"optional": False},
                    "dependencies": [{"name": "supervisor"}, {"name": "audio"}],
                }
            ],
        }
    )

    with pytest.raises(vol.error.Invalid):
        assert AppOptions(
            coresys,
            {
                "name": "str",
                "packages": [
                    {
                        "name": "str",
                        "options": {"optional": "bool"},
                        "dependencies": [{"name": "str"}],
                    }
                ],
            },
            MOCK_ADDON_NAME,
            MOCK_ADDON_SLUG,
        )(
            {
                "name": "Pascal",
                "packages": [
                    {
                        "name": "core",
                        "options": {"optional": False},
                        "dependencies": [{"name": "supervisor"}, "wrong"],
                    }
                ],
            }
        )


def test_simple_device_schema(coresys):
    """Test with simple schema."""
    for device in (
        Device(
            "ttyACM0",
            Path("/dev/ttyACM0"),
            Path("/sys/bus/usb/002"),
            "tty",
            None,
            [],
            {"ID_VENDOR": "xy"},
            [],
        ),
        Device(
            "ttyUSB0",
            Path("/dev/ttyUSB0"),
            Path("/sys/bus/usb/001"),
            "tty",
            None,
            [Path("/dev/ttyS1"), Path("/dev/serial/by-id/xyx")],
            {"ID_VENDOR": "xy"},
            [],
        ),
        Device(
            "ttyS0",
            Path("/dev/ttyS0"),
            Path("/sys/bus/usb/003"),
            "tty",
            None,
            [],
            {},
            [],
        ),
        Device(
            "video1",
            Path("/dev/video1"),
            Path("/sys/bus/usb/004"),
            "misc",
            None,
            [],
            {"ID_VENDOR": "xy"},
            [],
        ),
    ):
        coresys.hardware.update_device(device)

    data_device_path = AppOptions(
        coresys,
        {"name": "str", "password": "password", "input": "device"},
        MOCK_ADDON_NAME,
        MOCK_ADDON_SLUG,
    )({"name": "Pascal", "password": "1234", "input": "/dev/ttyUSB0"})
    assert data_device_path["input"] == "/dev/ttyUSB0"

    data = AppOptions(
        coresys,
        {"name": "str", "password": "password", "input": "device"},
        MOCK_ADDON_NAME,
        MOCK_ADDON_SLUG,
    )({"name": "Pascal", "password": "1234", "input": "/dev/serial/by-id/xyx"})
    assert data["input"] == "/dev/serial/by-id/xyx"

    assert AppOptions(
        coresys,
        {"name": "str", "password": "password", "input": "device(subsystem=tty)"},
        MOCK_ADDON_NAME,
        MOCK_ADDON_SLUG,
    )({"name": "Pascal", "password": "1234", "input": "/dev/ttyACM0"})

    with pytest.raises(vol.error.Invalid):
        assert AppOptions(
            coresys,
            {"name": "str", "password": "password", "input": "device"},
            MOCK_ADDON_NAME,
            MOCK_ADDON_SLUG,
        )({"name": "Pascal", "password": "1234", "input": "/dev/not_exists"})

    with pytest.raises(vol.error.Invalid):
        assert AppOptions(
            coresys,
            {"name": "str", "password": "password", "input": "device(subsystem=tty)"},
            MOCK_ADDON_NAME,
            MOCK_ADDON_SLUG,
        )({"name": "Pascal", "password": "1234", "input": "/dev/video1"})


def test_device_schema_wrong_type(coresys):
    """Test device option rejects non-string values."""
    with pytest.raises(vol.error.Invalid):
        AppOptions(
            coresys,
            {"name": "str", "input": "device(subsystem=tty)"},
            MOCK_ADDON_NAME,
            MOCK_ADDON_SLUG,
        )({"name": "Pascal", "input": {"baudrate": 115200, "flow_control": True}})

    with pytest.raises(vol.error.Invalid):
        AppOptions(
            coresys,
            {"name": "str", "input": "device"},
            MOCK_ADDON_NAME,
            MOCK_ADDON_SLUG,
        )({"name": "Pascal", "input": 12345})


def test_extract_device_paths(coresys):
    """Test extract_device_paths collects configured device paths.

    It must walk every schema shape (flat, optional, filtered, list, nested
    dict and list of dicts) and return the raw configured paths without
    resolving them against live hardware, while skipping non-device options,
    unset keys and empty values.
    """
    options = AppOptions(
        coresys,
        {
            "single": "device",
            "optional": "device?",
            "filtered": "device(subsystem=tty)",
            "many": ["device"],
            "group": {"inner": "device", "name": "str"},
            "repeated": [{"dev": "device", "label": "str"}],
            "plain": "str",
            "empty": "device?",
            "missing": "device",
        },
        MOCK_ADDON_NAME,
        MOCK_ADDON_SLUG,
    )

    assert options.extract_device_paths(
        {
            "single": "/dev/ttyUSB0",
            "optional": "/dev/serial/by-id/usb-aaa",
            "filtered": "/dev/ttyACM0",
            "many": ["/dev/bus/usb/001/002", "/dev/bus/usb/001/003"],
            "group": {"inner": "/dev/gpiochip0", "name": "x"},
            "repeated": [
                {"dev": "/dev/video0", "label": "cam0"},
                {"dev": "/dev/video1", "label": "cam1"},
            ],
            "plain": "not a device",
            "empty": "",
            # "missing" is intentionally absent from the options
        }
    ) == {
        Path("/dev/ttyUSB0"),
        Path("/dev/serial/by-id/usb-aaa"),
        Path("/dev/ttyACM0"),
        Path("/dev/bus/usb/001/002"),
        Path("/dev/bus/usb/001/003"),
        Path("/dev/gpiochip0"),
        Path("/dev/video0"),
        Path("/dev/video1"),
    }

    # No device options configured returns an empty set
    assert (
        AppOptions(
            coresys,
            {"name": "str", "port": "port"},
            MOCK_ADDON_NAME,
            MOCK_ADDON_SLUG,
        ).extract_device_paths({"name": "Pascal", "port": 8080})
        == set()
    )


def test_simple_schema_password(coresys):
    """Test with simple schema password pwned."""
    validate = AppOptions(
        coresys,
        {"name": "str", "password": "password", "fires": "bool", "alias": "str?"},
        MOCK_ADDON_NAME,
        MOCK_ADDON_SLUG,
    )

    assert validate(
        {"name": "Pascal", "password": "1234", "fires": True, "alias": "test"}
    )

    assert validate.pwned == {"7110eda4d09e062aa5e4a390b0a572ac0d2c0220"}

    validate.pwned.clear()
    assert validate({"name": "Pascal", "password": "", "fires": True, "alias": "test"})

    assert not validate.pwned


def test_ui_simple_schema(coresys):
    """Test with simple schema."""
    assert UiOptions(coresys)(
        {"name": "str", "password": "password", "fires": "bool", "alias": "str?"},
    ) == [
        {"name": "name", "required": True, "type": "string"},
        {"format": "password", "name": "password", "required": True, "type": "string"},
        {"name": "fires", "required": True, "type": "boolean"},
        {"name": "alias", "optional": True, "type": "string"},
    ]


def test_ui_group_schema(coresys):
    """Test with group schema."""
    assert UiOptions(coresys)(
        {
            "name": "str",
            "password": "password",
            "fires": "bool",
            "alias": "str?",
            "extended": {"name": "str", "data": ["str"], "path": "str?"},
        },
    ) == [
        {"name": "name", "required": True, "type": "string"},
        {"format": "password", "name": "password", "required": True, "type": "string"},
        {"name": "fires", "required": True, "type": "boolean"},
        {"name": "alias", "optional": True, "type": "string"},
        {
            "multiple": False,
            "name": "extended",
            "optional": True,
            "schema": [
                {"name": "name", "required": True, "type": "string"},
                {"multiple": True, "name": "data", "required": True, "type": "string"},
                {"name": "path", "optional": True, "type": "string"},
            ],
            "type": "schema",
        },
    ]


def test_ui_group_list_schema(coresys):
    """Test with group schema."""
    assert UiOptions(coresys)(
        {
            "name": "str",
            "password": "password",
            "fires": "bool",
            "alias": "str?",
            "extended": [{"name": "str", "data": ["str?"], "path": "str?"}],
        },
    ) == [
        {"name": "name", "required": True, "type": "string"},
        {"format": "password", "name": "password", "required": True, "type": "string"},
        {"name": "fires", "required": True, "type": "boolean"},
        {"name": "alias", "optional": True, "type": "string"},
        {
            "multiple": True,
            "name": "extended",
            "optional": True,
            "schema": [
                {"name": "name", "required": True, "type": "string"},
                {"multiple": True, "name": "data", "optional": True, "type": "string"},
                {"name": "path", "optional": True, "type": "string"},
            ],
            "type": "schema",
        },
    ]


def test_ui_simple_device_schema(coresys):
    """Test with simple schema."""
    for device in (
        Device(
            "ttyACM0",
            Path("/dev/ttyACM0"),
            Path("/sys/bus/usb/002"),
            "tty",
            None,
            [],
            {"ID_VENDOR": "xy"},
            [],
        ),
        Device(
            "ttyUSB0",
            Path("/dev/ttyUSB0"),
            Path("/sys/bus/usb/001"),
            "tty",
            None,
            [Path("/dev/ttyS1"), Path("/dev/serial/by-id/xyx")],
            {"ID_VENDOR": "xy"},
            [],
        ),
        Device(
            "ttyS0",
            Path("/dev/ttyS0"),
            Path("/sys/bus/usb/003"),
            "tty",
            None,
            [],
            {},
            [],
        ),
        Device(
            "video1",
            Path("/dev/video1"),
            Path("/sys/bus/usb/004"),
            "misc",
            None,
            [],
            {"ID_VENDOR": "xy"},
            [],
        ),
    ):
        coresys.hardware.update_device(device)

    data = UiOptions(coresys)(
        {
            "name": "str",
            "password": "password",
            "fires": "bool",
            "alias": "str?",
            "input": "device(subsystem=tty)",
        },
    )

    assert sorted(data[-1]["options"]) == sorted(
        [
            "/dev/serial/by-id/xyx",
            "/dev/ttyACM0",
            "/dev/ttyS0",
        ]
    )
    assert data[-1]["type"] == "select"


def test_ui_simple_device_schema_no_filter(coresys):
    """Test with simple schema without filter."""
    for device in (
        Device(
            "ttyACM0",
            Path("/dev/ttyACM0"),
            Path("/sys/bus/usb/002"),
            "tty",
            None,
            [],
            {"ID_VENDOR": "xy"},
            [],
        ),
        Device(
            "ttyUSB0",
            Path("/dev/ttyUSB0"),
            Path("/sys/bus/usb/001"),
            "tty",
            None,
            [Path("/dev/ttyS1"), Path("/dev/serial/by-id/xyx")],
            {"ID_VENDOR": "xy"},
            [],
        ),
        Device(
            "ttyS0",
            Path("/dev/ttyS0"),
            Path("/sys/bus/usb/003"),
            "tty",
            None,
            [],
            {},
            [],
        ),
        Device(
            "video1",
            Path("/dev/video1"),
            Path("/sys/bus/usb/004"),
            "misc",
            None,
            [],
            {"ID_VENDOR": "xy"},
            [],
        ),
    ):
        coresys.hardware.update_device(device)

    data = UiOptions(coresys)(
        {
            "name": "str",
            "password": "password",
            "fires": "bool",
            "alias": "str?",
            "input": "device",
        },
    )

    assert sorted(data[-1]["options"]) == sorted(
        ["/dev/serial/by-id/xyx", "/dev/ttyACM0", "/dev/ttyS0", "/dev/video1"]
    )
    assert data[-1]["type"] == "select"


def test_ui_schema_match_options(coresys):
    """Test simple alternation match patterns expose options for the UI."""
    data = UiOptions(coresys)(
        {
            "enabled_shares": [
                "match(^(?i:(addons|addon_configs|backup|config|media|share|ssl))$)"
            ],
            "protocol": "match(rsa|dsa|ecdsa|ed25519|rsa)",
            "port": "match(^(?:443|8443|10000)$)?",
        }
    )
    assert data[0] == {
        "name": "enabled_shares",
        "type": "string",
        "multiple": True,
        "required": True,
        "options": [
            "addons",
            "addon_configs",
            "backup",
            "config",
            "media",
            "share",
            "ssl",
        ],
    }
    # Duplicates are removed while preserving order
    assert data[1]["type"] == "string"
    assert data[1]["options"] == ["rsa", "dsa", "ecdsa", "ed25519"]
    assert data[2]["type"] == "string"
    assert data[2]["options"] == ["443", "8443", "10000"]
    assert data[2]["optional"] is True


def test_ui_schema_match_no_options(coresys):
    """Test non-enumerable match patterns stay plain string nodes."""
    data = UiOptions(coresys)(
        {
            "token": "match(^[a-f0-9]{32}$)",
            "network_key": "match(|[0-9a-fA-F]{32,32})?",
            "nested_groups": "match(^(a|b)|(c|d)$)",
            "extra_literal": "match(^(a|b)-suffix$)",
            "domain": "match(.+\\.duckdns\\.org)",
            "escaped": "match(^(a\\|b|c)$)",
        }
    )
    for node in data:
        assert node["type"] == "string"
        assert "options" not in node


def test_extract_match_options_validate():
    """Test every extracted option validates against its source pattern."""
    patterns = [
        "^(?i:(addons|addon_configs|backup|config|media|share|ssl))$",
        "rsa|dsa|ecdsa|ed25519|rsa",
        "^(?:443|8443|10000)$",
        "(?i)^(auto|manual)$",
    ]
    for pattern in patterns:
        options = _extract_match_options(pattern)
        assert options
        for option in options:
            assert re.match(pattern, option)


def test_log_entry(coresys, caplog):
    """Test log entry when no option match in schema."""
    options = AppOptions(coresys, {}, MOCK_ADDON_NAME, MOCK_ADDON_SLUG)({"test": "str"})
    assert isinstance(options, dict)
    assert not options
    assert (
        "Option 'test' does not exist in the schema for Mock Add-on (mock_addon)"
        in caplog.text
    )
