"""Tests for image pull progress tracking."""

import pytest

from supervisor.docker.manager import PullLogEntry, PullProgressDetail
from supervisor.docker.pull_progress import (
    DOWNLOAD_WEIGHT,
    EXTRACT_WEIGHT,
    ImagePullProgress,
    LayerProgress,
)


class TestLayerProgress:
    """Tests for LayerProgress class."""

    def test_already_exists_layer(self):
        """Test that already existing layer returns 100%."""
        layer = LayerProgress(layer_id="abc123", already_exists=True)
        assert layer.calculate_progress() == 100.0

    def test_extract_complete_layer(self):
        """Test that extracted layer returns 100%."""
        layer = LayerProgress(
            layer_id="abc123",
            total_size=1000,
            download_current=1000,
            download_complete=True,
            extract_complete=True,
        )
        assert layer.calculate_progress() == 100.0

    def test_download_complete_not_extracted(self):
        """Test layer that finished downloading but not extracting."""
        layer = LayerProgress(
            layer_id="abc123",
            total_size=1000,
            download_current=1000,
            download_complete=True,
            extract_complete=False,
        )
        assert layer.calculate_progress() == DOWNLOAD_WEIGHT  # 70%

    def test_extraction_progress_overlay2(self):
        """Test layer with byte-based extraction progress (overlay2)."""
        layer = LayerProgress(
            layer_id="abc123",
            total_size=1000,
            download_current=1000,
            extract_current=500,  # 50% extracted
            download_complete=True,
            extract_complete=False,
        )
        # 70% + (50% of 30%) = 70% + 15% = 85%
        assert layer.calculate_progress() == DOWNLOAD_WEIGHT + (0.5 * EXTRACT_WEIGHT)

    def test_downloading_progress(self):
        """Test layer during download phase."""
        layer = LayerProgress(
            layer_id="abc123",
            total_size=1000,
            download_current=500,  # 50% downloaded
            download_complete=False,
        )
        # 50% of 70% = 35%
        assert layer.calculate_progress() == 35.0

    def test_no_size_info_yet(self):
        """Test layer with no size information."""
        layer = LayerProgress(layer_id="abc123")
        assert layer.calculate_progress() == 0.0


