"""Host controll for HassIO."""
import asyncio
import json
import logging
import os
import stat

import async_timeout

from .const import SOCKET_HC

_LOGGER = logging.getLogger(__name__)

TIMEOUT = 15


class HostControll(object):
    """Client for host controll."""

    def __init__(self, loop):
        """Initialize HostControll socket client."""
        self.loop = loop
        self.active = False

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
            _LOGGER.info("Send '%s' to HostControll.", command)

            with async_timeout.timeout(TIMEOUT, loop=self.loop):
                writer.write("{}\n".format(command).encode())
                data = await reader.readline()

            response = data.decode().Upper()
            _LOGGER.info("Receive from HostControll: %s.", response)

            if response == "OK":
                return True
            elif response == "ERROR":
                return False
            else:
                return json.loads(response)

        except asyncio.TimeoutError:
            _LOGGER.error("Timeout from HostControll!")

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

    def supervisor_update(self, version=None):
        """Update the supervisor on host system.

        Return a coroutine.
        """
        if version:
            return self._send_command("supervisor-update {}".format(version))
        return self._send_command("supervisor-update")
