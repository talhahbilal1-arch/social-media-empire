"""Integration tests for VideoGenerator pipeline orchestration.

Tests verify all Phase 6 success criteria:
1. Sequential pipeline coordination (script -> video -> audio -> composite -> upload)
2. Error isolation in batch processing (one failure doesn't crash batch)
3. Temp file cleanup (compositor.cleanup() always called via finally)
4. Batch completion with accurate counts
5. Memory management (gc.collect() between videos)
"""

import gc
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil

from src.orchestration import VideoGenerator, GenerationResult, BatchResult
from src.models.brand import BrandConfig, ColorPalette
from src.models.content import Script, AudioResult
from src.video.timing import WordTiming, SentenceTiming


@pytest.fixture
def mock_brand_config():
    """Create a mock brand config for testing."""
    return BrandConfig(
        name="Test Brand",
        slug="test-brand",
        colors=ColorPalette(
            primary="#FF0000",
            secondary="#00FF00"
        ),
        tts_voice="en-US-JennyNeural",
        cta_text="Visit us!",
        cta_url="https://example.com"
    )


@pytest.fixture
def temp_dirs():
    """Create temporary directories for testing."""
    temp_base = tempfile.mkdtemp()
    output_dir = Path(temp_base) / "output"
    temp_dir = Path(temp_base) / "temp"
    output_dir.mkdir()
    temp_dir.mkdir()
    yield output_dir, temp_dir
    shutil.rmtree(temp_base, ignore_errors=True)


class TestGenerationResult:
    """Tests for GenerationResult dataclass."""

    def test_success_result(self):
        """Successful generation should have success=True and no error."""
        result = GenerationResult(
            success=True,
            video_path=Path("output/test.mp4"),
            public_url="https://example.com/test.mp4",
            duration_ms=1500.0
        )
        assert result.success is True
        assert result.error is None
        assert result.video_path == Path("output/test.mp4")
        assert result.public_url == "https://example.com/test.mp4"

    def test_failure_result(self):
        """Failed generation should have success=False and error message."""
        result = GenerationResult(
            success=False,
            error="API rate limit exceeded"
        )
        assert result.success is False
        assert "rate limit" in result.error
        assert result.video_path is None
        assert result.public_url is None

    def test_default_values(self):
        """Default values should indicate failure state."""
        result = GenerationResult()
        assert result.success is False
        assert result.video_path is None
        assert result.duration_ms == 0.0


class TestBatchResult:
    """Tests for BatchResult dataclass."""

    def test_counts(self):
        """Batch should correctly count successes and failures."""
        results = [
            GenerationResult(success=True),
            GenerationResult(success=True),
            GenerationResult(success=False, error="Failed"),
        ]
        batch = BatchResult(results=results)
        assert batch.success_count == 2
        assert batch.failure_count == 1
        assert batch.total_count == 3

    def test_success_rate(self):
        """Success rate should be calculated correctly."""
        results = [
            GenerationResult(success=True),
            GenerationResult(success=False, error="Failed"),
        ]
        batch = BatchResult(results=results)
        assert batch.success_rate == 0.5

    def test_empty_batch(self):
        """Empty batch should have zero counts and 0.0 success rate."""
        batch = BatchResult(results=[])
        assert batch.success_count == 0
        assert batch.failure_count == 0
        assert batch.total_count == 0
        assert batch.success_rate == 0.0

    def test_all_success(self):
        """All successful batch should have 1.0 success rate."""
        results = [
            GenerationResult(success=True),
            GenerationResult(success=True),
            GenerationResult(success=True),
        ]
        batch = BatchResult(results=results)
        assert batch.success_rate == 1.0

    def test_all_failure(self):
        """All failed batch should have 0.0 success rate."""
        results = [
            GenerationResult(success=False, error="Error 1"),
            GenerationResult(success=False, error="Error 2"),
        ]
        batch = BatchResult(results=results)
        assert batch.success_rate == 0.0


