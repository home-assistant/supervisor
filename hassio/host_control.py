"""Host control for HassIO."""
import asyncio
import json
import logging
import os
import stat

import async_timeout

from .const import SOCKET_HC

_LOGGER = logging.getLogger(__name__)

TIMEOUT = 15

LEVEL_POWER = 1
LEVEL_UPDATE_HOST = 2
LEVEL_NETWORK = 4


class HostControl(object):
    """Client for host control."""

    def __init__(self, loop):
        """Initialize HostControl socket client."""
        self.loop = loop
        self.active = False
        self.version = None

        mode = os.stat(SOCKET_HC)[stat.ST_MODE]
        if stat.S_ISSOCK(mode):
            self.active = True

    async def _send_command(self, command):
        """Send command to host.

        Is a coroutine.
        """
        if not self.active:
            return

        reader, writer = await asyncio.open_unix_connection(
            SOCKET_HC, loop=self.loop)

        try:
            # send
            _LOGGER.info("Send '%s' to HostControl.", command)

            with async_timeout.timeout(TIMEOUT, loop=self.loop):
                writer.write("{}\n".format(command).encode())
                data = await reader.readline()

            response = data.decode()
            _LOGGER.debug("Receive from HostControl: %s.", response)

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
                    _LOGGER.warning("Json parse error from HostControl.")

        except asyncio.TimeoutError:
            _LOGGER.error("Timeout from HostControl!")

        finally:
            writer.close()

    def info(self):
        """Return Info from host.

        Return a coroutine.
        """
        return self._send_command("info")

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

    def host_update(self, version=None):
        """Update the host system.

        Return a coroutine.
        """
        if version:
            return self._send_command("host-update {}".format(version))
        return self._send_command("host-update")
