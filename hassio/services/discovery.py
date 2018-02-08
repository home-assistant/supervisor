"""Handle discover message for Home-Assistant."""
import logging
from uuid import uuid4

from ..const import ATTR_UUID
from ..coresys import CoreSysAttributes

_LOGGER = logging.getLogger(__name__)

EVENT_DISCOVERY_ADD = 'hassio_discovery_add'
EVENT_DISCOVERY_DEL = 'hassio_discovery_del'


class Discovery(CoreSysAttributes):
    """Home-Assistant Discovery handler."""

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
            messages.append(message.raw())

        self._data.clear()
        self._data.extend(messages)
        self._services.data.save_data()

    def get(self, uuid):
        """Return discovery message."""
        return self.message_obj.get(uuid)

    @property
    def _data(self):
        """Return discovery data."""
        return self._services.data.discovery

    @property
    def list_messages(self):
        """Return list of available discovery messages."""
        return self.message_obj

    def send(self, provider, component, platform=None, config=None):
        """Send a discovery message to Home-Assistant."""
        message = Message(provider, component, platform, config)

        # Allready exists?
        for exists_message in self.message_obj:
            if exists_message == message:
                _LOGGER.warning("Found douplicate discovery message from %s",
                                provider)
                return exists_message

        _LOGGER.info("Send discovery to Home-Assistant %s/%s from %s",
                     component, platform, provider)
        self.message_obj[message.uuid] = message
        self.save()

        # send event to Home-Assistant
        self._loop.create_task(self._homeassistant.send_event(
            EVENT_DISCOVERY_ADD, {ATTR_UUID: message.uuid}))

        return message

    def remove(self, message):
        """Remove a discovery message from Home-Assistant."""
        self.message_obj.pop(message.uuid, None)
        self.save()

        # send event to Home-Assistant
        self._loop.create_task(self._homeassistant.send_event(
            EVENT_DISCOVERY_DEL, {ATTR_UUID: message.uuid}))


class Message(object):
    """Represent a single Discovery message."""

    def __init__(self, provider, component, platform, config, uuid=None):
        """Initialize discovery message."""
        self.provider = provider
        self.component = component
        self.platform = platform
        self.config = config
        self.uuid = uuid or uuid4().hex

    def raw(self):
        """Return raw discovery message."""
        return self.__dict__

    def __eq__(self, other):
        """Compare with other message."""
        for attribute in ('provider', 'component', 'platform', 'config'):
            if getattr(self, attribute) != getattr(other, attribute):
                return False
        return True
