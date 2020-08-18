"""Read hardware info from system."""
import asyncio
from datetime import datetime
import logging
from pathlib import Path
import re
import shutil
from typing import Any, Dict, List, Optional, Set, Union

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


@attr.s(slots=True, frozen=True)
class Device:
    """Represent a device."""

    name: str = attr.ib()
    path: Path = attr.ib()
    subsystem: str = attr.ib()
    links: List[Path] = attr.ib()
    attributes: Dict[str, str] = attr.ib()


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
                    device.subsystem,
                    [Path(node) for node in device.device_links],
                    {attr: device.properties[attr] for attr in device.properties},
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
    def serial_devices(self) -> List[Device]:
        """Return all serial and connected devices."""
        dev_list: List[Device] = []
        for device in self.devices:
            if device.subsystem != "tty" or (
                "ID_VENDOR" not in device.attributes
                and not RE_TTY.search(str(device.path))
            ):
                continue

            # Cleanup not usable device links
            for link in device.links.copy():
                if link.match("/dev/serial/by-id/*"):
                    continue
                device.links.remove(link)

            dev_list.append(device)

        return dev_list

    @property
    def usb_devices(self) -> List[Device]:
        """Return all usb and connected devices."""
        return [device for device in self.devices if device.subsystem == "usb"]

    @property
    def input_devices(self) -> Set[str]:
        """Return all input devices."""
        dev_list: Set[str] = set()
        for device in self.context.list_devices(subsystem="input"):
            if "NAME" in device.properties:
                dev_list.add(device.properties["NAME"].replace('"', ""))

        return dev_list

    @property
    def disk_devices(self) -> List[Device]:
        """Return all disk devices."""
        dev_list: List[Device] = []
        for device in self.devices:
            if device.subsystem != "block" or "ID_NAME" not in device.attributes:
                continue
            dev_list.append(device)

        return dev_list

    @property
    def support_audio(self) -> bool:
        """Return True if the system have audio support."""
        return bool(self.audio_devices)

    @property
    def audio_devices(self) -> Dict[str, Any]:
        """Return all available audio interfaces."""
        if not ASOUND_CARDS.exists():
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

    def get_disk_total_space(self, path: Union[str, Path]) -> float:
        """Return total space (GiB) on disk for path."""
        total, _, _ = shutil.disk_usage(path)
        return round(total / (1024.0 ** 3), 1)

    def get_disk_used_space(self, path: Union[str, Path]) -> float:
        """Return used space (GiB) on disk for path."""
        _, used, _ = shutil.disk_usage(path)
        return round(used / (1024.0 ** 3), 1)

    def get_disk_free_space(self, path: Union[str, Path]) -> float:
        """Return free space (GiB) on disk for path."""
        _, _, free = shutil.disk_usage(path)
        return round(free / (1024.0 ** 3), 1)

    async def udev_trigger(self) -> None:
        """Trigger a udev reload."""
        proc = await asyncio.create_subprocess_shell(
            "udevadm trigger && udevadm settle"
        )

        await proc.wait()
        if proc.returncode == 0:
            return

        _LOGGER.warning("udevadm device triggering fails!")
        raise HardwareNotSupportedError()
