"""Test add-ons schema to UI schema convertion."""

from hassio.addons.validate import schema_ui_options


def test_simple_schema():
    """Test with simple schema."""
    assert schema_ui_options(
        {"name": "str", "password": "password", "fires": "bool", "alias": "str?"}
    ) == [
        {"name": "name", "required": True, "type": "string"},
        {"format": "password", "name": "password", "required": True, "type": "string"},
        {"name": "fires", "required": True, "type": "boolean"},
        {"name": "alias", "optional": True, "type": "string"},
    ]


def test_group_schema():
    """Test with group schema."""
    assert schema_ui_options(
        {
            "name": "str",
            "password": "password",
            "fires": "bool",
            "alias": "str?",
            "extended": {"name": "str", "data": ["str"], "path": "str?"},
        }
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
                {"mutliple": True, "name": "data", "required": True, "type": "string"},
                {"name": "path", "optional": True, "type": "string"},
            ],
            "type": "schema",
        },
    ]


def test_group_list():
    """Test with group schema."""
    assert schema_ui_options(
        {
            "name": "str",
            "password": "password",
            "fires": "bool",
            "alias": "str?",
            "extended": [{"name": "str", "data": ["str?"], "path": "str?"}],
        }
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
                {"mutliple": True, "name": "data", "optional": True, "type": "string"},
                {"name": "path", "optional": True, "type": "string"},
            ],
            "type": "schema",
        },
    ]