class TestVideoGeneratorInit:
    """Tests for VideoGenerator initialization."""

    def test_creates_output_dirs(self, temp_dirs):
        """Output and temp directories should be created."""
        output_dir, temp_dir = temp_dirs
        # Remove dirs to test creation
        output_dir.rmdir()
        temp_dir.rmdir()

        vg = VideoGenerator(
            script_generator=Mock(),
            video_fetcher=Mock(),
            audio_synthesizer=Mock(),
            output_dir=output_dir,
            temp_dir=temp_dir
        )
        assert output_dir.exists()
        assert temp_dir.exists()

    def test_accepts_custom_clients(self):
        """Custom clients should be used when provided."""
        mock_script_gen = Mock()
        mock_video_fetch = Mock()
        mock_audio_synth = Mock()
        mock_storage = Mock()

        vg = VideoGenerator(
            script_generator=mock_script_gen,
            video_fetcher=mock_video_fetch,
            audio_synthesizer=mock_audio_synth,
            storage_client=mock_storage
        )

        assert vg.script_generator is mock_script_gen
        assert vg.video_fetcher is mock_video_fetch
        assert vg.audio_synthesizer is mock_audio_synth
        assert vg.storage_client is mock_storage


class TestPipelineCoordination:
    """Tests for sequential pipeline execution (Success Criteria 1)."""

    def test_pipeline_executes_in_order(self, mock_brand_config, temp_dirs):
        """Pipeline should execute in order: script -> video -> audio -> composite -> upload."""
        output_dir, temp_dir = temp_dirs
        call_order = []

        # Create mocks that record call order
        mock_script_gen = Mock()
        mock_script_gen.generate.side_effect = lambda *a, **k: (
            call_order.append("script"),
            Mock(
                topic="Test topic for video",
                voiceover="Test sentence one. Test sentence two.",
                search_terms=["test"],
                estimated_duration=30
            )
        )[1]

        mock_video_fetch = Mock()
        mock_video_fetch.fetch.side_effect = lambda *a, **k: (
            call_order.append("video"),
            Path("test_video.mp4")
        )[1]

        mock_audio_synth = Mock()
        mock_audio_synth.synthesize.side_effect = lambda *a, **k: (
            call_order.append("audio"),
            Mock(
                word_timings=[
                    WordTiming(text="Test", start=0.0, end=0.5),
                    WordTiming(text="sentence", start=0.5, end=1.0),
                    WordTiming(text="one.", start=1.0, end=1.5),
                    WordTiming(text="Test", start=1.5, end=2.0),
                    WordTiming(text="sentence", start=2.0, end=2.5),
                    WordTiming(text="two.", start=2.5, end=3.0),
                ],
                duration_ms=3000,
                audio_path=Path("test.mp3")
            )
        )[1]

        mock_storage = Mock()
        mock_storage.upload.side_effect = lambda *a, **k: (
            call_order.append("upload"),
            Mock(public_url="https://example.com/video.mp4")
        )[1]

        # Mock compositor to avoid actual video processing
        with patch("src.orchestration.video_generator.VideoCompositor") as MockCompositor:
            mock_comp_instance = MockCompositor.return_value
            mock_comp_instance.compose_video.side_effect = lambda *a, **k: call_order.append("composite")
            mock_comp_instance.cleanup = Mock()

            vg = VideoGenerator(
                script_generator=mock_script_gen,
                video_fetcher=mock_video_fetch,
                audio_synthesizer=mock_audio_synth,
                storage_client=mock_storage,
                output_dir=output_dir,
                temp_dir=temp_dir
            )
            result = vg.generate_one(mock_brand_config)

        assert call_order == ["script", "video", "audio", "composite", "upload"]
        assert result.success is True

    def test_upload_skipped_when_disabled(self, mock_brand_config, temp_dirs):
        """Upload should be skipped when upload=False."""
        output_dir, temp_dir = temp_dirs
        call_order = []

        mock_script_gen = Mock()
        mock_script_gen.generate.return_value = Mock(
            topic="Test topic",
            voiceover="Test.",
            search_terms=["test"],
            estimated_duration=30
        )

        mock_video_fetch = Mock()
        mock_video_fetch.fetch.return_value = Path("test.mp4")

        mock_audio_synth = Mock()
        mock_audio_synth.synthesize.return_value = Mock(
            word_timings=[WordTiming(text="Test.", start=0.0, end=1.0)],
            duration_ms=1000,
            audio_path=Path("test.mp3")
        )

        mock_storage = Mock()
        mock_storage.upload.side_effect = lambda *a, **k: call_order.append("upload")

        with patch("src.orchestration.video_generator.VideoCompositor") as MockCompositor:
            mock_comp_instance = MockCompositor.return_value
            mock_comp_instance.cleanup = Mock()

            vg = VideoGenerator(
                script_generator=mock_script_gen,
                video_fetcher=mock_video_fetch,
                audio_synthesizer=mock_audio_synth,
                storage_client=mock_storage,
                output_dir=output_dir,
                temp_dir=temp_dir
            )
            result = vg.generate_one(mock_brand_config, upload=False)

        assert "upload" not in call_order
        assert result.success is True
        assert result.public_url is None


