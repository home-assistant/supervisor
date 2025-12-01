"""Image pull progress tracking."""

from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass, field
from enum import Enum
import logging
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from .manager import PullLogEntry

_LOGGER = logging.getLogger(__name__)

# Progress weight distribution: 70% downloading, 30% extraction
DOWNLOAD_WEIGHT = 70.0
EXTRACT_WEIGHT = 30.0


class LayerPullStatus(Enum):
    """Status values for pulling an image layer.

    These are a subset of the statuses in a docker pull image log.
    The order field allows comparing which stage is further along.
    """

    PULLING_FS_LAYER = 1, "Pulling fs layer"
    WAITING = 1, "Waiting"
    RETRYING = 2, "Retrying"  # Matches "Retrying in N seconds"
    DOWNLOADING = 3, "Downloading"
    VERIFYING_CHECKSUM = 4, "Verifying Checksum"
    DOWNLOAD_COMPLETE = 5, "Download complete"
    EXTRACTING = 6, "Extracting"
    PULL_COMPLETE = 7, "Pull complete"
    ALREADY_EXISTS = 7, "Already exists"

    def __init__(self, order: int, status: str) -> None:
        """Set fields from values."""
        self.order = order
        self.status = status

    def __eq__(self, value: object, /) -> bool:
        """Check equality, allow string comparisons on status."""
        with suppress(AttributeError):
            return self.status == cast(LayerPullStatus, value).status
        return self.status == value

    def __hash__(self) -> int:
        """Return hash based on status string."""
        return hash(self.status)

    def __lt__(self, other: object) -> bool:
        """Order instances by stage progression."""
        with suppress(AttributeError):
            return self.order < cast(LayerPullStatus, other).order
        return False

    @classmethod
    def from_status(cls, status: str) -> LayerPullStatus | None:
        """Get enum from status string, or None if not recognized."""
        # Handle "Retrying in N seconds" pattern
        if status.startswith("Retrying in "):
            return cls.RETRYING
        for member in cls:
            if member.status == status:
                return member
        return None


@dataclass
class LayerProgress:
    """Track progress of a single layer."""

    layer_id: str
    total_size: int = 0  # Size in bytes (from downloading, reused for extraction)
    download_current: int = 0
    extract_current: int = 0  # Extraction progress in bytes (overlay2 only)
    download_complete: bool = False
    extract_complete: bool = False
    already_exists: bool = False  # Layer was already locally available

    def calculate_progress(self) -> float:
        """Calculate layer progress 0-100.

        Progress is weighted: 70% download, 30% extraction.
        For overlay2, we have byte-based extraction progress.
        For containerd, extraction jumps from 70% to 100% on completion.
        """
        if self.already_exists or self.extract_complete:
            return 100.0

        if self.download_complete:
            # Check if we have extraction progress (overlay2)
            if self.extract_current > 0 and self.total_size > 0:
                extract_pct = min(1.0, self.extract_current / self.total_size)
                return DOWNLOAD_WEIGHT + (extract_pct * EXTRACT_WEIGHT)
            # No extraction progress yet - return 70%
            return DOWNLOAD_WEIGHT

        if self.total_size > 0:
            download_pct = min(1.0, self.download_current / self.total_size)
            return download_pct * DOWNLOAD_WEIGHT

        return 0.0


