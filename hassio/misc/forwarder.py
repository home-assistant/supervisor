"""Setup the internal DNS service for host applications."""
import asyncio
import logging
import shlex
from typing import Optional

import async_timeout

_LOGGER = logging.getLogger(__name__)

COMMAND = "socat UDP-RECVFROM:53,fork UDP-SENDTO:{}"


class DNSForward:
    """Manage DNS forwarding to internal DNS."""

    def __init__(self):
        """Initialize DNS forwarding."""
        self.proc: Optional[asyncio.Process] = None

    async def start(self, dns_server: str) -> None:
        """Start DNS forwarding."""
        try:
            self.proc = await asyncio.create_subprocess_exec(
                *shlex.split(COMMAND.format(dns_server)),
                stdin=asyncio.subprocess.DEVNULL,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
        except OSError as err:
            _LOGGER.error("Can't start DNS forwarding: %s", err)
        else:
            _LOGGER.info("Start DNS port forwarding for host add-ons")

    async def stop(self) -> None:
        """Stop DNS forwarding."""
        if not self.proc:
            _LOGGER.warning("DNS forwarding is not running!")
            return

        self.proc.kill()
        try:
            with async_timeout.timeout(5):
                await self.proc.wait()
        except asyncio.TimeoutError:
            _LOGGER.warning("Stop waiting for DNS shutdown")

        _LOGGER.info("Stop DNS forwarding")
