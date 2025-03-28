"""DBus implementation with glib."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Coroutine
import logging
from typing import Any, cast

from dbus_fast import (
    ErrorType,
    InvalidIntrospectionError,
    Message,
    MessageType,
    Variant,
)
from dbus_fast.aio.message_bus import MessageBus
from dbus_fast.aio.proxy_object import ProxyInterface, ProxyObject
from dbus_fast.errors import DBusError as DBusFastDBusError
from dbus_fast.introspection import Node
from log_rate_limit import RateLimit, StreamRateLimitFilter

from ..exceptions import (
    DBusError,
    DBusFatalError,
    DBusInterfaceError,
    DBusInterfaceMethodError,
    DBusInterfacePropertyError,
    DBusInterfaceSignalError,
    DBusNoReplyError,
    DBusNotConnectedError,
    DBusObjectError,
    DBusParseError,
    DBusServiceUnkownError,
    DBusTimedOutError,
    DBusTimeoutError,
    HassioNotSupportedError,
)
from .sentry import async_capture_exception

_LOGGER: logging.Logger = logging.getLogger(__name__)
_LOGGER.addFilter(StreamRateLimitFilter(period_sec=30, allow_next_n=2))

DBUS_INTERFACE_OBJECT_MANAGER: str = "org.freedesktop.DBus.ObjectManager"
DBUS_INTERFACE_PROPERTIES: str = "org.freedesktop.DBus.Properties"
DBUS_METHOD_GETALL: str = "org.freedesktop.DBus.Properties.GetAll"


class DBus:
    """DBus handler."""

    def __init__(self, bus: MessageBus, bus_name: str, object_path: str) -> None:
        """Initialize dbus object."""
        self.bus_name: str = bus_name
        self.object_path: str = object_path
        self._proxy_obj: ProxyObject | None = None
        self._proxies: dict[str, ProxyInterface] = {}
        self._bus: MessageBus = bus
        self._signal_monitors: dict[str, dict[str, list[Callable]]] = {}

    @staticmethod
    async def connect(bus: MessageBus, bus_name: str, object_path: str) -> DBus:
        """Read object data."""
        self = DBus(bus, bus_name, object_path)

        # pylint: disable=protected-access
        await self.init_proxy()

        _LOGGER.debug("Connect to D-Bus: %s - %s", bus_name, object_path)
        return self

    @staticmethod
    def from_dbus_error(err: DBusFastDBusError) -> HassioNotSupportedError | DBusError:
        """Return correct dbus error based on type."""
        if err.type == ErrorType.SERVICE_UNKNOWN:
            return DBusServiceUnkownError(err.text)
        if err.type == ErrorType.UNKNOWN_INTERFACE:
            return DBusInterfaceError(err.text)
        if err.type in {
            ErrorType.UNKNOWN_METHOD,
            ErrorType.INVALID_SIGNATURE,
            ErrorType.INVALID_ARGS,
        }:
            return DBusInterfaceMethodError(err.text)
        if err.type == ErrorType.UNKNOWN_OBJECT:
            return DBusObjectError(err.text)
        if err.type in {ErrorType.UNKNOWN_PROPERTY, ErrorType.PROPERTY_READ_ONLY}:
            return DBusInterfacePropertyError(err.text)
        if err.type == ErrorType.DISCONNECTED:
            return DBusNotConnectedError(err.text)
        if err.type == ErrorType.TIMEOUT:
            return DBusTimeoutError(err.text)
        if err.type == ErrorType.TIMED_OUT:
            return DBusTimedOutError(err.text)
        if err.type == ErrorType.NO_REPLY:
            return DBusNoReplyError(err.text)
        return DBusFatalError(err.text, type_=err.type)

    @staticmethod
    async def call_dbus(
        proxy_interface: ProxyInterface,
        method: str,
        *args,
        unpack_variants: bool = True,
    ) -> Any:
        """Call a dbus method and handle the signature and errors."""
        _LOGGER.debug(
            "D-Bus call - %s.%s on %s",
            proxy_interface.introspection.name,
            method,
            proxy_interface.path,
        )
        try:
            if unpack_variants:
                return await getattr(proxy_interface, method)(
                    *args, unpack_variants=True
                )
            return await getattr(proxy_interface, method)(*args)
        except DBusFastDBusError as err:
            _LOGGER.debug(
                "D-Bus fast error on call - %s.%s on %s: %s",
                proxy_interface.introspection.name,
                method,
                proxy_interface.path,
                err,
            )
            raise DBus.from_dbus_error(err) from None
        except Exception as err:  # pylint: disable=broad-except
            await async_capture_exception(err)
            raise DBusFatalError(str(err)) from err

    def _add_interfaces(self):
        """Make proxy interfaces out of introspection data."""
        self._proxies = {
            interface.name: self._proxy_obj.get_interface(interface.name)
            for interface in self._proxy_obj.introspection.interfaces
        }

    async def introspect(self) -> Node:
        """Return introspection for dbus object."""
        for _ in range(3):
            try:
                return await self._bus.introspect(
                    self.bus_name, self.object_path, timeout=30
                )
            except InvalidIntrospectionError as err:
                raise DBusParseError(
                    f"Can't parse introspect data: {err}", _LOGGER.error
                ) from err
            except DBusFastDBusError as err:
                raise DBus.from_dbus_error(err) from None
            except TimeoutError:
                # The systemd D-Bus activate service has a timeout of 25s, which will raise. We should
                # not end up here unless the D-Bus broker is majorly overwhelmed.
                _LOGGER.critical(
                    "Timeout connecting to %s - %s",
                    self.bus_name,
                    self.object_path,
                    extra=RateLimit(stream_id=f"dbus_timeout_{self.bus_name}"),
                )
            except EOFError:
                _LOGGER.warning(
                    "Busy system at %s - %s",
                    self.bus_name,
                    self.object_path,
                    extra=RateLimit(stream_id=f"dbus_eof_{self.bus_name}"),
                )

            await asyncio.sleep(3)

        raise DBusFatalError(
            "Could not get introspection data after 3 attempts", _LOGGER.error
        )

    async def init_proxy(self, *, introspection: Node | None = None) -> None:
        """Read interface data."""
        if not introspection:
            introspection = await self.introspect()

        # If we have a proxy obj store signal monitors and disconnect first
        signal_monitors = self._signal_monitors
        if self._proxy_obj:
            self.disconnect()

        self._proxy_obj = self.bus.get_proxy_object(
            self.bus_name, self.object_path, introspection
        )
        self._add_interfaces()

        # Reconnect existing signal monitors on new proxy obj if possible (introspection may have changed)
        for intr, signals in signal_monitors.items():
            for name, callbacks in signals.items():
                if intr in self._proxies and hasattr(self._proxies[intr], f"on_{name}"):
                    for callback in callbacks:
                        try:
                            getattr(self._proxies[intr], f"on_{name}")(
                                callback, unpack_variants=True
                            )
                            self._add_signal_monitor(intr, name, callback)
                        except Exception:  # pylint: disable=broad-except
                            _LOGGER.exception("Can't re-add signal listener")

    @property
    def proxies(self) -> dict[str, ProxyInterface]:
        """Return all proxies."""
        return self._proxies

    @property
    def bus(self) -> MessageBus:
        """Get message bus."""
        return self._bus

    @property
    def connected(self) -> bool:
        """Is connected."""
        return self._proxy_obj is not None

    @property
    def properties(self) -> DBusCallWrapper | None:
        """Get properties proxy interface."""
        if DBUS_INTERFACE_PROPERTIES not in self._proxies:
            return None
        return DBusCallWrapper(self, DBUS_INTERFACE_PROPERTIES)

    @property
    def object_manager(self) -> DBusCallWrapper | None:
        """Get object manager proxy interface."""
        if DBUS_INTERFACE_OBJECT_MANAGER not in self._proxies:
            return None
        return DBusCallWrapper(self, DBUS_INTERFACE_OBJECT_MANAGER)

    async def get_properties(self, interface: str) -> dict[str, Any]:
        """Read all properties from interface."""
        if not self.properties:
            raise DBusInterfaceError(
                f"DBus Object does not have interface {DBUS_INTERFACE_PROPERTIES}"
            )
        return await self.properties.call_get_all(interface)

    def sync_property_changes(
        self,
        interface: str,
        update: Callable[[dict[str, Any]], Coroutine[None]],
    ) -> Callable:
        """Sync property changes for interface with cache.

        Pass return value to `stop_sync_property_changes` to stop.
        """

        async def sync_property_change(
            prop_interface: str, changed: dict[str, Variant], invalidated: list[str]
        ):
            """Sync property changes to cache."""
            if interface != prop_interface:
                return

            _LOGGER.debug(
                "Property change for %s-%s: %s changed & %s invalidated",
                self.bus_name,
                self.object_path,
                list(changed.keys()),
                invalidated,
            )

            if invalidated:
                await update()
            else:
                await update(changed)

        self.properties.on_properties_changed(sync_property_change)
        return sync_property_change

    def stop_sync_property_changes(self, sync_property_change: Callable):
        """Stop syncing property changes with cache."""
        self.properties.off_properties_changed(sync_property_change)

    def disconnect(self):
        """Remove all active signal listeners."""
        for intr, signals in self._signal_monitors.items():
            for name, callbacks in signals.items():
                for callback in callbacks:
                    try:
                        getattr(self._proxies[intr], f"off_{name}")(
                            callback, unpack_variants=True
                        )
                    except Exception:  # pylint: disable=broad-except
                        _LOGGER.exception("Can't remove signal listener")

        self._signal_monitors = {}

    def signal(self, signal_member: str) -> DBusSignalWrapper:
        """Get signal context manager for this object."""
        return DBusSignalWrapper(self, signal_member)

    def _add_signal_monitor(
        self, interface: str, dbus_name: str, callback: Callable
    ) -> None:
        """Add a callback to the tracked signal monitors."""
        if interface not in self._signal_monitors:
            self._signal_monitors[interface] = {}

        if dbus_name not in self._signal_monitors[interface]:
            self._signal_monitors[interface][dbus_name] = [callback]

        else:
            self._signal_monitors[interface][dbus_name].append(callback)

    @property
    def _call_wrapper(self) -> DBusCallWrapper:
        """Get dbus call wrapper for current dbus object."""
        return DBusCallWrapper(self, self.bus_name)

    def __getattr__(self, name: str) -> DBusCallWrapper:
        """Map to dbus method."""
        return getattr(self._call_wrapper, name)

    def call(self, name: str, *args, unpack_variants: bool = True) -> Awaitable[Any]:
        """Call a dbus method."""
        return self._call_wrapper.call(name, *args, unpack_variants=unpack_variants)

    def get(self, name: str, *, unpack_variants: bool = True) -> Awaitable[Any]:
        """Get a dbus property value."""
        return self._call_wrapper.get(name, unpack_variants=unpack_variants)

    def set(self, name: str, value: Any) -> Awaitable[None]:
        """Set a dbus property."""
        return self._call_wrapper.set(name, value)

    def on(self, name: str, callback: Callable) -> None:
        """Add listener for a signal."""
        self._call_wrapper.on(name, callback)

    def off(self, name: str, callback: Callable) -> None:
        """Remove listener for a signal."""
        self._call_wrapper.off(name, callback)


class DBusCallWrapper:
    """Wrapper a DBus interface for a call."""

    def __init__(self, dbus: DBus, interface: str) -> None:
        """Initialize wrapper."""
        self.dbus: DBus = dbus
        self.interface: str = interface
        self._proxy: ProxyInterface | None = self.dbus._proxies.get(self.interface)

    def __call__(self, *args, **kwargs) -> None:
        """Catch this method from being called."""
        _LOGGER.error("D-Bus method %s not exists!", self.interface)
        raise DBusInterfaceMethodError()

    def _dbus_action(
        self, name: str
    ) -> DBusCallWrapper | Callable[..., Awaitable[Any]] | Callable[[Callable], None]:
        """Map to dbus method."""
        if not self._proxy:
            return DBusCallWrapper(self.dbus, f"{self.interface}.{name}")

        dbus_parts = name.split("_", 1)
        dbus_type = dbus_parts[0]

        if not hasattr(self._proxy, name):
            message = f"{name} does not exist in D-Bus interface {self.interface}!"
            if dbus_type == "call":
                raise DBusInterfaceMethodError(message, _LOGGER.error)
            if dbus_type == "get":
                raise DBusInterfacePropertyError(message, _LOGGER.error)
            if dbus_type == "set":
                raise DBusInterfacePropertyError(message, _LOGGER.error)
            if dbus_type in ["on", "off"]:
                raise DBusInterfaceSignalError(message, _LOGGER.error)

        # Can't wrap these since *args callbacks aren't supported. But can track them for automatic disconnect later
        if dbus_type in ["on", "off"]:
            _LOGGER.debug(
                "D-Bus signal monitor - %s.%s on %s",
                self.interface,
                name,
                self.dbus.object_path,
            )
            dbus_name = dbus_parts[1]

            if dbus_type == "on":

                def _on_signal(callback: Callable):
                    getattr(self._proxy, name)(callback, unpack_variants=True)

                    # pylint: disable=protected-access
                    self.dbus._add_signal_monitor(self.interface, dbus_name, callback)
                    # pylint: enable=protected-access

                return _on_signal

            def _off_signal(callback: Callable):
                getattr(self._proxy, name)(callback, unpack_variants=True)

                # pylint: disable=protected-access
                if (
                    self.interface not in self.dbus._signal_monitors
                    or dbus_name not in self.dbus._signal_monitors[self.interface]
                    or callback
                    not in self.dbus._signal_monitors[self.interface][dbus_name]
                ):
                    _LOGGER.warning(
                        "Signal listener not found for %s.%s", self.interface, dbus_name
                    )
                else:
                    self.dbus._signal_monitors[self.interface][dbus_name].remove(
                        callback
                    )

                    if not self.dbus._signal_monitors[self.interface][dbus_name]:
                        del self.dbus._signal_monitors[self.interface][dbus_name]
                        if not self.dbus._signal_monitors[self.interface]:
                            del self.dbus._signal_monitors[self.interface]
                # pylint: enable=protected-access

            return _off_signal

        if dbus_type in ["call", "get"]:

            def _method_wrapper(*args, unpack_variants: bool = True) -> Awaitable:
                return DBus.call_dbus(
                    self._proxy, name, *args, unpack_variants=unpack_variants
                )

            return _method_wrapper

        elif dbus_type == "set":

            def _set_wrapper(*args) -> Awaitable:
                return DBus.call_dbus(self._proxy, name, *args, unpack_variants=False)

            return _set_wrapper

        # Didn't reach the dbus call yet, just happened to hit another interface. Return a wrapper
        return DBusCallWrapper(self.dbus, f"{self.interface}.{name}")

    def __getattr__(self, name: str) -> DBusCallWrapper:
        """Map to a dbus method."""
        return cast(DBusCallWrapper, self._dbus_action(name))

    def call(self, name: str, *args, unpack_variants: bool = True) -> Awaitable[Any]:
        """Call a dbus method."""
        return cast(Callable[..., Awaitable[Any]], self._dbus_action(f"call_{name}"))(
            *args, unpack_variants=unpack_variants
        )

    def get(self, name: str, *, unpack_variants: bool = True) -> Awaitable[Any]:
        """Get a dbus property value."""
        return cast(Callable[[bool], Awaitable[Any]], self._dbus_action(f"get_{name}"))(
            unpack_variants=unpack_variants
        )

    def set(self, name: str, value: Any) -> Awaitable[None]:
        """Set a dbus property."""
        return cast(Callable[[Any], Awaitable[Any]], self._dbus_action(f"set_{name}"))(
            value
        )

    def on(self, name: str, callback: Callable) -> None:
        """Add listener for a signal."""
        cast(Callable[[Callable], None], self._dbus_action(f"on_{name}"))(callback)

    def off(self, name: str, callback: Callable) -> None:
        """Remove listener for a signal."""
        cast(Callable[[Callable], None], self._dbus_action(f"off_{name}"))(callback)


class DBusSignalWrapper:
    """Wrapper for D-Bus Signal."""

    def __init__(self, dbus: DBus, signal_member: str) -> None:
        """Initialize wrapper."""
        self._dbus: DBus = dbus
        signal_parts = signal_member.split(".")
        self._interface = ".".join(signal_parts[:-1])
        self._member = signal_parts[-1]
        self._match: str = f"type='signal',interface={self._interface},member={self._member},path={self._dbus.object_path}"
        self._messages: asyncio.Queue[Message] = asyncio.Queue()

    def _message_handler(self, msg: Message):
        if msg.message_type != MessageType.SIGNAL:
            return

        _LOGGER.debug(
            "Signal message received %s, %s.%s object %s",
            msg.body,
            msg.interface,
            msg.member,
            msg.path,
        )
        if (
            msg.interface != self._interface
            or msg.member != self._member
            or msg.path != self._dbus.object_path
        ):
            return

        self._messages.put_nowait(msg)

    async def __aenter__(self):
        """Install match for signals and start collecting signal messages."""
        _LOGGER.debug("Install match for signal %s.%s", self._interface, self._member)
        await self._dbus._bus.call(
            Message(
                destination="org.freedesktop.DBus",
                interface="org.freedesktop.DBus",
                path="/org/freedesktop/DBus",
                member="AddMatch",
                signature="s",
                body=[self._match],
            )
        )

        self._dbus._bus.add_message_handler(self._message_handler)
        return self

    async def wait_for_signal(self) -> Any:
        """Wait for signal and returns signal payload."""
        msg = await self._messages.get()
        return msg.body

    async def __aexit__(self, exc_t, exc_v, exc_tb):
        """Stop collecting signal messages and remove match for signals."""
        self._dbus._bus.remove_message_handler(self._message_handler)

        await self._dbus._bus.call(
            Message(
                destination="org.freedesktop.DBus",
                interface="org.freedesktop.DBus",
                path="/org/freedesktop/DBus",
                member="RemoveMatch",
                signature="s",
                body=[self._match],
            )
        )
