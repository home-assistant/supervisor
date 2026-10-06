"""Handle discover message for Home Assistant."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import logging
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from ..const import (
    ATTR_ADDON,
    ATTR_APP,
    ATTR_CONFIG,
    ATTR_DISCOVERY,
    FILE_HASSIO_DISCOVERY,
)
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import HomeAssistantAPIError
from ..utils.common import FileConfiguration
from .validate import SCHEMA_DISCOVERY_CONFIG

if TYPE_CHECKING:
    from ..apps.app import App

_LOGGER: logging.Logger = logging.getLogger(__name__)

CMD_NEW = "post"
CMD_DEL = "delete"


@dataclass(slots=True)
class Message:
    """Represent a single Discovery message."""

    app: str
    service: str
    config: dict[str, Any] = field(compare=False)
    uuid: str = field(default_factory=lambda: uuid4().hex, compare=False)


class Discovery(CoreSysAttributes, FileConfiguration):
    """Home Assistant Discovery handler."""

    def __init__(self, coresys: CoreSys):
        """Initialize discovery handler."""
        super().__init__(FILE_HASSIO_DISCOVERY, SCHEMA_DISCOVERY_CONFIG)
        self.coresys: CoreSys = coresys
        self.message_obj: dict[str, Message] = {}
        # Messages restored from a backup which Home Assistant was not told
        # about yet. Only the app knows when its service is actually up, so the
        # push waits for the app to send the message itself (see send()).
        self._unannounced: set[str] = set()

    async def load(self) -> None:
        """Load exists discovery message into storage."""
        messages = {}
        for message in self._data[ATTR_DISCOVERY]:
            discovery = Message(**message)
            messages[discovery.uuid] = discovery

        _LOGGER.info("Loaded %d messages", len(messages))
        self.message_obj = messages

    async def save(self) -> None:
        """Write discovery message into data file."""
        messages: list[dict[str, Any]] = []
        for message in self.list_messages:
            messages.append(asdict(message))

        self._data[ATTR_DISCOVERY].clear()
        self._data[ATTR_DISCOVERY].extend(messages)
        await self.save_data()

    def get(self, uuid: str) -> Message | None:
        """Return discovery message."""
        return self.message_obj.get(uuid)

    @property
    def list_messages(self) -> list[Message]:
        """Return list of available discovery messages."""
        return list(self.message_obj.values())

    def messages_for_app(self, slug: str) -> list[Message]:
        """Return list of discovery messages sent by an app."""
        return [message for message in self.list_messages if message.app == slug]

    async def send(self, app: App, service: str, config: dict[str, Any]) -> Message:
        """Send a discovery message to Home Assistant."""
        # Create message
        message = Message(app.slug, service, config)

        # Already exists?
        for exists_msg in self.list_messages:
            if exists_msg != message:
                continue
            if exists_msg.config != config:
                message = exists_msg
                message.config = config
            elif exists_msg.uuid in self._unannounced:
                # Restored from a backup, this is the first time the app
                # announces it, so Home Assistant still needs to hear about it
                message = exists_msg
            else:
                _LOGGER.debug("Duplicate discovery message from %s", app.slug)
                return exists_msg
            break

        _LOGGER.info(
            "Sending discovery to Home Assistant %s from %s", service, app.slug
        )
        self.message_obj[message.uuid] = message
        self._unannounced.discard(message.uuid)
        await self.save()

        self.sys_create_task(self._push_discovery(message, CMD_NEW))
        return message

    async def remove(self, message: Message) -> None:
        """Remove a discovery message from Home Assistant."""
        self.message_obj.pop(message.uuid, None)
        self._unannounced.discard(message.uuid)
        await self.save()

        _LOGGER.info(
            "Delete discovery to Home Assistant %s from %s",
            message.service,
            message.app,
        )
        self.sys_create_task(self._push_discovery(message, CMD_DEL))

    async def restore_app_messages(self, app: App, messages: list[Message]) -> None:
        """Restore discovery messages of an app from a backup.

        Home Assistant ties a config entry to the uuid of the discovery message
        it came from. The uuid identifies an installation of the app, it stays
        the same for as long as the data of the app does, and a restore brings
        that data back, so the uuid of the backup comes with it.

        A live message under the same uuid is the same installation, only its
        config is taken from the backup, as the restore may bring back another
        version of the app which announces a different config. A live message
        under another uuid belongs to an installation which the restore just
        replaced. It is retracted as an uninstall would, so that Home Assistant
        drops its config entry, and the message of the backup takes its place.

        A restored message is not pushed to Home Assistant here. The service
        behind it is not up at this point, and it may never come up if the app
        is not started again. Instead it is marked as unannounced so that the
        push happens once the app sends the message itself.
        """
        live = {message.service: message for message in self.messages_for_app(app.slug)}
        # Services restored so far, a backup listing a service twice keeps the first
        seen: set[str] = set()
        restored = False

        for message in messages:
            if message.service in seen:
                continue
            if message.service not in app.discovery:
                _LOGGER.info(
                    "Skipping discovery message for service %s, app %s does not provide it anymore",
                    message.service,
                    app.slug,
                )
                continue

            if (live_msg := live.get(message.service)) is not None:
                if live_msg.uuid == message.uuid:
                    seen.add(message.service)
                    if live_msg.config == message.config:
                        continue
                    live_msg.config = message.config
                    self._unannounced.add(live_msg.uuid)
                    restored = True
                    _LOGGER.info(
                        "Restored config of discovery %s for service %s from %s",
                        live_msg.uuid,
                        message.service,
                        app.slug,
                    )
                    continue

                _LOGGER.info(
                    "Retracting discovery %s for service %s from %s, the restore replaces it with %s",
                    live_msg.uuid,
                    message.service,
                    app.slug,
                    message.uuid,
                )
                await self.remove(live_msg)

            if message.uuid in self.message_obj:
                # Messages are keyed by uuid across all apps, so restoring this
                # one would drop the message it collides with
                _LOGGER.warning(
                    "Skipping discovery message for service %s of app %s, uuid %s is already in use",
                    message.service,
                    app.slug,
                    message.uuid,
                )
                continue

            self.message_obj[message.uuid] = message
            self._unannounced.add(message.uuid)
            seen.add(message.service)
            restored = True
            _LOGGER.info(
                "Restored discovery %s for service %s from %s",
                message.uuid,
                message.service,
                app.slug,
            )

        if restored:
            await self.save()

    async def _push_discovery(self, message: Message, command: str) -> None:
        """Send a discovery request."""
        if not await self.sys_homeassistant.api.check_api_state():
            _LOGGER.info("Discovery %s message ignore", message.uuid)
            return

        data = asdict(message)
        data.pop(ATTR_CONFIG)
        # Home Assistant expects the legacy "addon" key in the push payload.
        data[ATTR_ADDON] = data.pop(ATTR_APP)

        try:
            async with self.sys_homeassistant.api.make_request(
                command,
                f"api/hassio_push/discovery/{message.uuid}",
                json=data,
                timeout=10,
            ):
                _LOGGER.info("Discovery %s message send", message.uuid)
                return
        except HomeAssistantAPIError as err:
            _LOGGER.error("Discovery %s message failed: %s", message.uuid, err)
