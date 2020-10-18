"""Test exception helpers."""

from supervisor.utils import check_exception_chain, get_message_from_exception_chain


def test_simple_chain_exception():
    """Test simple chain of excepiton."""

    try:
        raise ValueError()
    except ValueError as err:
        assert check_exception_chain(err, ValueError)


def test_simple_chain_exception_not():
    """Test simple chain of excepiton."""

    try:
        raise ValueError()
    except ValueError as err:
        assert not check_exception_chain(err, KeyError)


def test_simple_nested_chain_exception():
    """Test simple nested chain of excepiton."""

    try:
        try:
            raise ValueError()
        except ValueError as err:
            raise KeyError() from err
    except KeyError as err:
        assert check_exception_chain(err, ValueError)


def test_list_nested_chain_exception():
    """Test list nested chain of excepiton."""

    try:
        try:
            raise ValueError()
        except ValueError as err:
            raise KeyError() from err
    except KeyError as err:
        assert check_exception_chain(err, (ValueError, OSError))


def test_list_nested_chain_exception_not():
    """Test list nested chain of excepiton."""

    try:
        try:
            raise ValueError()
        except ValueError as err:
            raise KeyError() from err
    except KeyError as err:
        assert not check_exception_chain(err, (AssertionError, OSError))


def test_simple_chain_exception_message():
    """Test simple chain of excepiton."""

    try:
        raise ValueError("error")
    except ValueError as err:
        assert get_message_from_exception_chain(err) == "error"


def test_simple_chain_exception_not_message():
    """Test simple chain of excepiton."""

    try:
        raise ValueError()
    except ValueError as err:
        assert not get_message_from_exception_chain(err)


def test_simple_nested_chain_exception_message():
    """Test simple nested chain of excepiton."""

    try:
        try:
            raise ValueError("error")
        except ValueError as err:
            raise KeyError() from err
    except KeyError as err:
        assert get_message_from_exception_chain(err) == "error"
