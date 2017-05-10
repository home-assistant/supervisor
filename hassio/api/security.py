"""Init file for HassIO security rest api."""
from datetime import datetime, timedelta
import io
import logging
import hashlib
import os

from aiohttp import web
import voluptuous as vol
import pyotp
import pyqrcode

from .util import api_process, api_validate, hash_password
from ..const import ATTR_INITIALIZE, ATTR_PASSWORD, ATTR_TOTP, ATTR_SESSION

_LOGGER = logging.getLogger(__name__)

SCHEMA_PASSWORD = vol.Schema({
    vol.Required(ATTR_PASSWORD): vol.Coerce(str),
})

SCHEMA_SESSION = SCHEMA_PASSWORD.extend({
    vol.Optional(ATTR_TOTP, default=None): vol.Coerce(str),
})


class APISecurity(object):
    """Handle rest api for security functions."""

    def __init__(self, config, loop):
        """Initialize security rest api part."""
        self.config = config
        self.loop = loop

    def _check_password(self, body):
        """Check if password is valid and security is initialize."""
        if not self.config.security_initialize:
            raise RuntimeError("First set a password")

        password = hash_password(body[ATTR_PASSWORD])
        if password != self.config.security_password:
            raise RuntimeError("Wrong password")

    @api_process
    async def info(self, request):
        """Return host information."""
        return {
            ATTR_INITIALIZE: self.config.security_initialize,
            ATTR_TOTP: self.config.security_totp is not None,
        }

    @api_process
    async def options(self, request):
        """Set options / password."""
        body = await api_validate(SCHEMA_PASSWORD, request)

        if self.config.security_initialize:
            raise RuntimeError("Password is already set!")

        self.config.security_password = hash_password(body[ATTR_PASSWORD])
        self.config.security_initialize = True
        return True

    @api_process
    async def totp(self, request):
        """Set and initialze TOTP."""
        body = await api_validate(SCHEMA_PASSWORD, request)
        self._check_password(body)

        # generate TOTP
        totp_init_key = pyotp.random_base32()
        totp = pyotp.TOTP(totp_init_key)

        # init qrcode
        buff = io.BytesIO()

        qrcode = pyqrcode.create(totp.provisioning_uri("Hass.IO"))
        qrcode.svg(buff)

        # finish
        self.config.security_totp = totp_init_key
        return web.Response(body=buff.getvalue(), content_type='image/svg+xml')

    @api_process
    async def session(self, request):
        """Set and initialze session."""
        body = await api_validate(SCHEMA_SESSION, request)
        self._check_password(body)

        # check TOTP
        if self.config.security_totp:
            totp = pyotp.TOTP(self.config.security_totp)
            if body[ATTR_TOTP] != totp.now():
                raise RuntimeError("Invalid TOTP token!")

        # create session
        valid_until = datetime.now() + timedelta(days=1)
        session = hashlib.sha256(os.urandom(54)).hexdigest()

        # store session
        self.config.security_sessions = (session, valid_until)
        return {ATTR_SESSION: session}
