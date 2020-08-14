"""Handle discover message for Home Assistant."""
from __future__ import annotations

from contextlib import suppress
import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from uuid import UUID, uuid4

import attr
import voluptuous as vol
from voluptuous.humanize import humanize_error

from ..const import ATTR_CONFIG, ATTR_DISCOVERY, FILE_HASSIO_DISCOVERY
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import DiscoveryError, HomeAssistantAPIError
from ..utils.json import JsonConfig
from .validate import SCHEMA_DISCOVERY_CONFIG, valid_discovery_config

if TYPE_CHECKING:
    from ..addons.addon import Addon

_LOGGER: logging.Logger = logging.getLogger(__name__)

CMD_NEW = "post"
CMD_DEL = "delete"


@attr.s
class Message:
    """Represent a single Discovery message."""

    addon: str = attr.ib()
    service: str = attr.ib()
    config: Dict[str, Any] = attr.ib(eq=False)
    uuid: UUID = attr.ib(factory=lambda: uuid4().hex, eq=False)


class Discovery(CoreSysAttributes, JsonConfig):
    """Home Assistant Discovery handler."""

    def __init__(self, coresys: CoreSys):
        """Initialize discovery handler."""
        super().__init__(FILE_HASSIO_DISCOVERY, SCHEMA_DISCOVERY_CONFIG)
        self.coresys: CoreSys = coresys
        self.message_obj: Dict[str, Message] = {}

    async def load(self) -> None:
        """Load exists discovery message into storage."""
        messages = {}
        for message in self._data[ATTR_DISCOVERY]:
            discovery = Message(**message)
            messages[discovery.uuid] = discovery

        _LOGGER.info("Load %d messages", len(messages))
        self.message_obj = messages

    def save(self) -> None:
        """Write discovery message into data file."""
        messages: List[Dict[str, Any]] = []
        for message in self.list_messages:
            messages.append(attr.asdict(message))

        self._data[ATTR_DISCOVERY].clear()
        self._data[ATTR_DISCOVERY].extend(messages)
        self.save_data()

    def get(self, uuid: str) -> Optional[Message]:
        """Return discovery message."""
        return self.message_obj.get(uuid)

    @property
    def list_messages(self) -> List[Message]:
        """Return list of available discovery messages."""
        return list(self.message_obj.values())

    def send(self, addon: Addon, service: str, config: Dict[str, Any]) -> Message:
        """Send a discovery message to Home Assistant."""
        try:
            config = valid_discovery_config(service, config)
        except vol.Invalid as err:
            _LOGGER.error("Invalid discovery %s config", humanize_error(config, err))
            raise DiscoveryError()

        # Create message
        message = Message(addon.slug, service, config)

        # Already exists?
        for exists_msg in self.list_messages:
            if exists_msg != message:
                continue
            if exists_msg.config != config:
                message = exists_msg
                message.config = config
            else:
                _LOGGER.debug("Duplicate discovery message from %s", addon.slug)
                return exists_msg
            break

        _LOGGER.info("Send discovery to Home Assistant %s from %s", service, addon.slug)
        self.message_obj[message.uuid] = message
        self.save()

        self.sys_create_task(self._push_discovery(message, CMD_NEW))
        return message

    def remove(self, message: Message) -> None:
        """Remove a discovery message from Home Assistant."""
        self.message_obj.pop(message.uuid, None)
        self.save()

        _LOGGER.info(
            "Delete discovery to Home Assistant %s from %s",
            message.service,
            message.addon,
        )
        self.sys_create_task(self._push_discovery(message, CMD_DEL))

    async def _push_discovery(self, message: Message, command: str) -> None:
        """Send a discovery request."""
        if not await self.sys_homeassistant.check_api_state():
            _LOGGER.info("Discovery %s message ignore", message.uuid)
            return

        data = attr.asdict(message)
        data.pop(ATTR_CONFIG)

        with suppress(HomeAssistantAPIError):
            async with self.sys_homeassistant.make_request(
                command,
                f"api/hassio_push/discovery/{message.uuid}",
                json=data,
                timeout=10,
            ):
                _LOGGER.info("Discovery %s message send", message.uuid)
                return

        _LOGGER.warning("Discovery %s message fail", message.uuid)
