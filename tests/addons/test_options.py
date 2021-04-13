"""Test add-ons schema to UI schema convertion."""
from pathlib import Path

import pytest
import voluptuous as vol

from supervisor.addons.options import AddonOptions, UiOptions
from supervisor.hardware.data import Device

MOCK_ADDON_NAME = "Mock Add-on"
MOCK_ADDON_SLUG = "mock_addon"


def test_simple_schema(coresys):
    """Test with simple schema."""
    assert AddonOptions(
        coresys,
        {"name": "str", "password": "password", "fires": "bool", "alias": "str?"},
        MOCK_ADDON_NAME,
        MOCK_ADDON_SLUG,
    )({"name": "Pascal", "password": "1234", "fires": True, "alias": "test"})

    assert AddonOptions(
        coresys,
        {"name": "str", "password": "password", "fires": "bool", "alias": "str?"},
        MOCK_ADDON_NAME,
        MOCK_ADDON_SLUG,
    )({"name": "Pascal", "password": "1234", "fires": True})

    with pytest.raises(vol.error.Invalid):
        AddonOptions(
            coresys,
            {"name": "str", "password": "password", "fires": "bool", "alias": "str?"},
            MOCK_ADDON_NAME,
            MOCK_ADDON_SLUG,
        )({"name": "Pascal", "password": "1234", "fires": "hah"})

    with pytest.raises(vol.error.Invalid):
        AddonOptions(
            coresys,
            {"name": "str", "password": "password", "fires": "bool", "alias": "str?"},
            MOCK_ADDON_NAME,
            MOCK_ADDON_SLUG,
        )({"name": "Pascal", "fires": True})


def test_complex_schema_list(coresys):
    """Test with complex list schema."""
    assert AddonOptions(
        coresys,
        {"name": "str", "password": "password", "extend": ["str"]},
        MOCK_ADDON_NAME,
        MOCK_ADDON_SLUG,
    )({"name": "Pascal", "password": "1234", "extend": ["test", "blu"]})

    with pytest.raises(vol.error.Invalid):
        AddonOptions(
            coresys,
            {"name": "str", "password": "password", "extend": ["str"]},
            MOCK_ADDON_NAME,
            MOCK_ADDON_SLUG,
        )({"name": "Pascal", "password": "1234", "extend": ["test", 1]})

    with pytest.raises(vol.error.Invalid):
        AddonOptions(
            coresys,
            {"name": "str", "password": "password", "extend": ["str"]},
            MOCK_ADDON_NAME,
            MOCK_ADDON_SLUG,
        )({"name": "Pascal", "password": "1234", "extend": "test"})


def test_optional_schema_list(coresys):
    """Test with an optional list schema."""
    assert AddonOptions(
        coresys,
        {"name": "str", "password": "password", "extend": ["str?"]},
        MOCK_ADDON_NAME,
        MOCK_ADDON_SLUG,
    )({"name": "Pascal", "password": "1234"})

    assert AddonOptions(
        coresys,
        {"name": "str", "password": "password", "extend": ["str?"]},
        MOCK_ADDON_NAME,
        MOCK_ADDON_SLUG,
    )({"name": "Pascal", "password": "1234", "extend": []})

    with pytest.raises(vol.error.Invalid):
        AddonOptions(
            coresys,
            {"name": "str", "password": "password", "extend": ["str"]},
            MOCK_ADDON_NAME,
            MOCK_ADDON_SLUG,
        )({"name": "Pascal", "password": "1234"})

    assert AddonOptions(
        coresys,
        {"name": "str", "password": "password", "extend": ["str"]},
        MOCK_ADDON_NAME,
        MOCK_ADDON_SLUG,
    )({"name": "Pascal", "password": "1234", "extend": []})


def test_complex_schema_dict(coresys):
    """Test with complex dict schema."""
    assert AddonOptions(
        coresys,
        {"name": "str", "password": "password", "extend": {"test": "int"}},
        MOCK_ADDON_NAME,
        MOCK_ADDON_SLUG,
    )({"name": "Pascal", "password": "1234", "extend": {"test": 1}})

    with pytest.raises(vol.error.Invalid):
        AddonOptions(
            coresys,
            {"name": "str", "password": "password", "extend": {"test": "int"}},
            MOCK_ADDON_NAME,
            MOCK_ADDON_SLUG,
        )({"name": "Pascal", "password": "1234", "extend": {"wrong": 1}})

    with pytest.raises(vol.error.Invalid):
        AddonOptions(
            coresys,
            {"name": "str", "password": "password", "extend": ["str"]},
            MOCK_ADDON_NAME,
            MOCK_ADDON_SLUG,
        )({"name": "Pascal", "password": "1234", "extend": "test"})


