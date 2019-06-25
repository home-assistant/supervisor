"""Common test functions."""
import json
from pathlib import Path


def load_json_fixture(filename):
    """Load a fixture."""
    path = Path(Path(__file__).parent.joinpath("fixtures"), filename)
    return json.loads(path.read_text())


def mock_coro(return_value=None, exception=None):
    """Return a coro that returns a value or raise an exception."""
    return mock_coro_func(return_value, exception)()


def mock_coro_func(return_value=None, exception=None):
    """Return a method to create a coro function that returns a value."""

    async def coro(*args, **kwargs):
        """Fake coroutine."""
        if exception:
            raise exception
        return return_value

    return coro
