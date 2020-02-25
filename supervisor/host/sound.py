"""Pulse host control."""
from enum import Enum
import logging
from typing import List

import attr
from pulsectl import Pulse, PulseError

from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import PulseAudioError

_LOGGER: logging.Logger = logging.getLogger(__name__)

PULSE_NAME = "supervisor"


class SourceType(str, Enum):
    """INPUT/OUTPUT type of source."""

    INPUT = "input"
    OUTPUT = "output"


@attr.s(frozen=True)
class AudioProfile:
    """Represent a input/output profile."""

    name: str = attr.ib()
    description: str = attr.ib()
    volume: float = attr.ib()
    default: bool = attr.ib()


class SoundControl(CoreSysAttributes):
    """Pulse control from Host."""

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize PulseAudio sound control."""
        self.coresys: CoreSys = coresys
        self._input: List[AudioProfile] = []
        self._output: List[AudioProfile] = []

    @property
    def input_profiles(self) -> List[AudioProfile]:
        """Return a list of available input profiles."""
        return self._input

    @property
    def output_profiles(self) -> List[AudioProfile]:
        """Return a list of available output profiles."""
        return self._output

    async def set_default(self, source: SourceType, name: str) -> None:
        """Set a profile to default input/output."""
        try:
            with Pulse(PULSE_NAME) as pulse:
                if source == SourceType.INPUT:
                    # Get source and set it as default
                    source = pulse.get_source_by_name(name)
                    pulse.source_default_set(source)
                else:
                    # Get sink and set it as default
                    sink = pulse.get_sink_by_name(name)
                    pulse.sink_default_set(sink)
        except PulseError as err:
            _LOGGER.error("Can't set %s as default: %s", name, err)
            raise PulseAudioError() from None

        # Reload data
        await self.update()

    async def set_volume(self, source: SourceType, name: str, volume: float) -> None:
        """Set a profile to volume input/output."""
        try:
            with Pulse(PULSE_NAME) as pulse:
                if source == SourceType.INPUT:
                    # Get source and set it as default
                    source = pulse.get_source_by_name(name)
                else:
                    # Get sink and set it as default
                    source = pulse.get_sink_by_name(name)

                pulse.volume_set_all_chans(source, volume)
        except PulseError as err:
            _LOGGER.error("Can't set %s volume: %s", name, err)
            raise PulseAudioError() from None

        # Reload data
        await self.update()

    async def update(self):
        """Update properties over dbus."""
        _LOGGER.info("Update PulseAudio information")
        try:
            with Pulse(PULSE_NAME) as pulse:
                server = pulse.server_info()

                # Update output
                self._output.clear()
                for sink in pulse.sink_list():
                    self._output.append(
                        AudioProfile(
                            sink.name,
                            sink.desc,
                            sink.volume.value_flat,
                            sink.name == server.default_sink_name,
                        )
                    )

                # Update input
                self._input.clear()
                for source in pulse.source_list():
                    self._input.append(
                        AudioProfile(
                            source.name,
                            source.desc,
                            source.volume.value_flat,
                            source.name == server.default_source_name,
                        )
                    )
        except PulseError as err:
            _LOGGER.warning("Can't update PulseAudio data: %s", err)
