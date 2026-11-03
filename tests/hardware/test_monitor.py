"""Test hardware monitor."""

from pathlib import Path
import threading
from unittest.mock import MagicMock, patch

import pytest
import pyudev

from supervisor.coresys import CoreSys
from supervisor.hardware.const import UdevKernelAction

# pylint: disable=protected-access

SYS_PATH = "/sys/devices/platform/usb1/1-1/ttyUSB0"


def _kernel_event() -> MagicMock:
    """Return a kernel add event for a serial device."""
    kernel = MagicMock(spec=pyudev.Device)
    kernel.action = UdevKernelAction.ADD
    kernel.device_node = "/dev/ttyUSB0"
    kernel.sys_path = SYS_PATH
    return kernel


def _udev_device(initialized: bool) -> MagicMock:
    """Return a udev device as returned by pyudev."""
    udev = MagicMock(spec=pyudev.Device)
    udev.is_initialized = initialized
    udev.sys_name = "ttyUSB0"
    udev.device_node = "/dev/ttyUSB0"
    udev.sys_path = SYS_PATH
    udev.subsystem = "tty"
    udev.parent = None
    udev.device_links = []
    udev.properties = {"ID_VENDOR": "test"}
    udev.children = []
    udev.__len__.return_value = len(udev.properties)
    return udev


@pytest.mark.parametrize(
    ("lookups", "expected_calls"),
    [
        pytest.param([True], 1, id="initialized"),
        pytest.param([None, True], 2, id="not_found_then_initialized"),
        pytest.param([False, True], 2, id="not_initialized_then_initialized"),
        pytest.param([False, False, False], 3, id="never_initialized"),
    ],
)
async def test_udev_add_event_looks_up_device_in_executor(
    coresys: CoreSys, lookups: list[bool | None], expected_calls: int
) -> None:
    """Test add event reads the device from udev without blocking the event loop."""
    threads: list[threading.Thread] = []
    results = iter(lookups)

    def _from_sys_path(context: pyudev.Context, sys_path: str) -> MagicMock:
        threads.append(threading.current_thread())
        assert sys_path == SYS_PATH
        if (initialized := next(results)) is None:
            raise pyudev.DeviceNotFoundAtPathError(sys_path)
        return _udev_device(initialized)

    with (
        patch("supervisor.hardware.monitor.asyncio.sleep"),
        patch.object(pyudev.Devices, "from_sys_path", _from_sys_path),
    ):
        await coresys.hardware.monitor._async_udev_events(_kernel_event())

    assert len(threads) == expected_calls
    assert threading.main_thread() not in threads
    assert coresys.hardware.get_by_path(Path(SYS_PATH)).name == "ttyUSB0"


async def test_udev_add_event_device_not_found(
    coresys: CoreSys, caplog: pytest.LogCaptureFixture
) -> None:
    """Test add event is ignored if udev never finds the device."""
    with (
        patch("supervisor.hardware.monitor.asyncio.sleep"),
        patch.object(
            pyudev.Devices,
            "from_sys_path",
            side_effect=pyudev.DeviceNotFoundAtPathError(SYS_PATH),
        ) as from_sys_path,
    ):
        await coresys.hardware.monitor._async_udev_events(_kernel_event())

    assert from_sys_path.call_count == 3
    assert not coresys.hardware.exists_device_node(Path("/dev/ttyUSB0"))
    assert f"Ignore device {SYS_PATH} / fails to initialize by udev" in caplog.text
