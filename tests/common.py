"""Common test functions."""

import asyncio
from collections.abc import Callable, Sequence
from datetime import datetime
from functools import partial
from importlib import import_module
from inspect import getclosurevars
import json
from pathlib import Path
from typing import Any, Self

from dbus_fast.aio.message_bus import MessageBus

from supervisor.apps.app import App
from supervisor.const import AppState, BusEvent
from supervisor.coresys import CoreSys
from supervisor.docker.const import ContainerState
from supervisor.jobs.decorator import Job
from supervisor.resolution.validate import get_valid_modules
from supervisor.utils.yaml import read_yaml_file

from .dbus_service_mocks.base import DBusServiceMock


def force_app_state(app: App, state: AppState) -> None:
    """Drive an app's derived state to ``state`` by setting underlying signals.

    The ``App.state`` property is purely derived from the last observed
    container state and an operation-error flag. Tests sometimes need a
    specific AppState as setup without spinning up real Docker events;
    this helper maps each AppState back to plausible signals and emits
    the resulting transition through the normal side-effect path.
    """
    # pylint: disable=protected-access
    old_state = app.state
    app._operation_error = False
    match state:
        case AppState.UNKNOWN:
            app._container_state = None
        case AppState.STOPPED:
            app._container_state = ContainerState.STOPPED
        case AppState.STARTED:
            app._container_state = ContainerState.HEALTHY
        case AppState.STARTUP:
            app._container_state = ContainerState.RUNNING
            # STARTUP only resolves from RUNNING when the container has a
            # healthcheck configured; ensure one is present in the mocked
            # container metadata.
            meta = app.instance._meta or {}
            meta.setdefault("Config", {})["Healthcheck"] = {"Test": ["CMD", "true"]}
            app.instance._meta = meta
        case AppState.ERROR:
            app._operation_error = True
    app._emit_state_change(old_state)


async def fire_bus_event(coresys: CoreSys, event: BusEvent, data: Any) -> None:
    """Fire a bus event and await its listener tasks.

    ``Bus.fire_event`` is sync and returns the listener tasks it spawned.
    Tests that drive a system under test by firing a bus event need to
    wait for those listener tasks to finish before asserting; this helper
    bundles the gather so call sites stay short.
    """
    await asyncio.gather(*coresys.bus.fire_event(event, data))


async def wait_for(
    predicate: Callable[[], bool],
    *,
    timeout: float = 5.0,
    interval: float = 0.01,
) -> None:
    """Poll a synchronous predicate until truthy or the deadline elapses.

    Useful when a test fires a D-Bus signal (or another out-of-band
    trigger) and needs to observe state mutated by the resulting async
    chain — e.g. a signal handler that schedules its own follow-up
    tasks. Completes the moment the predicate is true, so the wait
    costs only what's actually needed; this avoids the choice between a
    fixed sleep that's fast on idle and racy under load and a fixed
    sleep that's robust under load and wasteful on idle.
    """
    deadline = asyncio.get_running_loop().time() + timeout
    while not predicate():
        if asyncio.get_running_loop().time() >= deadline:
            raise AssertionError(f"Predicate did not become true within {timeout}s")
        await asyncio.sleep(interval)


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


def is_in_list(a: list, b: list):
    """Check if all elements in list a are in list b in order.

    Taken from https://stackoverflow.com/a/69175987/12156188.
    """

    for c in a:
        if c in b:
            b = b[b.index(c) :]
        else:
            return False
    return True


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


class AsyncIterator:
    """Make list/fixture into async iterator for test mocks."""

    def __init__(self, seq: Sequence[Any]) -> None:
        """Initialize with sequence."""
        self.iter = iter(seq)

    def __aiter__(self) -> Self:
        """Implement aiter."""
        return self

    async def __anext__(self) -> Any:
        """Return next in sequence."""
        try:
            return next(self.iter)
        except StopIteration:
            raise StopAsyncIteration from None
