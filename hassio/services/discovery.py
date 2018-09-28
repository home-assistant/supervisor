"""Handle discover message for Home Assistant."""
import logging
from contextlib import suppress
from uuid import uuid4

import attrs
import voluptuous as vol
from voluptuous.humanize import humanize_error

from .validate import DISCOVERY_SERVICES
from ..coresys import CoreSysAttributes
from ..exceptions import DiscoveryError, HomeAssistantAPIError

_LOGGER = logging.getLogger(__name__)

CMD_NEW = 'post'
CMD_DEL = 'delete'


class Discovery(CoreSysAttributes):
    """Home Assistant Discovery handler."""

    def __init__(self, coresys):
        """Initialize discovery handler."""
        self.coresys = coresys
        self.message_obj = {}

    def load(self):
        """Load exists discovery message into storage."""
        messages = {}
        for message in self._data:
            discovery = Message(**message)
            messages[discovery.uuid] = discovery

        self.message_obj = messages

    def save(self):
        """Write discovery message into data file."""
        messages = []
        for message in self.message_obj.values():
            messages.append(attrs.asdict(message))

        self._data.clear()
        self._data.extend(messages)
        self.sys_services.data.save_data()

    def get(self, uuid):
        """Return discovery message."""
        return self.message_obj.get(uuid)

    @property
    def _data(self):
        """Return discovery data."""
        return self.sys_services.data.discovery

    @property
    def list_messages(self):
        """Return list of available discovery messages."""
        return self.message_obj.values()

    def send(self, provider, service, component, platform, config):
        """Send a discovery message to Home Assistant."""
        if service not in DISCOVERY_SERVICES:
            _LOGGER.error("Unknown service for discovery %s", service)
            raise DiscoveryError()

        # Check config
        try:
            DISCOVERY_SERVICES[service](config)
        except vol.Invalid as err:
            _LOGGER.error(
                "Invalid discovery %s config", humanize_error(config, err))
            raise DiscoveryError() from None

        # Create message
        message = Message(provider, component, platform, config)

        # Already exists?
        for old_message in self.message_obj:
            if old_message != message:
                continue
            _LOGGER.warning("Duplicate discovery message from %s", provider)
            return old_message

        _LOGGER.info("Send discovery to Home Assistant %s/%s from %s",
                     component, platform, provider)
        self.message_obj[message.uuid] = message
        self.save()

        self.sys_create_task(self._push_discovery(message.uuid, CMD_NEW))
        return message

    def remove(self, message):
        """Remove a discovery message from Home Assistant."""
        self.message_obj.pop(message.uuid, None)
        self.save()

        _LOGGER.info("Delete discovery to Home Assistant %s/%s from %s",
                     message.component, message.platform, message.provider)
        self.sys_create_task(self._push_discovery(message.uuid, CMD_DEL))

    async def _push_discovery(self, uuid, command):
        """Send a discovery request."""
        if not await self.sys_homeassistant.check_api_state():
            _LOGGER.info("Discovery %s mesage ignore", uuid)
            return

        with suppress(HomeAssistantAPIError):
            async with self.sys_homeassistant.make_request(
                    command, f"api/hassio_push/discovery/{uuid}") as req:
                _LOGGER.info("Discovery %s message send", uuid)
                return

        _LOGGER.warning("Discovery %s message fail", uuid)


@attr.s
class Message:
    """Represent a single Discovery message."""
    provider = attr.ib()
    component = attr.ib()
    platform = attr.ib()
    config = attr.ib()
    uuid = attr.ib(factory=uuid4().hex, cmp=False)