class TestErrorIsolation:
    """Tests for error handling and isolation (Success Criteria 2)."""

    def test_single_failure_doesnt_crash_batch(self, mock_brand_config, temp_dirs):
        """One video failure should not stop other videos in batch."""
        output_dir, temp_dir = temp_dirs
        call_count = [0]

        mock_script_gen = Mock()

        def script_side_effect(*a, **k):
            call_count[0] += 1
            if call_count[0] == 2:  # Fail on second video
                raise Exception("Simulated API failure")
            return Mock(
                topic="Test topic",
                voiceover="Test.",
                search_terms=["test"],
                estimated_duration=30
            )

        mock_script_gen.generate.side_effect = script_side_effect

        mock_video_fetch = Mock()
        mock_video_fetch.fetch.return_value = Path("test.mp4")

        mock_audio_synth = Mock()
        mock_audio_synth.synthesize.return_value = Mock(
            word_timings=[WordTiming(text="Test.", start=0.0, end=1.0)],
            duration_ms=1000,
            audio_path=Path("test.mp3")
        )

        mock_storage = Mock()
        mock_storage.upload.return_value = Mock(public_url="https://example.com/video.mp4")

        with patch("src.orchestration.video_generator.VideoCompositor") as MockCompositor:
            mock_comp_instance = MockCompositor.return_value
            mock_comp_instance.cleanup = Mock()

            vg = VideoGenerator(
                script_generator=mock_script_gen,
                video_fetcher=mock_video_fetch,
                audio_synthesizer=mock_audio_synth,
                storage_client=mock_storage,
                output_dir=output_dir,
                temp_dir=temp_dir
            )
            result = vg.generate_batch(mock_brand_config, count=3)

        # Should have 3 results: 2 success, 1 failure
        assert result.total_count == 3
        assert result.failure_count == 1
        assert result.success_count == 2

    def test_failure_includes_error_message(self, mock_brand_config, temp_dirs):
        """Failed generation should capture error message."""
        output_dir, temp_dir = temp_dirs
        mock_script_gen = Mock()
        mock_script_gen.generate.side_effect = Exception("API rate limit exceeded")

        vg = VideoGenerator(
            script_generator=mock_script_gen,
            video_fetcher=Mock(),
            audio_synthesizer=Mock(),
            output_dir=output_dir,
            temp_dir=temp_dir
        )
        result = vg.generate_one(mock_brand_config)

        assert result.success is False
        assert "rate limit" in result.error

    def test_all_videos_fail_gracefully(self, mock_brand_config, temp_dirs):
        """Batch should complete even if all videos fail."""
        output_dir, temp_dir = temp_dirs

        mock_script_gen = Mock()
        mock_script_gen.generate.side_effect = Exception("Always fails")

        vg = VideoGenerator(
            script_generator=mock_script_gen,
            video_fetcher=Mock(),
            audio_synthesizer=Mock(),
            output_dir=output_dir,
            temp_dir=temp_dir
        )
        result = vg.generate_batch(mock_brand_config, count=3)

        assert result.total_count == 3
        assert result.failure_count == 3
        assert result.success_count == 0
        assert result.success_rate == 0.0