@dataclass
class ImagePullProgress:
    """Track overall progress of pulling an image.

    Uses count-based progress where each layer contributes equally regardless of size.
    This avoids progress regression when large layers are discovered late due to
    Docker's rate-limiting of concurrent downloads.

    Progress is only reported after the first "Downloading" event, since Docker
    sends "Already exists" and "Pulling fs layer" events before we know the full
    layer count.
    """

    layers: dict[str, LayerProgress] = field(default_factory=dict)
    _last_reported_progress: float = field(default=0.0, repr=False)
    _seen_downloading: bool = field(default=False, repr=False)

    def get_or_create_layer(self, layer_id: str) -> LayerProgress:
        """Get existing layer or create new one."""
        if layer_id not in self.layers:
            self.layers[layer_id] = LayerProgress(layer_id=layer_id)
        return self.layers[layer_id]

    def process_event(self, entry: PullLogEntry) -> None:
        """Process a pull log event and update layer state."""
        # Skip events without layer ID or status
        if not entry.id or not entry.status:
            return

        # Skip metadata events that aren't layer-specific
        # "Pulling from X" has id=tag but isn't a layer
        if entry.status.startswith("Pulling from "):
            return

        # Parse status to enum (returns None for unrecognized statuses)
        status = LayerPullStatus.from_status(entry.status)
        if status is None:
            return

        layer = self.get_or_create_layer(entry.id)

        # Handle "Already exists" - layer is locally available
        if status is LayerPullStatus.ALREADY_EXISTS:
            layer.already_exists = True
            layer.download_complete = True
            layer.extract_complete = True
            return

        # Handle "Pulling fs layer" / "Waiting" - layer is being tracked
        if status in (LayerPullStatus.PULLING_FS_LAYER, LayerPullStatus.WAITING):
            return

        # Handle "Downloading" - update download progress
        if status is LayerPullStatus.DOWNLOADING:
            # Mark that we've seen downloading - now we know layer count is complete
            self._seen_downloading = True
            if (
                entry.progress_detail
                and entry.progress_detail.current is not None
                and entry.progress_detail.total is not None
            ):
                layer.download_current = entry.progress_detail.current
                # Only set total_size if not already set or if this is larger
                # (handles case where total changes during download)
                layer.total_size = max(layer.total_size, entry.progress_detail.total)
            return

        # Handle "Verifying Checksum" - download is essentially complete
        if status is LayerPullStatus.VERIFYING_CHECKSUM:
            if layer.total_size > 0:
                layer.download_current = layer.total_size
            return

        # Handle "Download complete" - download phase done
        if status is LayerPullStatus.DOWNLOAD_COMPLETE:
            layer.download_complete = True
            if layer.total_size > 0:
                layer.download_current = layer.total_size
            elif layer.total_size == 0:
                # Small layer that skipped downloading phase
                # Set minimal size so it doesn't distort weighted average
                layer.total_size = 1
                layer.download_current = 1
            return

        # Handle "Extracting" - extraction in progress
        if status is LayerPullStatus.EXTRACTING:
            # For overlay2: progressDetail has {current, total} in bytes
            # For containerd: progressDetail has {current, units: "s"} (time elapsed)
            # We can only use byte-based progress (overlay2)
            layer.download_complete = True
            if layer.total_size > 0:
                layer.download_current = layer.total_size

            # Check if this is byte-based extraction progress (overlay2)
            # Overlay2 has {current, total} in bytes, no units field
            # Containerd has {current, units: "s"} which is useless for progress
            if (
                entry.progress_detail
                and entry.progress_detail.current is not None
                and entry.progress_detail.units is None
            ):
                # Use layer's total_size from downloading phase (doesn't change)
                layer.extract_current = entry.progress_detail.current
                _LOGGER.debug(
                    "Layer %s extracting: %d/%d (%.1f%%)",
                    layer.layer_id,
                    layer.extract_current,
                    layer.total_size,
                    (layer.extract_current / layer.total_size * 100)
                    if layer.total_size > 0
                    else 0,
                )
            return

        # Handle "Pull complete" - layer is fully done
        if status is LayerPullStatus.PULL_COMPLETE:
            layer.download_complete = True
            layer.extract_complete = True
            if layer.total_size > 0:
                layer.download_current = layer.total_size
            return

        # Handle "Retrying in N seconds" - reset download progress
        if status is LayerPullStatus.RETRYING:
            layer.download_current = 0
            layer.download_complete = False
            return

    def calculate_progress(self) -> float:
        """Calculate overall progress 0-100.

        Uses count-based progress where each layer that needs pulling contributes
        equally. Layers that already exist locally are excluded from the calculation.

        Returns 0 until we've seen the first "Downloading" event, since Docker
        reports "Already exists" and "Pulling fs layer" events before we know
        the complete layer count.
        """
        # Don't report progress until we've seen downloading start
        # This ensures we know the full layer count before calculating progress
        if not self._seen_downloading or not self.layers:
            return 0.0

        # Only count layers that need pulling (exclude already_exists)
        layers_to_pull = [
            layer for layer in self.layers.values() if not layer.already_exists
        ]

        if not layers_to_pull:
            # All layers already exist, nothing to download
            return 100.0

        # Each layer contributes equally: sum of layer progresses / total layers
        total_progress = sum(layer.calculate_progress() for layer in layers_to_pull)
        return total_progress / len(layers_to_pull)

    def get_stage(self) -> str | None:
        """Get current stage based on layer states."""
        if not self.layers:
            return None

        # Check if any layer is still downloading
        for layer in self.layers.values():
            if layer.already_exists:
                continue
            if not layer.download_complete:
                return "Downloading"

        # All downloads complete, check if extracting
        for layer in self.layers.values():
            if layer.already_exists:
                continue
            if not layer.extract_complete:
                return "Extracting"

        # All done
        return "Pull complete"

    def should_update_job(self, threshold: float = 1.0) -> tuple[bool, float]:
        """Check if job should be updated based on progress change.

        Returns (should_update, current_progress).
        Updates are triggered when progress changes by at least threshold%.
        Progress is guaranteed to only increase (monotonic).
        """
        current_progress = self.calculate_progress()

        # Ensure monotonic progress - never report a decrease
        # This can happen when new layers get size info and change the weighted average
        if current_progress < self._last_reported_progress:
            _LOGGER.debug(
                "Progress decreased from %.1f%% to %.1f%%, keeping last reported",
                self._last_reported_progress,
                current_progress,
            )
            return False, self._last_reported_progress

        if current_progress >= self._last_reported_progress + threshold:
            _LOGGER.debug(
                "Progress update: %.1f%% -> %.1f%% (delta: %.1f%%)",
                self._last_reported_progress,
                current_progress,
                current_progress - self._last_reported_progress,
            )
            self._last_reported_progress = current_progress
            return True, current_progress

        return False, self._last_reported_progress
