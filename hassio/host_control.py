"""Host control for HassIO."""
import asyncio
import json
import logging

import async_timeout

from .const import (
    SOCKET_HC, ATTR_LAST_VERSION, ATTR_VERSION, ATTR_TYPE, ATTR_FEATURES,
    ATTR_HOSTNAME, ATTR_OS)

_LOGGER = logging.getLogger(__name__)

TIMEOUT = 15
UNKNOWN = 'unknown'

FEATURES_SHUTDOWN = 'shutdown'
FEATURES_REBOOT = 'reboot'
FEATURES_UPDATE = 'update'
FEATURES_NETWORK_INFO = 'network_info'
FEATURES_NETWORK_CONTROL = 'network_control'


class HostControl(object):
    """Client for host control."""

    def __init__(self, loop):
        """Initialize HostControl socket client."""
        self.loop = loop
        self.active = False
        self.version = UNKNOWN
        self.last_version = UNKNOWN
        self.type = UNKNOWN
        self.features = []
        self.hostname = UNKNOWN
        self.os_info = UNKNOWN

        if SOCKET_HC.is_socket():
            self.active = True

    async def _send_command(self, command):
        """Send command to host.

        Is a coroutine.
        """
        if not self.active:
            return

        reader, writer = await asyncio.open_unix_connection(
            str(SOCKET_HC), loop=self.loop)

        try:
            # send
            _LOGGER.info("Send '%s' to HostControl.", command)

            with async_timeout.timeout(TIMEOUT, loop=self.loop):
                writer.write("{}\n".format(command).encode())
                data = await reader.readline()

            response = data.decode().rstrip()
            _LOGGER.info("Receive from HostControl: %s.", response)

            if response == "OK":
                return True
            elif response == "ERROR":
                return False
            elif response == "WRONG":
                return None
            else:
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    _LOGGER.warning("Json parse error from HostControl '%s'.",
                                    response)

        except asyncio.TimeoutError:
            _LOGGER.error("Timeout from HostControl!")

        finally:
            writer.close()

    async def load(self):
        """Load Info from host.

        Return a coroutine.
        """
        info = await self._send_command("info")
        if not info:
            return

        self.version = info.get(ATTR_VERSION, UNKNOWN)
        self.last_version = info.get(ATTR_LAST_VERSION, UNKNOWN)
        self.type = info.get(ATTR_TYPE, UNKNOWN)
        self.features = info.get(ATTR_FEATURES, [])
        self.hostname = info.get(ATTR_HOSTNAME, UNKNOWN)
        self.os_info = info.get(ATTR_OS, UNKNOWN)

    def reboot(self):
        """Reboot the host system.

        Return a coroutine.
        """
        return self._send_command("reboot")

    def shutdown(self):
        """Shutdown the host system.

        Return a coroutine.
        """
        return self._send_command("shutdown")

    def update(self, version=None):
        """Update the host system.

        Return a coroutine.
        """
        if version:
            return self._send_command("update {}".format(version))
        return self._send_command("update")