class TestTempFileCleanup:
    """Tests for temporary file cleanup (Success Criteria 3)."""

    def test_cleanup_on_success(self, mock_brand_config, temp_dirs):
        """Compositor cleanup should be called after successful generation."""
        output_dir, temp_dir = temp_dirs
        cleanup_called = [False]

        with patch("src.orchestration.video_generator.VideoCompositor") as MockCompositor:
            mock_comp = MockCompositor.return_value

            def cleanup_side_effect():
                cleanup_called[0] = True

            mock_comp.cleanup.side_effect = cleanup_side_effect

            mock_script_gen = Mock()
            mock_script_gen.generate.return_value = Mock(
                topic="Test topic",
                voiceover="Test.",
                search_terms=["test"],
                estimated_duration=30
            )

            mock_video_fetch = Mock()
            mock_video_fetch.fetch.return_value = Path("test.mp4")

            mock_audio_synth = Mock()
            mock_audio_synth.synthesize.return_value = Mock(
                word_timings=[WordTiming(text="Test.", start=0.0, end=1.0)],
                duration_ms=1000,
                audio_path=Path("test.mp3")
            )

            mock_storage = Mock()
            mock_storage.upload.return_value = Mock(public_url="https://example.com/video.mp4")

            vg = VideoGenerator(
                script_generator=mock_script_gen,
                video_fetcher=mock_video_fetch,
                audio_synthesizer=mock_audio_synth,
                storage_client=mock_storage,
                output_dir=output_dir,
                temp_dir=temp_dir
            )
            result = vg.generate_one(mock_brand_config)

        assert cleanup_called[0], "compositor.cleanup() should be called on success"
        assert result.success is True

    def test_cleanup_on_failure(self, mock_brand_config, temp_dirs):
        """Compositor cleanup should be called even when generation fails."""
        output_dir, temp_dir = temp_dirs
        cleanup_called = [False]

        with patch("src.orchestration.video_generator.VideoCompositor") as MockCompositor:
            mock_comp = MockCompositor.return_value

            def cleanup_side_effect():
                cleanup_called[0] = True

            mock_comp.cleanup.side_effect = cleanup_side_effect
            mock_comp.compose_video.side_effect = Exception("FFmpeg error")

            mock_script_gen = Mock()
            mock_script_gen.generate.return_value = Mock(
                topic="Test topic",
                voiceover="Test.",
                search_terms=["test"],
                estimated_duration=30
            )

            mock_video_fetch = Mock()
            mock_video_fetch.fetch.return_value = Path("test.mp4")

            mock_audio_synth = Mock()
            mock_audio_synth.synthesize.return_value = Mock(
                word_timings=[WordTiming(text="Test.", start=0.0, end=1.0)],
                duration_ms=1000,
                audio_path=Path("test.mp3")
            )

            vg = VideoGenerator(
                script_generator=mock_script_gen,
                video_fetcher=mock_video_fetch,
                audio_synthesizer=mock_audio_synth,
                output_dir=output_dir,
                temp_dir=temp_dir
            )
            result = vg.generate_one(mock_brand_config)

        assert cleanup_called[0], "compositor.cleanup() should be called even on failure"
        assert result.success is False

    def test_cleanup_on_early_failure(self, mock_brand_config, temp_dirs):
        """Cleanup should not fail even when compositor was never created."""
        output_dir, temp_dir = temp_dirs

        mock_script_gen = Mock()
        mock_script_gen.generate.side_effect = Exception("Script generation failed")

        vg = VideoGenerator(
            script_generator=mock_script_gen,
            video_fetcher=Mock(),
            audio_synthesizer=Mock(),
            output_dir=output_dir,
            temp_dir=temp_dir
        )

        # Should not raise - cleanup handles None compositor
        result = vg.generate_one(mock_brand_config)

        assert result.success is False
        assert "Script generation failed" in result.error


