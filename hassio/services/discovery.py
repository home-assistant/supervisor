"""Handle discover message for Home-Assistant."""
import logging

from ..coresys import CoreSysAttributes


EVENT_DISCOVERY = 'hassio_discovery'


class Discovery(CoreSysAttributes):
    """Home-Assistant Discovery handler."""

    def __init__(self, coresys):
        """Initialize discovery handler."""
        self.coresys = coresys
        self.message_obj = []

    def load(self):
        """Load exists discovery message into storage."""
        messages = []
        for message in self._data:
            messages.append(Message(**message))

        self.message_obj = messages

    def save(self):
        """Write discovery message into data file."""
        messages = []
        for message in self.message_obj:
            messages.append(message.raw())

        self._data = messages
        self._services.data.save_data()

    @property
    def _data(self):
        """Return discovery data."""
        return self._services.data.discovery

    @property
    def list_messages(self):
        """Return list of available discovery messages."""
        return self.message_obj

    async def send_discovery(self, provider, component,
                             platform=None, config=None)
        """Send a discovery message to Home-Assistant."""
        message = Message(provider, component, platform, config)

        # Allready exists?
        for exists_message in self.message_obj:
            if exists_message == message:
                return True
        self.message_obj.append(message)

        # send event to Home-Assistant
        sending = await self._homeassistant.send_event(EVENT_DISCOVERY, {
            ATTR_COMPONENT: component,
            ATTR_PLATFORM: platform,
        })

        if not sending:
            return False
        return True


class Message(obect):
    """Represent a single Discovery message."""

    def __init__(self, provider, component, platform, config):
        """Initialize discovery message."""
        self.provider = provider
        self.component = component
        self.platform = platform
        self.config = config

    def raw(self):
        """Return raw discovery message."""
        return self.__dict__

    def __eq__(self, other):
        """Compare with other message."""
        for attribute in (provider, component, platform, config):
            if getattr(self, attribute) != getattr(other, attribute):
                return False
        return True
