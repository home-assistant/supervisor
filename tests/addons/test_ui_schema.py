"""Test add-ons schema to UI schema convertion."""

from supervisor.addons.options import UiOptions


def test_simple_schema(coresys):
    """Test with simple schema."""
    assert UiOptions(coresys)(
        {"name": "str", "password": "password", "fires": "bool", "alias": "str?"},
    ) == [
        {"name": "name", "required": True, "type": "string"},
        {"format": "password", "name": "password", "required": True, "type": "string"},
        {"name": "fires", "required": True, "type": "boolean"},
        {"name": "alias", "optional": True, "type": "string"},
    ]


def test_group_schema(coresys):
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


def test_group_list(coresys):
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
