"""Tools file for HassIO."""
import asyncio
import logging

import aiohttp
import async_timeout

from .const import URL_SUPERVISOR_VERSION


async def fetch_current_versions(websession):
    """Fetch current versions from github."""
    try:
        with async_timeout.timeout(10, loop=websession.loop):
            async with websession.get(URL_SUPERVISOR_VERSION) as request:
                return (await request.json())

    except Exception:  # pylint: disable=broad-except
        return None
