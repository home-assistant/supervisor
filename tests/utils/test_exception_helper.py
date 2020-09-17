"""Test exception helpers."""

from supervisor.utils import check_exception_chain


def test_simple_chain_exception():
    """Test simple chain of excepiton."""

    try:
        raise ValueError()
    except ValueError as err:
        assert check_exception_chain(err, ValueError)


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