class TestImagePullProgress:
    """Tests for ImagePullProgress class."""

    def test_empty_progress(self):
        """Test progress with no layers."""
        progress = ImagePullProgress()
        assert progress.calculate_progress() == 0.0

    def test_all_layers_already_exist(self):
        """Test when all layers already exist locally.

        When an image is fully cached, there are no "Downloading" events.
        Progress stays at 0 until the job completes and sets 100%.
        """
        progress = ImagePullProgress()

        # Simulate "Already exists" events
        entry1 = PullLogEntry(
            job_id="test",
            id="layer1",
            status="Already exists",
            progress_detail=PullProgressDetail(),
        )
        entry2 = PullLogEntry(
            job_id="test",
            id="layer2",
            status="Already exists",
            progress_detail=PullProgressDetail(),
        )
        progress.process_event(entry1)
        progress.process_event(entry2)

        # No downloading events = no progress reported (job completion sets 100%)
        assert progress.calculate_progress() == 0.0

    def test_single_layer_download(self):
        """Test progress tracking for single layer download."""
        progress = ImagePullProgress()

        # Pull fs layer
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="layer1",
                status="Pulling fs layer",
                progress_detail=PullProgressDetail(),
            )
        )

        # Start downloading
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="layer1",
                status="Downloading",
                progress_detail=PullProgressDetail(current=500, total=1000),
            )
        )
        # 50% of download phase = 35%
        assert progress.calculate_progress() == pytest.approx(35.0)

        # Download complete
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="layer1",
                status="Download complete",
                progress_detail=PullProgressDetail(),
            )
        )
        assert progress.calculate_progress() == 70.0

        # Pull complete
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="layer1",
                status="Pull complete",
                progress_detail=PullProgressDetail(),
            )
        )
        assert progress.calculate_progress() == 100.0

    def test_multiple_layers_equal_weight_progress(self):
        """Test count-based progress where each layer contributes equally."""
        progress = ImagePullProgress()

        # Two layers: sizes don't matter for weight, each layer = 50%

        # Pulling fs layer for both
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="large",
                status="Pulling fs layer",
                progress_detail=PullProgressDetail(),
            )
        )
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="small",
                status="Pulling fs layer",
                progress_detail=PullProgressDetail(),
            )
        )

        # Large layer: 50% downloaded = 35% layer progress (50% of 70%)
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="large",
                status="Downloading",
                progress_detail=PullProgressDetail(current=500, total=1000),
            )
        )

        # Small layer: 100% downloaded, waiting for extraction = 70% layer progress
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="small",
                status="Download complete",
                progress_detail=PullProgressDetail(),
            )
        )
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="small",
                status="Downloading",
                progress_detail=PullProgressDetail(current=100, total=100),
            )
        )

        # Progress calculation (count-based, equal weight per layer):
        # Large layer: 35% (50% of 70% download weight)
        # Small layer: 70% (download complete)
        # Each layer = 50% weight
        # Total: (35 + 70) / 2 = 52.5%
        assert progress.calculate_progress() == pytest.approx(52.5)

    def test_download_retry(self):
        """Test that download retry resets progress."""
        progress = ImagePullProgress()

        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="layer1",
                status="Pulling fs layer",
                progress_detail=PullProgressDetail(),
            )
        )

        # Download 50%
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="layer1",
                status="Downloading",
                progress_detail=PullProgressDetail(current=500, total=1000),
            )
        )
        assert progress.calculate_progress() == pytest.approx(35.0)

        # Retry
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="layer1",
                status="Retrying in 5 seconds",
            )
        )
        assert progress.calculate_progress() == 0.0

    def test_layer_skips_download(self):
        """Test small layer that goes straight to Download complete."""
        progress = ImagePullProgress()

        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="small",
                status="Pulling fs layer",
                progress_detail=PullProgressDetail(),
            )
        )

        # Goes directly to Download complete (skipping Downloading events)
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="small",
                status="Download complete",
                progress_detail=PullProgressDetail(),
            )
        )

        # Should still work - sets minimal size
        layer = progress.layers["small"]
        assert layer.total_size == 1
        assert layer.download_complete is True

    def test_containerd_extract_progress(self):
        """Test extraction progress with containerd snapshotter (time-based)."""
        progress = ImagePullProgress()

        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="layer1",
                status="Pulling fs layer",
                progress_detail=PullProgressDetail(),
            )
        )

        # Download complete
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="layer1",
                status="Downloading",
                progress_detail=PullProgressDetail(current=1000, total=1000),
            )
        )
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="layer1",
                status="Download complete",
                progress_detail=PullProgressDetail(),
            )
        )

        # Containerd extraction progress (time-based, not byte-based)
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="layer1",
                status="Extracting",
                progress_detail=PullProgressDetail(current=5, units="s"),
            )
        )

        # Should be at 70% (download complete, time-based extraction not tracked)
        assert progress.calculate_progress() == 70.0

        # Pull complete
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="layer1",
                status="Pull complete",
                progress_detail=PullProgressDetail(),
            )
        )
        assert progress.calculate_progress() == 100.0

    def test_overlay2_extract_progress(self):
        """Test extraction progress with overlay2 (byte-based)."""
        progress = ImagePullProgress()

        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="layer1",
                status="Pulling fs layer",
                progress_detail=PullProgressDetail(),
            )
        )

        # Download complete
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="layer1",
                status="Downloading",
                progress_detail=PullProgressDetail(current=1000, total=1000),
            )
        )
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="layer1",
                status="Download complete",
                progress_detail=PullProgressDetail(),
            )
        )

        # At download complete, progress should be 70%
        assert progress.calculate_progress() == 70.0

        # Overlay2 extraction progress (byte-based, 50% extracted)
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="layer1",
                status="Extracting",
                progress_detail=PullProgressDetail(current=500, total=1000),
            )
        )

        # Should be at 70% + (50% of 30%) = 85%
        assert progress.calculate_progress() == pytest.approx(85.0)

        # Extraction continues to 80%
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="layer1",
                status="Extracting",
                progress_detail=PullProgressDetail(current=800, total=1000),
            )
        )

        # Should be at 70% + (80% of 30%) = 94%
        assert progress.calculate_progress() == pytest.approx(94.0)

        # Pull complete
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="layer1",
                status="Pull complete",
                progress_detail=PullProgressDetail(),
            )
        )
        assert progress.calculate_progress() == 100.0

    def test_get_stage(self):
        """Test stage detection."""
        progress = ImagePullProgress()

        assert progress.get_stage() is None

        # Add a layer that needs downloading
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="layer1",
                status="Pulling fs layer",
                progress_detail=PullProgressDetail(),
            )
        )
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="layer1",
                status="Downloading",
                progress_detail=PullProgressDetail(current=500, total=1000),
            )
        )
        assert progress.get_stage() == "Downloading"

        # Download complete
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="layer1",
                status="Download complete",
                progress_detail=PullProgressDetail(),
            )
        )
        assert progress.get_stage() == "Extracting"

        # Pull complete
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="layer1",
                status="Pull complete",
                progress_detail=PullProgressDetail(),
            )
        )
        assert progress.get_stage() == "Pull complete"

    def test_should_update_job(self):
        """Test update threshold logic."""
        progress = ImagePullProgress()

        # Initial state - no updates
        should_update, _ = progress.should_update_job()
        assert not should_update

        # Add a layer and start downloading
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="layer1",
                status="Pulling fs layer",
                progress_detail=PullProgressDetail(),
            )
        )

        # Small progress - 1%
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="layer1",
                status="Downloading",
                progress_detail=PullProgressDetail(current=20, total=1000),
            )
        )
        # 2% of download = 1.4% total
        should_update, current = progress.should_update_job()
        assert should_update
        assert current == pytest.approx(1.4)

        # Tiny increment - shouldn't trigger update
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="layer1",
                status="Downloading",
                progress_detail=PullProgressDetail(current=25, total=1000),
            )
        )
        should_update, _ = progress.should_update_job()
        assert not should_update

        # Larger increment - should trigger
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="layer1",
                status="Downloading",
                progress_detail=PullProgressDetail(current=100, total=1000),
            )
        )
        should_update, _ = progress.should_update_job()
        assert should_update

    def test_verifying_checksum(self):
        """Test that Verifying Checksum marks download as nearly complete."""
        progress = ImagePullProgress()

        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="layer1",
                status="Pulling fs layer",
                progress_detail=PullProgressDetail(),
            )
        )
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="layer1",
                status="Downloading",
                progress_detail=PullProgressDetail(current=800, total=1000),
            )
        )
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="layer1",
                status="Verifying Checksum",
                progress_detail=PullProgressDetail(),
            )
        )

        layer = progress.layers["layer1"]
        assert layer.download_current == 1000  # Should be set to total

    def test_events_without_status_ignored(self):
        """Test that events without status are ignored."""
        progress = ImagePullProgress()

        # Event without status (just id field)
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="abc123",
            )
        )

        # Event without id
        progress.process_event(
            PullLogEntry(
                job_id="test",
                status="Digest: sha256:abc123",
            )
        )

        # They shouldn't create layers or cause errors
        assert len(progress.layers) == 0

    def test_mixed_already_exists_and_pull(self):
        """Test combination of cached and pulled layers."""
        progress = ImagePullProgress()

        # Layer 1 already exists
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="cached",
                status="Already exists",
                progress_detail=PullProgressDetail(),
            )
        )

        # Layer 2 needs to be pulled
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="pulled",
                status="Pulling fs layer",
                progress_detail=PullProgressDetail(),
            )
        )
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="pulled",
                status="Downloading",
                progress_detail=PullProgressDetail(current=500, total=1000),
            )
        )

        # Only 1 layer needs pulling (cached layer excluded)
        # pulled: 35% (50% of 70% download weight)
        assert progress.calculate_progress() == pytest.approx(35.0)

        # Complete the pulled layer
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="pulled",
                status="Download complete",
                progress_detail=PullProgressDetail(),
            )
        )
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="pulled",
                status="Pull complete",
                progress_detail=PullProgressDetail(),
            )
        )

        assert progress.calculate_progress() == 100.0

    def test_pending_layers_prevent_premature_100(self):
        """Test that layers without size info scale down progress."""
        progress = ImagePullProgress()

        # First batch of layers - they complete
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="layer1",
                status="Pulling fs layer",
                progress_detail=PullProgressDetail(),
            )
        )
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="layer2",
                status="Pulling fs layer",
                progress_detail=PullProgressDetail(),
            )
        )

        # Layer1 downloads and completes
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="layer1",
                status="Downloading",
                progress_detail=PullProgressDetail(current=1000, total=1000),
            )
        )
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="layer1",
                status="Pull complete",
                progress_detail=PullProgressDetail(),
            )
        )

        # Layer2 is still pending (no size info yet) - simulating Docker rate limiting
        # Progress should NOT be 100% because layer2 hasn't started

        # Layer1 is 100% complete, layer2 is 0%
        # With scaling: 1 known layer at 100%, 1 pending layer
        # Scale factor = 1/(1+1) = 0.5, so progress = 100 * 0.5 = 50%
        assert progress.calculate_progress() == pytest.approx(50.0)

        # Now layer2 starts downloading
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="layer2",
                status="Downloading",
                progress_detail=PullProgressDetail(current=500, total=1000),
            )
        )

        # Now both layers have size info, no scaling needed
        # Layer1: 100%, Layer2: 35% (50% of 70%)
        # Weighted by equal size: (100 + 35) / 2 = 67.5%
        assert progress.calculate_progress() == pytest.approx(67.5)

        # Complete layer2
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="layer2",
                status="Pull complete",
                progress_detail=PullProgressDetail(),
            )
        )

        assert progress.calculate_progress() == 100.0

    def test_large_layers_appearing_late_dont_cause_regression(self):
        """Test that large layers discovered late don't cause progress to drop.

        This simulates Docker's rate-limiting behavior where small layers complete
        first, then large layers start downloading later.
        """
        progress = ImagePullProgress()

        # All layers announced upfront (Docker does this)
        for layer_id in ["small1", "small2", "big1", "big2"]:
            progress.process_event(
                PullLogEntry(
                    job_id="test",
                    id=layer_id,
                    status="Pulling fs layer",
                    progress_detail=PullProgressDetail(),
                )
            )

        # Big layers are "Waiting" (rate limited)
        for layer_id in ["big1", "big2"]:
            progress.process_event(
                PullLogEntry(
                    job_id="test",
                    id=layer_id,
                    status="Waiting",
                    progress_detail=PullProgressDetail(),
                )
            )

        # Small layers download quickly (1KB each)
        for layer_id in ["small1", "small2"]:
            progress.process_event(
                PullLogEntry(
                    job_id="test",
                    id=layer_id,
                    status="Downloading",
                    progress_detail=PullProgressDetail(current=1000, total=1000),
                )
            )
            progress.process_event(
                PullLogEntry(
                    job_id="test",
                    id=layer_id,
                    status="Pull complete",
                    progress_detail=PullProgressDetail(),
                )
            )

        # At this point, 2 small layers are complete, 2 big layers are unknown size
        progress_before_big = progress.calculate_progress()

        # Now big layers start downloading - they're 100MB each!
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="big1",
                status="Downloading",
                progress_detail=PullProgressDetail(current=1000000, total=100000000),
            )
        )

        progress_after_big1 = progress.calculate_progress()

        # Progress should NOT drop significantly when big layer appears
        # The monotonic tracking in should_update_job will help, but the
        # raw calculation should also not regress too badly
        assert progress_after_big1 >= progress_before_big * 0.5, (
            f"Progress dropped too much: {progress_before_big} -> {progress_after_big1}"
        )

        # Second big layer appears
        progress.process_event(
            PullLogEntry(
                job_id="test",
                id="big2",
                status="Downloading",
                progress_detail=PullProgressDetail(current=1000000, total=100000000),
            )
        )

        # Should still make forward progress overall
        # Complete all layers
        for layer_id in ["big1", "big2"]:
            progress.process_event(
                PullLogEntry(
                    job_id="test",
                    id=layer_id,
                    status="Pull complete",
                    progress_detail=PullProgressDetail(),
                )
            )

        assert progress.calculate_progress() == 100.0
