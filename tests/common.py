"""Common test functions."""
import asyncio
from importlib import import_module
import json
from pathlib import Path
from typing import Any

from dbus_fast.aio.message_bus import MessageBus
from dbus_fast.introspection import Method, Property, Signal

from supervisor.dbus.interface import DBusInterface, DBusInterfaceProxy
from supervisor.resolution.validate import get_valid_modules
from supervisor.utils.dbus import DBUS_INTERFACE_PROPERTIES
from supervisor.utils.yaml import read_yaml_file

from .dbus_service_mocks.base import DBusServiceMock


def get_dbus_name(intr_list: list[Method | Property | Signal], snake_case: str) -> str:
    """Find name in introspection list, fallback to ignore case match."""
    name = "".join([part.capitalize() for part in snake_case.split("_")])
    names = [item.name for item in intr_list]
    if name in names:
        return name

    # Acronyms like NTP can't be easily converted back to camel case. Fallback to ignore case match
    lower_name = name.lower()
    for val in names:
        if lower_name == val.lower():
            return val

    raise AttributeError(f"Could not find match for {name} in D-Bus introspection!")


def fire_watched_signal(dbus: DBusInterface, signal: str, data: list[Any] | str):
    """Test firing a watched signal."""
    if isinstance(data, str) and exists_fixture(data):
        data = load_json_fixture(data)

    if not isinstance(data, list):
        raise ValueError("Data must be a list!")

    signal_parts = signal.split(".")
    interface = ".".join(signal_parts[:-1])
    name = signal_parts[-1]

    # pylint: disable=protected-access
    assert interface in dbus.dbus._signal_monitors

    signals = dbus.dbus._proxies[interface].introspection.signals
    signal_monitors = {
        get_dbus_name(signals, k): v
        for k, v in dbus.dbus._signal_monitors[interface].items()
    }
    assert name in signal_monitors

    for coro in [callback(*data) for callback in signal_monitors[name]]:
        asyncio.create_task(coro)


def fire_property_change_signal(
    dbus: DBusInterfaceProxy,
    changed: dict[str, Any] | None = None,
    invalidated: list[str] | None = None,
):
    """Fire a property change signal for an interface proxy."""
    fire_watched_signal(
        dbus,
        f"{DBUS_INTERFACE_PROPERTIES}.PropertiesChanged",
        [dbus.properties_interface, changed or {}, invalidated or []],
    )


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
) -> dict[str, list[DBusServiceMock] | DBusServiceMock]:
    """Mock specified dbus services on bus.

    to_mock is dictionary where the key is a dbus service to mock (module must exist
    in dbus_service_mocks). Value is the object path for the mocked service. Can also
    be a list of object paths or None (if the mocked service defines the object path).
    """
    services: dict[str, list[DBusServiceMock] | DBusServiceMock] = {}
    requested_names: set[str] = set()

    for module in get_valid_modules("dbus_service_mocks", base=__file__):
        if module in to_mock:
            service_module = import_module(f"{__package__}.dbus_service_mocks.{module}")

            if service_module.BUS_NAME not in requested_names:
                await bus.request_name(service_module.BUS_NAME)
                requested_names.add(service_module.BUS_NAME)

            if isinstance(to_mock[module], list):
                services[module] = [
                    service_module.setup(obj_path).export(bus)
                    for obj_path in to_mock[module]
                ]
            else:
                services[module] = service_module.setup(to_mock[module]).export(bus)

    return services