class TestBatchCompletion:
    """Tests for batch processing completion (Success Criteria 4 & 5)."""

    def test_batch_reports_final_counts(self, mock_brand_config, temp_dirs):
        """Batch should report accurate success/failure counts."""
        output_dir, temp_dir = temp_dirs
        failure_indices = [1, 3]  # Fail 2nd and 4th videos (0-indexed)

        call_count = [0]
        mock_script_gen = Mock()

        def script_side_effect(*a, **k):
            call_count[0] += 1
            if call_count[0] in [i + 1 for i in failure_indices]:
                raise Exception("Simulated failure")
            return Mock(
                topic="Test topic",
                voiceover="Test.",
                search_terms=["test"],
                estimated_duration=30
            )

        mock_script_gen.generate.side_effect = script_side_effect

        mock_video_fetch = Mock()
        mock_video_fetch.fetch.return_value = Path("test.mp4")

        mock_audio_synth = Mock()
        mock_audio_synth.synthesize.return_value = Mock(
            word_timings=[WordTiming(text="Test.", start=0.0, end=1.0)],
            duration_ms=1000,
            audio_path=Path("test.mp3")
        )

        mock_storage = Mock()
        mock_storage.upload.return_value = Mock(public_url="https://example.com/video.mp4")

        with patch("src.orchestration.video_generator.VideoCompositor") as MockCompositor:
            mock_comp_instance = MockCompositor.return_value
            mock_comp_instance.cleanup = Mock()

            vg = VideoGenerator(
                script_generator=mock_script_gen,
                video_fetcher=mock_video_fetch,
                audio_synthesizer=mock_audio_synth,
                storage_client=mock_storage,
                output_dir=output_dir,
                temp_dir=temp_dir
            )
            result = vg.generate_batch(mock_brand_config, count=5)

        assert result.total_count == 5
        assert result.success_count == 3
        assert result.failure_count == 2
        assert 0.5 < result.success_rate < 0.7  # 60% success rate

    def test_gc_called_between_videos(self, mock_brand_config, temp_dirs):
        """Garbage collection should run between videos."""
        output_dir, temp_dir = temp_dirs

        gc_calls = []
        original_collect = gc.collect

        def mock_gc_collect(*args, **kwargs):
            gc_calls.append(True)
            return original_collect(*args, **kwargs)

        mock_script_gen = Mock()
        mock_script_gen.generate.return_value = Mock(
            topic="Test topic",
            voiceover="Test.",
            search_terms=["test"],
            estimated_duration=30
        )

        mock_video_fetch = Mock()
        mock_video_fetch.fetch.return_value = Path("test.mp4")

        mock_audio_synth = Mock()
        mock_audio_synth.synthesize.return_value = Mock(
            word_timings=[WordTiming(text="Test.", start=0.0, end=1.0)],
            duration_ms=1000,
            audio_path=Path("test.mp3")
        )

        mock_storage = Mock()
        mock_storage.upload.return_value = Mock(public_url="https://example.com/video.mp4")

        with patch("src.orchestration.video_generator.VideoCompositor") as MockCompositor:
            mock_comp_instance = MockCompositor.return_value
            mock_comp_instance.cleanup = Mock()

            with patch("gc.collect", mock_gc_collect):
                vg = VideoGenerator(
                    script_generator=mock_script_gen,
                    video_fetcher=mock_video_fetch,
                    audio_synthesizer=mock_audio_synth,
                    storage_client=mock_storage,
                    output_dir=output_dir,
                    temp_dir=temp_dir
                )
                vg.generate_batch(mock_brand_config, count=3)

        # Should have at least 3 gc.collect() calls (one per video)
        assert len(gc_calls) >= 3

    def test_empty_batch(self, mock_brand_config, temp_dirs):
        """Batch with count=0 should return empty result."""
        output_dir, temp_dir = temp_dirs

        vg = VideoGenerator(
            script_generator=Mock(),
            video_fetcher=Mock(),
            audio_synthesizer=Mock(),
            output_dir=output_dir,
            temp_dir=temp_dir
        )

        result = vg.generate_batch(mock_brand_config, count=0)

        assert result.total_count == 0
        assert result.success_rate == 0.0


