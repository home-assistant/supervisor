"""Pulse host control."""
from datetime import timedelta
from enum import Enum
import logging
from typing import List

import attr
from pulsectl import Pulse, PulseError, PulseIndexError, PulseOperationFailed

from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import PulseAudioError
from ..utils import AsyncThrottle

_LOGGER: logging.Logger = logging.getLogger(__name__)

PULSE_NAME = "supervisor"


class SourceType(str, Enum):
    """INPUT/OUTPUT type of source."""

    INPUT = "input"
    OUTPUT = "output"


@attr.s(frozen=True)
class AudioStream:
    """Represent a input/output profile."""

    name: str = attr.ib()
    description: str = attr.ib()
    volume: float = attr.ib()
    default: bool = attr.ib()


@attr.s(frozen=True)
class SoundProfile:
    """Represent a Sound Card profile."""

    name: str = attr.ib()
    description: str = attr.ib()
    active: bool = attr.ib()


@attr.s(frozen=True)
class SoundCard:
    """Represent a Sound Card."""

    name: str = attr.ib()
    driver: str = attr.ib()
    profiles: List[SoundProfile] = attr.ib()


class SoundControl(CoreSysAttributes):
    """Pulse control from Host."""

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize PulseAudio sound control."""
        self.coresys: CoreSys = coresys
        self._cards: List[SoundCard] = []
        self._inputs: List[AudioStream] = []
        self._outputs: List[AudioStream] = []

    @property
    def cards(self) -> List[SoundCard]:
        """Return a list of available sound cards and profiles."""
        return self._cards

    @property
    def inputs(self) -> List[AudioStream]:
        """Return a list of available input streams."""
        return self._inputs

    @property
    def outputs(self) -> List[AudioStream]:
        """Return a list of available output streams."""
        return self._outputs

    async def set_default(self, source: SourceType, name: str) -> None:
        """Set a stream to default input/output."""

        def _set_default():
            try:
                with Pulse(PULSE_NAME) as pulse:
                    if source == SourceType.OUTPUT:
                        # Get source and set it as default
                        source = pulse.get_source_by_name(name)
                        pulse.source_default_set(source)
                    else:
                        # Get sink and set it as default
                        sink = pulse.get_sink_by_name(name)
                        pulse.sink_default_set(sink)
            except PulseIndexError:
                _LOGGER.error("Can't find %s profile %s", source, name)
                raise PulseAudioError() from None
            except PulseError as err:
                _LOGGER.error("Can't set %s as default: %s", name, err)
                raise PulseAudioError() from None

        # Run and Reload data
        await self.sys_run_in_executor(_set_default)
        await self.update()

    async def set_volume(self, source: SourceType, name: str, volume: float) -> None:
        """Set a stream to volume input/output."""

        def _set_volume():
            try:
                with Pulse(PULSE_NAME) as pulse:
                    if source == SourceType.OUTPUT:
                        # Get source and set it as default
                        source = pulse.get_source_by_name(name)
                    else:
                        # Get sink and set it as default
                        source = pulse.get_sink_by_name(name)

                    pulse.volume_set_all_chans(source, volume)
            except PulseIndexError:
                _LOGGER.error("Can't find %s profile %s", source, name)
                raise PulseAudioError() from None
            except PulseError as err:
                _LOGGER.error("Can't set %s volume: %s", name, err)
                raise PulseAudioError() from None

        # Run and Reload data
        await self.sys_run_in_executor(_set_volume)
        await self.update()

    async def ativate_profile(self, card_name: str, profile_name: str) -> None:
        """Set a profile to volume input/output."""

        def _activate_profile():
            try:
                with Pulse(PULSE_NAME) as pulse:
                    card = pulse.get_sink_by_name(card_name)
                    pulse.card_profile_set(card, profile_name)

            except PulseIndexError:
                _LOGGER.error("Can't find %s profile %s", card_name, profile_name)
                raise PulseAudioError() from None
            except PulseError as err:
                _LOGGER.error(
                    "Can't activate %s profile %s: %s", card_name, profile_name, err
                )
                raise PulseAudioError() from None

        # Run and Reload data
        await self.sys_run_in_executor(_activate_profile)
        await self.update()

    @AsyncThrottle(timedelta(seconds=10))
    async def update(self):
        """Update properties over dbus."""
        _LOGGER.info("Update PulseAudio information")

        def _update():
            try:
                with Pulse(PULSE_NAME) as pulse:
                    server = pulse.server_info()

                    # Update output
                    self._outputs.clear()
                    for sink in pulse.sink_list():
                        self._outputs.append(
                            AudioStream(
                                sink.name,
                                sink.description,
                                sink.volume.value_flat,
                                sink.name == server.default_sink_name,
                            )
                        )

                    # Update input
                    self._inputs.clear()
                    for source in pulse.source_list():
                        # Filter monitor devices out because we did not use it now
                        if source.name.endswith(".monitor"):
                            continue
                        self._inputs.append(
                            AudioStream(
                                source.name,
                                source.description,
                                source.volume.value_flat,
                                source.name == server.default_source_name,
                            )
                        )

                    # Update Sound Card
                    self._cards.clear()
                    for card in pulse.card_list():
                        sound_profiles: List[SoundProfile] = []

                        # Generate profiles
                        for profile in card.profile_list:
                            if not profile.available:
                                continue
                            sound_profiles.append(
                                SoundProfile(
                                    profile.name,
                                    profile.description,
                                    profile.name == card.profile_active.name,
                                )
                            )

                        self._cards.append(
                            SoundCard(card.name, card.driver, sound_profiles)
                        )

            except PulseOperationFailed as err:
                _LOGGER.error("Error while processing pulse update: %s", err)
                raise PulseAudioError() from None
            except PulseError as err:
                _LOGGER.debug("Can't update PulseAudio data: %s", err)

        # Run update from pulse server
        await self.sys_run_in_executor(_update)
