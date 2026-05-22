"""Test exception helpers."""

import pytest

from supervisor.utils import check_exception_chain, get_message_from_exception_chain


def _raise_value_error(message: str | None = None) -> None:
    """Raise a ValueError, optionally with a message."""
    if message is None:
        raise ValueError
    raise ValueError(message)


def _raise_key_error_from_value_error(value_message: str | None = None) -> None:
    """Raise a KeyError chained from a ValueError."""
    try:
        _raise_value_error(value_message)
    except ValueError as err:
        raise KeyError from err


def test_simple_chain_exception():
    """Test simple chain of exception."""
    with pytest.raises(ValueError, match="^$") as exc_info:
        _raise_value_error()
    assert check_exception_chain(exc_info.value, ValueError)


def test_simple_chain_exception_not():
    """Test simple chain of exception."""
    with pytest.raises(ValueError, match="^$") as exc_info:
        _raise_value_error()
    assert not check_exception_chain(exc_info.value, KeyError)


def test_simple_nested_chain_exception():
    """Test simple nested chain of exception."""
    with pytest.raises(KeyError) as exc_info:
        _raise_key_error_from_value_error()
    assert check_exception_chain(exc_info.value, ValueError)


def test_list_nested_chain_exception():
    """Test list nested chain of exception."""
    with pytest.raises(KeyError) as exc_info:
        _raise_key_error_from_value_error()
    assert check_exception_chain(exc_info.value, (ValueError, OSError))


def test_list_nested_chain_exception_not():
    """Test list nested chain of exception."""
    with pytest.raises(KeyError) as exc_info:
        _raise_key_error_from_value_error()
    assert not check_exception_chain(exc_info.value, (AssertionError, OSError))


def test_simple_chain_exception_message():
    """Test simple chain of exception."""
    with pytest.raises(ValueError, match="^error$") as exc_info:
        _raise_value_error("error")
    assert get_message_from_exception_chain(exc_info.value) == "error"


def test_simple_chain_exception_not_message():
    """Test simple chain of exception."""
    with pytest.raises(ValueError, match="^$") as exc_info:
        _raise_value_error()
    assert not get_message_from_exception_chain(exc_info.value)


def test_simple_nested_chain_exception_message():
    """Test simple nested chain of exception."""
    with pytest.raises(KeyError) as exc_info:
        _raise_key_error_from_value_error("error")
    assert get_message_from_exception_chain(exc_info.value) == "error"