class TestMultiBrandGeneration:
    """Tests for generate_for_brands() method."""

    def test_processes_multiple_brands(self, temp_dirs):
        """Should process videos for multiple brands."""
        output_dir, temp_dir = temp_dirs

        mock_script_gen = Mock()
        mock_script_gen.generate.return_value = Mock(
            topic="Test topic",
            voiceover="Test.",
            search_terms=["test"],
            estimated_duration=30
        )

        mock_video_fetch = Mock()
        mock_video_fetch.fetch.return_value = Path("test.mp4")

        mock_audio_synth = Mock()
        mock_audio_synth.synthesize.return_value = Mock(
            word_timings=[WordTiming(text="Test.", start=0.0, end=1.0)],
            duration_ms=1000,
            audio_path=Path("test.mp3")
        )

        mock_storage = Mock()
        mock_storage.upload.return_value = Mock(public_url="https://example.com/video.mp4")

        # Mock BrandLoader
        mock_brand = BrandConfig(
            name="Test Brand",
            slug="test-brand",
            colors=ColorPalette(primary="#FF0000", secondary="#00FF00"),
            tts_voice="en-US-JennyNeural",
            cta_text="Test CTA",
            cta_url="https://example.com"
        )

        with patch("src.orchestration.video_generator.VideoCompositor") as MockCompositor:
            mock_comp_instance = MockCompositor.return_value
            mock_comp_instance.cleanup = Mock()

            with patch("src.orchestration.video_generator.BrandLoader") as MockLoader:
                MockLoader.return_value.load.return_value = mock_brand

                vg = VideoGenerator(
                    script_generator=mock_script_gen,
                    video_fetcher=mock_video_fetch,
                    audio_synthesizer=mock_audio_synth,
                    storage_client=mock_storage,
                    output_dir=output_dir,
                    temp_dir=temp_dir
                )
                results = vg.generate_for_brands(
                    ["brand-a", "brand-b"],
                    count_per_brand=2
                )

        assert "brand-a" in results
        assert "brand-b" in results
        assert results["brand-a"].total_count == 2
        assert results["brand-b"].total_count == 2

    def test_one_brand_failure_doesnt_stop_others(self, temp_dirs):
        """Failure in one brand should not stop processing of others."""
        output_dir, temp_dir = temp_dirs

        mock_script_gen = Mock()
        mock_script_gen.generate.return_value = Mock(
            topic="Test topic",
            voiceover="Test.",
            search_terms=["test"],
            estimated_duration=30
        )

        mock_video_fetch = Mock()
        mock_video_fetch.fetch.return_value = Path("test.mp4")

        mock_audio_synth = Mock()
        mock_audio_synth.synthesize.return_value = Mock(
            word_timings=[WordTiming(text="Test.", start=0.0, end=1.0)],
            duration_ms=1000,
            audio_path=Path("test.mp3")
        )

        mock_storage = Mock()
        mock_storage.upload.return_value = Mock(public_url="https://example.com/video.mp4")

        mock_brand = BrandConfig(
            name="Test Brand",
            slug="test-brand",
            colors=ColorPalette(primary="#FF0000", secondary="#00FF00"),
            tts_voice="en-US-JennyNeural",
            cta_text="Test CTA",
            cta_url="https://example.com"
        )

        with patch("src.orchestration.video_generator.VideoCompositor") as MockCompositor:
            mock_comp_instance = MockCompositor.return_value
            mock_comp_instance.cleanup = Mock()

            with patch("src.orchestration.video_generator.BrandLoader") as MockLoader:
                loader_instance = MockLoader.return_value

                def load_brand(slug):
                    if slug == "failing-brand":
                        raise Exception("Brand config not found")
                    return mock_brand

                loader_instance.load.side_effect = load_brand

                vg = VideoGenerator(
                    script_generator=mock_script_gen,
                    video_fetcher=mock_video_fetch,
                    audio_synthesizer=mock_audio_synth,
                    storage_client=mock_storage,
                    output_dir=output_dir,
                    temp_dir=temp_dir
                )
                results = vg.generate_for_brands(
                    ["failing-brand", "working-brand"],
                    count_per_brand=1
                )

        # Both brands should have results
        assert "failing-brand" in results
        assert "working-brand" in results

        # Failing brand should have 1 failed result
        assert results["failing-brand"].failure_count == 1

        # Working brand should succeed
        assert results["working-brand"].success_count == 1
