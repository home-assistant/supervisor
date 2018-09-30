"""Handle discover message for Home Assistant."""
import logging
from contextlib import suppress
from uuid import uuid4

import attr
import voluptuous as vol
from voluptuous.humanize import humanize_error

from .const import FILE_HASSIO_DISCOVERY, ATTR_CONFIG, ATTR_DISCOVERY
from .coresys import CoreSysAttributes
from .exceptions import DiscoveryError, HomeAssistantAPIError
from .validate import SCHEMA_DISCOVERY_CONFIG
from .utils.json import JsonConfig
from .services.validate import DISCOVERY_SERVICES

_LOGGER = logging.getLogger(__name__)

CMD_NEW = 'post'
CMD_DEL = 'delete'


class Discovery(CoreSysAttributes, JsonConfig):
    """Home Assistant Discovery handler."""

    def __init__(self, coresys):
        """Initialize discovery handler."""
        super().__init__(FILE_HASSIO_DISCOVERY, SCHEMA_DISCOVERY_CONFIG)
        self.coresys = coresys
        self.message_obj = {}

    async def load(self):
        """Load exists discovery message into storage."""
        messages = {}
        for message in self._data[ATTR_DISCOVERY]:
            discovery = Message(**message)
            messages[discovery.uuid] = discovery

        self.message_obj = messages

    def save(self):
        """Write discovery message into data file."""
        messages = []
        for message in self.message_obj.values():
            messages.append(attr.asdict(message))

        self._data[ATTR_DISCOVERY].clear()
        self._data[ATTR_DISCOVERY].extend(messages)
        self.save_data()

    def get(self, uuid):
        """Return discovery message."""
        return self.message_obj.get(uuid)

    @property
    def list_messages(self):
        """Return list of available discovery messages."""
        return self.message_obj.values()

    def send(self, addon, service, component, platform, config):
        """Send a discovery message to Home Assistant."""
        try:
            DISCOVERY_SERVICES[service](config)
        except vol.Invalid as err:
            _LOGGER.error(
                "Invalid discovery %s config", humanize_error(config, err))
            raise DiscoveryError() from None

        # Create message
        message = Message(addon.slug, service, component, platform, config)

        # Already exists?
        for old_message in self.list_messages:
            if old_message != message:
                continue
            _LOGGER.warning("Duplicate discovery message from %s", addon.slug)
            return old_message

        _LOGGER.info("Send discovery to Home Assistant %s/%s from %s",
                     component, platform, addon.slug)
        self.message_obj[message.uuid] = message
        self.save()

        self.sys_create_task(self._push_discovery(message, CMD_NEW))
        return message

    def remove(self, message):
        """Remove a discovery message from Home Assistant."""
        self.message_obj.pop(message.uuid, None)
        self.save()

        _LOGGER.info("Delete discovery to Home Assistant %s/%s from %s",
                     message.component, message.platform, message.addon)
        self.sys_create_task(self._push_discovery(message, CMD_DEL))

    async def _push_discovery(self, message, command):
        """Send a discovery request."""
        if not await self.sys_homeassistant.check_api_state():
            _LOGGER.info("Discovery %s mesage ignore", message.uuid)
            return

        data = attr.asdict(message)
        data.pop(ATTR_CONFIG)

        with suppress(HomeAssistantAPIError):
            async with self.sys_homeassistant.make_request(
                    command, f"api/hassio_push/discovery/{message.uuid}",
                    json=data, timeout=10):
                _LOGGER.info("Discovery %s message send", message.uuid)
                return

        _LOGGER.warning("Discovery %s message fail", message.uuid)


@attr.s
class Message:
    """Represent a single Discovery message."""
    addon = attr.ib()
    service = attr.ib()
    component = attr.ib()
    platform = attr.ib()
    config = attr.ib(cmp=False)
    uuid = attr.ib(factory=lambda: uuid4().hex, cmp=False)
