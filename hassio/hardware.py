"""Read hardware info from system."""
import logging
from pathlib import Path
import re

import pyudev

from .const import ATTR_NAME, ATTR_TYPE, ATTR_DEVICES

_LOGGER = logging.getLogger(__name__)

ASOUND_CARDS = Path("/proc/asound/cards")
RE_CARDS = re.compile(r"(\d+) \[(\w*) *\]: (.*\w)")

ASOUND_DEVICES = Path("/proc/asound/devices")
RE_DEVICES = re.compile(r"\[.*(\d+)- (\d+).*\]: ([\w ]*)")


class Hardware(object):
    """Represent a interface to procfs, sysfs and udev."""

    def __init__(self):
        """Init hardware object."""
        self.context = pyudev.Context()

    @property
    def serial_devices(self):
        """Return all serial and connected devices."""
        dev_list = set()
        for device in self.context.list_devices(subsystem='tty'):
            if 'ID_VENDOR' in device:
                dev_list.add(device.device_node)

        return list(dev_list)

    @property
    def input_devices(self):
        """Return all input devices."""
        dev_list = set()
        for device in self.context.list_devices(subsystem='input'):
            if 'NAME' in device:
                dev_list.add(device['NAME'])

        return list(dev_list)

    @property
    def disk_devices(self):
        """Return all disk devices."""
        dev_list = set()
        for device in self.context.list_devices(subsystem='block'):
            if 'ID_VENDOR' in device:
                dev_list.add(device.device_node)

        return list(dev_list)

    @property
    def audio_devices(self):
        """Return all available audio interfaces."""
        try:
            with ASOUND_CARDS.open('r') as cards_file:
                cards = cards_file.read()
            with ASOUND_DEVICES.open('r') as devices_file:
                devices = devices_file.read()
        except OSError as err:
            _LOGGER.error("Can't read asound data -> %s", err)
            return

        audio_list = {}

        # parse cards
        for match in RE_CARDS.finditer(cards):
            audio_list[match.group(1)] = {
                ATTR_NAME: match.group(3),
                ATTR_TYPE: match.group(2),
                ATTR_DEVICES: {},
            }

        # parse devices
        for match in RE_DEVICES(devices):
            try:
                audio_list[match.group(1)][ATTR_DEVICES][match.group(2)] = \
                    match.group(3)
            except KeyError:
                _LOGGER.warning("Wrong audio device found %s", match.group(0))
                continue

        return audio_list
