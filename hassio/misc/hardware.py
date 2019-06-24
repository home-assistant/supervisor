"""Read hardware info from system."""
from datetime import datetime
import logging
from pathlib import Path
import re

import pyudev

from ..const import ATTR_NAME, ATTR_TYPE, ATTR_DEVICES, CHAN_ID, CHAN_TYPE

_LOGGER = logging.getLogger(__name__)

ASOUND_CARDS = Path("/proc/asound/cards")
RE_CARDS = re.compile(r"(\d+) \[(\w*) *\]: (.*\w)")

ASOUND_DEVICES = Path("/proc/asound/devices")
RE_DEVICES = re.compile(r"\[.*(\d+)- (\d+).*\]: ([\w ]*)")

PROC_STAT = Path("/proc/stat")
RE_BOOT_TIME = re.compile(r"btime (\d+)")

GPIO_DEVICES = Path("/sys/class/gpio")
SOC_DEVICES = Path("/sys/devices/platform/soc")
RE_TTY = re.compile(r"tty[A-Z]+")


class Hardware:
    """Representation of an interface to procfs, sysfs and udev."""

    def __init__(self):
        """Init hardware object."""
        self.context = pyudev.Context()

    @property
    def serial_devices(self):
        """Return all serial and connected devices."""
        dev_list = set()
        for device in self.context.list_devices(subsystem="tty"):
            if "ID_VENDOR" in device or RE_TTY.search(device.device_node):
                dev_list.add(device.device_node)

                # Add /dev/serial/by-id devlink for current device
                if "DEVLINKS" in device and device["DEVLINKS"]:
                    devlinks = [
                        symlink
                        for symlink in device["DEVLINKS"].split(" ")
                        if symlink.startswith("/dev/serial/by-id")
                    ]
                    dev_list.update(devlinks)

        return dev_list

    @property
    def input_devices(self):
        """Return all input devices."""
        dev_list = set()
        for device in self.context.list_devices(subsystem="input"):
            if "NAME" in device:
                dev_list.add(device["NAME"].replace('"', ""))

        return dev_list

    @property
    def disk_devices(self):
        """Return all disk devices."""
        dev_list = set()
        for device in self.context.list_devices(subsystem="block"):
            if device.device_node.startswith("/dev/sd"):
                dev_list.add(device.device_node)

        return dev_list

    @property
    def support_audio(self):
        """Return True if the system have audio support."""
        return bool(self.audio_devices)

    @property
    def audio_devices(self):
        """Return all available audio interfaces."""
        if not ASOUND_CARDS.exists():
            _LOGGER.debug("No audio devices found")
            return {}

        try:
            cards = ASOUND_CARDS.read_text()
            devices = ASOUND_DEVICES.read_text()
        except OSError as err:
            _LOGGER.error("Can't read asound data: %s", err)
            return {}

        audio_list = {}

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
    def support_gpio(self):
        """Return True if device support GPIOs."""
        return SOC_DEVICES.exists() and GPIO_DEVICES.exists()

    @property
    def gpio_devices(self):
        """Return list of GPIO interface on device."""
        dev_list = set()
        for interface in GPIO_DEVICES.glob("gpio*"):
            dev_list.add(interface.name)

        return dev_list

    @property
    def last_boot(self):
        """Return last boot time."""
        try:
            with PROC_STAT.open("r") as stat_file:
                stats = stat_file.read()
        except OSError as err:
            _LOGGER.error("Can't read stat data: %s", err)
            return None

        # parse stat file
        found = RE_BOOT_TIME.search(stats)
        if not found:
            _LOGGER.error("Can't found last boot time!")
            return None

        return datetime.utcfromtimestamp(int(found.group(1)))
