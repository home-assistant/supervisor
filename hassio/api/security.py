"""Handle security part of this API."""
import logging

from aiohttp.web import middleware

from ..const import HEADER_TOKEN, REQUEST_FROM

_LOGGER = logging.getLogger(__name__)


@middleware
async def security_layer(request, handler):
    """Check security access of this layer."""
    coresys = request.app['coresys']
    hassio_token = request.headers.get(HEADER_TOKEN)

    # Need to be removed later
    if not hassio_token:
        _LOGGER.warning("No valid hassio token for API access!")
        request[REQUEST_FROM] = 'UNKNOWN'

    # From Home-Assistant
    elif hassio_token == coresys.homeassistant.uuid:
        request[REQUEST_FROM] = 'homeassistant'

    # From Add-on
    else:
        for addon in coresys.addons.list_addons:
            if hassio_token != addon.uuid:
                continue
            request[REQUEST_FROM] = addon.slug
            break

    return await handler(request)