def test_simple_device_schema(coresys):
    """Test with simple schema."""
    for device in (
        Device(
            "ttyACM0",
            Path("/dev/ttyACM0"),
            Path("/sys/bus/usb/002"),
            "tty",
            [],
            {"ID_VENDOR": "xy"},
        ),
        Device(
            "ttyUSB0",
            Path("/dev/ttyUSB0"),
            Path("/sys/bus/usb/001"),
            "tty",
            [Path("/dev/ttyS1"), Path("/dev/serial/by-id/xyx")],
            {"ID_VENDOR": "xy"},
        ),
        Device("ttyS0", Path("/dev/ttyS0"), Path("/sys/bus/usb/003"), "tty", [], {}),
        Device(
            "video1",
            Path("/dev/video1"),
            Path("/sys/bus/usb/004"),
            "misc",
            [],
            {"ID_VENDOR": "xy"},
        ),
    ):
        coresys.hardware.update_device(device)

    assert AddonOptions(
        coresys,
        {"name": "str", "password": "password", "input": "device"},
        MOCK_ADDON_NAME,
        MOCK_ADDON_SLUG,
    )({"name": "Pascal", "password": "1234", "input": "/dev/ttyUSB0"})

    data = AddonOptions(
        coresys,
        {"name": "str", "password": "password", "input": "device"},
        MOCK_ADDON_NAME,
        MOCK_ADDON_SLUG,
    )({"name": "Pascal", "password": "1234", "input": "/dev/serial/by-id/xyx"})
    assert data["input"] == "/dev/ttyUSB0"

    assert AddonOptions(
        coresys,
        {"name": "str", "password": "password", "input": "device(subsystem=tty)"},
        MOCK_ADDON_NAME,
        MOCK_ADDON_SLUG,
    )({"name": "Pascal", "password": "1234", "input": "/dev/ttyACM0"})

    with pytest.raises(vol.error.Invalid):
        assert AddonOptions(
            coresys,
            {"name": "str", "password": "password", "input": "device"},
            MOCK_ADDON_NAME,
            MOCK_ADDON_SLUG,
        )({"name": "Pascal", "password": "1234", "input": "/dev/not_exists"})

    with pytest.raises(vol.error.Invalid):
        assert AddonOptions(
            coresys,
            {"name": "str", "password": "password", "input": "device(subsystem=tty)"},
            MOCK_ADDON_NAME,
            MOCK_ADDON_SLUG,
        )({"name": "Pascal", "password": "1234", "input": "/dev/video1"})


def test_simple_schema_password(coresys):
    """Test with simple schema password pwned."""
    validate = AddonOptions(
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
            [],
            {"ID_VENDOR": "xy"},
        ),
        Device(
            "ttyUSB0",
            Path("/dev/ttyUSB0"),
            Path("/sys/bus/usb/001"),
            "tty",
            [Path("/dev/ttyS1"), Path("/dev/serial/by-id/xyx")],
            {"ID_VENDOR": "xy"},
        ),
        Device("ttyS0", Path("/dev/ttyS0"), Path("/sys/bus/usb/003"), "tty", [], {}),
        Device(
            "video1",
            Path("/dev/video1"),
            Path("/sys/bus/usb/004"),
            "misc",
            [],
            {"ID_VENDOR": "xy"},
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
            [],
            {"ID_VENDOR": "xy"},
        ),
        Device(
            "ttyUSB0",
            Path("/dev/ttyUSB0"),
            Path("/sys/bus/usb/001"),
            "tty",
            [Path("/dev/ttyS1"), Path("/dev/serial/by-id/xyx")],
            {"ID_VENDOR": "xy"},
        ),
        Device("ttyS0", Path("/dev/ttyS0"), Path("/sys/bus/usb/003"), "tty", [], {}),
        Device(
            "video1",
            Path("/dev/video1"),
            Path("/sys/bus/usb/004"),
            "misc",
            [],
            {"ID_VENDOR": "xy"},
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


def test_log_entry(coresys, caplog):
    """Test log entry when no option match in schema."""
    options = AddonOptions(coresys, {}, MOCK_ADDON_NAME, MOCK_ADDON_SLUG)(
        {"test": "str"}
    )
    assert options == {}
    assert (
        "Option 'test' does not exist in the schema for Mock Add-on (mock_addon)"
        in caplog.text
    )
