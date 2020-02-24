"""Read hardware info from system."""
import asyncio
from datetime import datetime
import logging
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Set

import attr
import pyudev

from ..const import ATTR_DEVICES, ATTR_NAME, ATTR_TYPE, CHAN_ID, CHAN_TYPE
from ..exceptions import HardwareNotSupportedError


_LOGGER: logging.Logger = logging.getLogger(__name__)

ASOUND_CARDS: Path = Path("/proc/asound/cards")
RE_CARDS: re.Pattern = re.compile(r"(\d+) \[(\w*) *\]: (.*\w)")

ASOUND_DEVICES: Path = Path("/proc/asound/devices")
RE_DEVICES: re.Pattern = re.compile(r"\[.*(\d+)- (\d+).*\]: ([\w ]*)")

PROC_STAT: Path = Path("/proc/stat")
RE_BOOT_TIME: re.Pattern = re.compile(r"btime (\d+)")

GPIO_DEVICES: Path = Path("/sys/class/gpio")
SOC_DEVICES: Path = Path("/sys/devices/platform/soc")
RE_TTY: re.Pattern = re.compile(r"tty[A-Z]+")

RE_VIDEO_DEVICES = re.compile(r"^(?:vchiq|cec\d+|video\d+)")


@attr.s(frozen=True)
class Device:
    """Represent a device."""

    name: str = attr.ib()
    path: Path = attr.ib()
    links: List[Path] = attr.ib()


class Hardware:
    """Representation of an interface to procfs, sysfs and udev."""

    def __init__(self):
        """Init hardware object."""
        self.context = pyudev.Context()

    @property
    def devices(self) -> List[Device]:
        """Return a list of all available devices."""
        dev_list: List[Device] = []

        # Exctract all devices
        for device in self.context.list_devices():
            # Skip devices without mapping
            if not device.device_node:
                continue

            dev_list.append(
                Device(
                    device.sys_name,
                    Path(device.device_node),
                    [Path(node) for node in device.device_links],
                )
            )

        return dev_list

    @property
    def video_devices(self) -> List[Device]:
        """Return all available video devices."""
        dev_list: List[Device] = []

        for device in self.devices:
            if not RE_VIDEO_DEVICES.match(device.name):
                continue
            dev_list.append(device)

        return dev_list

    @property
    def serial_devices(self) -> Set[str]:
        """Return all serial and connected devices."""
        dev_list: Set[str] = set()
        for device in self.context.list_devices(subsystem="tty"):
            if "ID_VENDOR" in device.properties or RE_TTY.search(device.device_node):
                dev_list.add(device.device_node)

        return dev_list

    @property
    def serial_by_id(self) -> Set[str]:
        """Return all /dev/serial/by-id for serial devices."""
        dev_list: Set[str] = set()
        for device in self.context.list_devices(subsystem="tty"):
            if "ID_VENDOR" in device.properties or RE_TTY.search(device.device_node):
                # Add /dev/serial/by-id devlink for current device
                for dev_link in device.device_links:
                    if not dev_link.startswith("/dev/serial/by-id"):
                        continue
                    dev_list.add(dev_link)

        return dev_list

    @property
    def input_devices(self) -> Set[str]:
        """Return all input devices."""
        dev_list: Set[str] = set()
        for device in self.context.list_devices(subsystem="input"):
            if "NAME" in device.properties:
                dev_list.add(device.properties["NAME"].replace('"', ""))

        return dev_list

    @property
    def disk_devices(self) -> Set[str]:
        """Return all disk devices."""
        dev_list: Set[str] = set()
        for device in self.context.list_devices(subsystem="block"):
            if "ID_NAME" in device.properties:
                dev_list.add(device.device_node)

        return dev_list

    @property
    def support_audio(self) -> bool:
        """Return True if the system have audio support."""
        return bool(self.audio_devices)

    @property
    def audio_devices(self) -> Dict[str, Any]:
        """Return all available audio interfaces."""
        if not ASOUND_CARDS.exists():
            _LOGGER.info("No audio devices found")
            return {}

        try:
            cards = ASOUND_CARDS.read_text()
            devices = ASOUND_DEVICES.read_text()
        except OSError as err:
            _LOGGER.error("Can't read asound data: %s", err)
            return {}

        audio_list: Dict[str, Any] = {}

        # parse cards
        for match in RE_CARDS.finditer(cards):
            audio_list[match.group(1)] = {
                ATTR_NAME: match.group(3),
                ATTR_TYPE: match.group(2),
                ATTR_DEVICES: [],
            }

        # parse devices
        for match in RE_DEVICES.finditer(devices):
            try:
                audio_list[match.group(1)][ATTR_DEVICES].append(
                    {CHAN_ID: match.group(2), CHAN_TYPE: match.group(3)}
                )
            except KeyError:
                _LOGGER.warning("Wrong audio device found %s", match.group(0))
                continue

        return audio_list

    @property
    def support_gpio(self) -> bool:
        """Return True if device support GPIOs."""
        return SOC_DEVICES.exists() and GPIO_DEVICES.exists()

    @property
    def gpio_devices(self) -> Set[str]:
        """Return list of GPIO interface on device."""
        dev_list: Set[str] = set()
        for interface in GPIO_DEVICES.glob("gpio*"):
            dev_list.add(interface.name)

        return dev_list

    @property
    def last_boot(self) -> Optional[str]:
        """Return last boot time."""
        try:
            with PROC_STAT.open("r") as stat_file:
                stats: str = stat_file.read()
        except OSError as err:
            _LOGGER.error("Can't read stat data: %s", err)
            return None

        # parse stat file
        found: Optional[re.Match] = RE_BOOT_TIME.search(stats)
        if not found:
            _LOGGER.error("Can't found last boot time!")
            return None

        return datetime.utcfromtimestamp(int(found.group(1)))

    async def udev_trigger(self) -> None:
        """Trigger a udev reload."""
        proc = await asyncio.create_subprocess_shell("udevadm trigger && udevadm settle")

        await proc.wait()
        if proc.returncode == 0:
            return

        _LOGGER.warning("udevadm device triggering fails!")
        raise HardwareNotSupportedError()
