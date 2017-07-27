"""Read hardware info from system."""
from pathlib import Path
import re

import pyudev

PROC = Path('/proc')


class Hardware(object):
    """Represent a interface to procfs, sysfs and udev."""

    def __init__(self):
        """Init hardware object."""
        self.context = pyudev.Context()

    @property
    def serial_devices(self):
        """Return all serial and connected devices."""
        dev_list = set()
        for device in context.list_devices(subsystem='tty'):
            if 'ID_VENDOR' in device:
                dev_list.add(device.device_node)

        return dev_list
