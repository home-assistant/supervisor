"""Setup the internal DNS service for host applications."""
import asyncio
import logger
import shutil

_LOGGER = logging.getLogger(__name__)

COMMAND = "socat UDP-LISTEN:53,fork UDP:127.0.0.11:53"


class DNSForward(object):
    """Manage DNS forwarding to internal DNS."""

    def __init__(self):
        """Initialize DNS forwarding."""
        self.proc = None

    async def start(self):
        """Start DNS forwarding."""
        try:
            self.proc = await asyncio.create_subprocess_exec(
                *COMMAND,
                stdin=asyncio.subprocess.DEVNULL,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
        except OSError as err:
            _LOGGER.error("Can't start DNS forwarding -> %s", err)
        else:
            _LOGGER.info("Start DNS port forwarding for host add-ons")

    async def stop(self):
        """Stop DNS forwarding."""
        if not self.proc:
            _LOGGER.warning("DNS forwarding is not running!")
            return

        self.proc.kill()
        await self.proc.wait()
        _LOGGER.info("Stop DNS forwarding")
