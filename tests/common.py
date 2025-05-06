"""Common test functions."""

import asyncio
from datetime import datetime
from functools import partial
from importlib import import_module
from inspect import getclosurevars
import json
from pathlib import Path
from typing import Any

from dbus_fast.aio.message_bus import MessageBus

from supervisor.jobs.decorator import Job
from supervisor.resolution.validate import get_valid_modules
from supervisor.utils.yaml import read_yaml_file

from .dbus_service_mocks.base import DBusServiceMock


def get_fixture_path(filename: str) -> Path:
    """Get path for fixture."""
    return Path(Path(__file__).parent.joinpath("fixtures"), filename)


def load_json_fixture(filename: str) -> Any:
    """Load a json fixture."""
    path = get_fixture_path(filename)
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml_fixture(filename: str) -> Any:
    """Load a YAML fixture."""
    path = get_fixture_path(filename)
    return read_yaml_file(path)


def load_fixture(filename: str) -> str:
    """Load a fixture."""
    path = get_fixture_path(filename)
    return path.read_text(encoding="utf-8")


def load_binary_fixture(filename: str) -> bytes:
    """Load a fixture without decoding."""
    path = get_fixture_path(filename)
    return path.read_bytes()


def exists_fixture(filename: str) -> bool:
    """Check if a fixture exists."""
    path = get_fixture_path(filename)
    return path.exists()


async def mock_dbus_services(
    to_mock: dict[str, list[str] | str | None], bus: MessageBus
) -> dict[str, dict[str, DBusServiceMock] | DBusServiceMock]:
    """Mock specified dbus services on bus.

    to_mock is dictionary where the key is a dbus service to mock (module must exist
    in dbus_service_mocks). Value is the object path for the mocked service. Can also
    be a list of object paths or None (if the mocked service defines the object path).

    A dictionary is returned where the key is the dbus service to mock and the value
    is the instance of the mocked service. If a list of object paths is provided,
    the value is a dictionary where the key is the object path and value is the
    mocked instance of the service for that object path.
    """
    services: dict[str, list[DBusServiceMock] | DBusServiceMock] = {}
    requested_names: set[str] = set()

    for module in await asyncio.get_running_loop().run_in_executor(
        None, partial(get_valid_modules, base=__file__), "dbus_service_mocks"
    ):
        if module in to_mock:
            service_module = import_module(f"{__package__}.dbus_service_mocks.{module}")

            if service_module.BUS_NAME not in requested_names:
                await bus.request_name(service_module.BUS_NAME)
                requested_names.add(service_module.BUS_NAME)

            if isinstance(to_mock[module], list):
                services[module] = {
                    obj_path: service_module.setup(obj_path).export(bus)
                    for obj_path in to_mock[module]
                }
            else:
                services[module] = service_module.setup(to_mock[module]).export(bus)

    return services


def get_job_decorator(func) -> Job:
    """Get Job object of decorated function."""
    # Access the closure of the wrapper function
    job = getclosurevars(func).nonlocals["self"]
    if not isinstance(job, Job):
        raise TypeError(f"{func.__qualname__} is not a Job")
    return job


def reset_last_call(func, group: str | None = None) -> None:
    """Reset last call for a function using the Job decorator."""
    get_job_decorator(func).set_last_call(datetime.min, group)


class MockResponse:
    """Mock response for aiohttp requests."""

    def __init__(self, *, status=200, text=""):
        """Initialize mock response."""
        self.status = status
        self._text = text

    def update_text(self, text: str):
        """Update the text of the response."""
        self._text = text

    async def read(self):
        """Read the response body."""
        return self._text.encode("utf-8")

    async def text(self) -> str:
        """Return the response body as text."""
        return self._text

    async def __aenter__(self):
        """Enter the context manager."""
        return self

    async def __aexit__(self, exc_type, exc, tb):
        """Exit the context manager."""
