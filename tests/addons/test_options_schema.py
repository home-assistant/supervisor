"""Test add-ons schema to UI schema convertion."""

import pytest
import voluptuous as vol

from supervisor.addons.validate import validate_options


def test_simple_schema(coresys):
    """Test with simple schema."""
    assert validate_options(
        coresys,
        {"name": "str", "password": "password", "fires": "bool", "alias": "str?"},
    )({"name": "Pascal", "password": "1234", "fires": True, "alias": "test"})

    assert validate_options(
        coresys,
        {"name": "str", "password": "password", "fires": "bool", "alias": "str?"},
    )({"name": "Pascal", "password": "1234", "fires": True})

    with pytest.raises(vol.error.Invalid):
        validate_options(
            coresys,
            {"name": "str", "password": "password", "fires": "bool", "alias": "str?"},
        )({"name": "Pascal", "password": "1234", "fires": "hah"})

    with pytest.raises(vol.error.Invalid):
        validate_options(
            coresys,
            {"name": "str", "password": "password", "fires": "bool", "alias": "str?"},
        )({"name": "Pascal", "fires": True})


def test_complex_schema_list(coresys):
    """Test with complex list schema."""
    assert validate_options(
        coresys, {"name": "str", "password": "password", "extend": ["str"]},
    )({"name": "Pascal", "password": "1234", "extend": ["test", "blu"]})

    with pytest.raises(vol.error.Invalid):
        validate_options(
            coresys, {"name": "str", "password": "password", "extend": ["str"]},
        )({"name": "Pascal", "password": "1234", "extend": ["test", 1]})

    with pytest.raises(vol.error.Invalid):
        validate_options(
            coresys, {"name": "str", "password": "password", "extend": ["str"]},
        )({"name": "Pascal", "password": "1234", "extend": "test"})


def test_complex_schema_dict(coresys):
    """Test with complex dict schema."""
    assert validate_options(
        coresys, {"name": "str", "password": "password", "extend": {"test": "int"}},
    )({"name": "Pascal", "password": "1234", "extend": {"test": 1}})

    with pytest.raises(vol.error.Invalid):
        validate_options(
            coresys, {"name": "str", "password": "password", "extend": {"test": "int"}},
        )({"name": "Pascal", "password": "1234", "extend": {"wrong": 1}})

    with pytest.raises(vol.error.Invalid):
        validate_options(
            coresys, {"name": "str", "password": "password", "extend": ["str"]},
        )({"name": "Pascal", "password": "1234", "extend": "test"})
