"""Video generation pipeline orchestrator.

This module provides the VideoGenerator class that orchestrates the complete
video generation pipeline: script -> video -> audio -> composite -> upload.

Features:
- Per-video error isolation in batch processing
- Automatic temp file cleanup via try/finally
- Memory management with gc.collect() between videos
- Optional upload to Supabase storage
"""

import gc
import logging
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from src.models.brand import BrandConfig
from src.models.content import Script, AudioResult
from src.services.script_generator import ScriptGenerator
from src.services.video_fetcher import VideoFetcher
from src.services.audio_synthesizer import AudioSynthesizer
from src.clients.storage import SupabaseClient
from src.video.compositor import VideoCompositor
from src.video.timing import group_words_into_sentences, SentenceTiming
from src.utils.brand_loader import BrandLoader


@dataclass
class GenerationResult:
    """Result of a single video generation attempt.

    Attributes:
        success: Whether the video was successfully generated and uploaded
        video_path: Path to the generated video file (if successful)
        public_url: Public URL of uploaded video (if upload enabled and successful)
        error: Error message if generation failed
        duration_ms: Time taken for generation in milliseconds
    """

    success: bool = False
    video_path: Optional[Path] = None
    public_url: Optional[str] = None
    error: Optional[str] = None
    duration_ms: float = 0.0


@dataclass
class BatchResult:
    """Result of batch video generation.

    Attributes:
        results: List of GenerationResult for each video attempted
        total_duration_ms: Total time for batch processing in milliseconds
    """

    results: List[GenerationResult] = field(default_factory=list)
    total_duration_ms: float = 0.0

    @property
    def success_count(self) -> int:
        """Number of successful generations."""
        return sum(1 for r in self.results if r.success)

    @property
    def failure_count(self) -> int:
        """Number of failed generations."""
        return sum(1 for r in self.results if not r.success)

    @property
    def total_count(self) -> int:
        """Total number of generation attempts."""
        return len(self.results)

    @property
    def success_rate(self) -> float:
        """Success rate as a float (0.0 to 1.0)."""
        if self.total_count == 0:
            return 0.0
        return self.success_count / self.total_count


class VideoGenerator:
    """Orchestrates the complete video generation pipeline.

    Pipeline stages:
    1. Generate script (ScriptGenerator)
    2. Fetch stock video (VideoFetcher)
    3. Synthesize TTS audio (AudioSynthesizer)
    4. Create sentence timings for text overlay
    5. Compose final video (VideoCompositor)
    6. Upload to storage (SupabaseClient) - optional

    Error handling:
    - Each video generation is isolated with try/except
    - Compositor cleanup() always runs via finally block
    - gc.collect() runs after each video in batch mode
    - Failed videos don't crash batch processing

    Example:
        >>> brand_config = load_brand('menopause-planner')
        >>> generator = VideoGenerator()
        >>> result = generator.generate_one(brand_config)
        >>> if result.success:
        ...     print(f"Video uploaded: {result.public_url}")
    """

    def __init__(
        self,
        script_generator: Optional[ScriptGenerator] = None,
        video_fetcher: Optional[VideoFetcher] = None,
        audio_synthesizer: Optional[AudioSynthesizer] = None,
        storage_client: Optional[SupabaseClient] = None,
        output_dir: Optional[Path] = None,
        temp_dir: Optional[Path] = None,
    ) -> None:
        """Initialize VideoGenerator.

        Args:
            script_generator: ScriptGenerator instance (creates default if None)
            video_fetcher: VideoFetcher instance (creates default if None)
            audio_synthesizer: AudioSynthesizer instance (creates default if None)
            storage_client: SupabaseClient instance (creates default if None)
            output_dir: Directory for final video outputs (default: output/)
            temp_dir: Directory for temporary files (default: temp/)
        """
        self.script_generator = script_generator or ScriptGenerator()
        self.video_fetcher = video_fetcher or VideoFetcher()
        self.audio_synthesizer = audio_synthesizer or AudioSynthesizer()
        self.storage_client = storage_client

        self.output_dir = output_dir or Path("output")
        self.temp_dir = temp_dir or Path("temp")

        # Create directories if they don't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger(self.__class__.__name__)

    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences by punctuation.

        Splits on '. ', '! ', and '? ' while keeping the punctuation
        with each sentence.

        Args:
            text: Voiceover text to split

        Returns:
            List of sentences
        """
        # Split on sentence-ending punctuation followed by space or end
        # Use regex to split while keeping the delimiter with the preceding text
        pattern = r'(?<=[.!?])\s+'
        sentences = re.split(pattern, text.strip())

        # Filter out empty strings
        return [s.strip() for s in sentences if s.strip()]

    def _generate_output_filename(self, brand_slug: str) -> str:
        """Generate unique output filename with timestamp.

        Args:
            brand_slug: Brand identifier for filename prefix

        Returns:
            Filename in format: {brand_slug}_{YYYYMMDD_HHMMSS}.mp4
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{brand_slug}_{timestamp}.mp4"

    def _cleanup_temp_files(self, temp_files: List[Path]) -> None:
        """Delete temporary files without raising exceptions.

        Args:
            temp_files: List of paths to delete
        """
        for path in temp_files:
            try:
                if path and path.exists():
                    path.unlink()
                    self.logger.debug(f"Cleaned up temp file: {path}")
            except Exception as e:
                self.logger.warning(f"Failed to cleanup {path}: {e}")

    def generate_one(
        self,
        brand_config: BrandConfig,
        topic_seed: Optional[str] = None,
        upload: bool = True,
    ) -> GenerationResult:
        """Generate a single video for a brand.

        Pipeline:
        1. Generate script with AI
        2. Fetch stock video based on search terms
        3. Synthesize TTS audio from voiceover
        4. Create sentence timings for text overlay
        5. Compose video with overlays and audio
        6. Upload to storage (if enabled)

        Args:
            brand_config: Brand configuration with colors, voice, CTA
            topic_seed: Optional seed for reproducible topic generation
            upload: Whether to upload final video to storage

        Returns:
            GenerationResult with success status, paths, and timing
        """
        start_time = time.time()
        temp_files: List[Path] = []
        compositor: Optional[VideoCompositor] = None

        try:
            # Step 1: Generate script
            self.logger.info(
                f"[1/6] Generating script for {brand_config.slug}",
                extra={"topic_seed": topic_seed}
            )
            step_start = time.time()
            script: Script = self.script_generator.generate(brand_config, topic_seed)
            self.logger.info(
                f"Script generated in {(time.time() - step_start)*1000:.0f}ms",
                extra={"topic": script.topic[:50], "search_terms": script.search_terms}
            )

            # Step 2: Fetch stock video
            self.logger.info(
                f"[2/6] Fetching video for terms: {script.search_terms}",
            )
            step_start = time.time()
            stock_video_path: Path = self.video_fetcher.fetch(
                script.search_terms,
                target_duration=script.estimated_duration
            )
            self.logger.info(
                f"Video fetched in {(time.time() - step_start)*1000:.0f}ms",
                extra={"path": str(stock_video_path)}
            )

            # Step 3: Synthesize audio
            self.logger.info(
                f"[3/6] Synthesizing audio with voice: {brand_config.tts_voice}",
            )
            step_start = time.time()
            audio_result: AudioResult = self.audio_synthesizer.synthesize(
                script.voiceover,
                brand_config
            )
            self.logger.info(
                f"Audio synthesized in {(time.time() - step_start)*1000:.0f}ms",
                extra={"duration_ms": audio_result.duration_ms}
            )

            # Step 4: Create sentence timings
            self.logger.info("[4/6] Creating sentence timings")
            step_start = time.time()
            sentences = self._split_into_sentences(script.voiceover)
            sentence_timings: List[SentenceTiming] = group_words_into_sentences(
                audio_result.word_timings,
                sentences
            )
            self.logger.info(
                f"Sentence timings created in {(time.time() - step_start)*1000:.0f}ms",
                extra={"sentence_count": len(sentence_timings)}
            )

            # Step 5: Compose video
            self.logger.info("[5/6] Composing video")
            step_start = time.time()

            # Generate output path
            output_filename = self._generate_output_filename(brand_config.slug)
            output_path = self.output_dir / output_filename

            # Create compositor and compose
            compositor = VideoCompositor(brand_config)
            compositor.compose_video(
                video_path=str(stock_video_path),
                audio_path=str(audio_result.audio_path),
                sentence_timings=sentence_timings,
                output_path=str(output_path)
            )
            self.logger.info(
                f"Video composed in {(time.time() - step_start)*1000:.0f}ms",
                extra={"output_path": str(output_path)}
            )

            # Step 6: Upload (if enabled)
            public_url = None
            if upload:
                self.logger.info("[6/6] Uploading to storage")
                step_start = time.time()

                if self.storage_client is None:
                    # Create storage client lazily (may not have credentials during testing)
                    self.storage_client = SupabaseClient()

                destination = f"{brand_config.slug}/{output_filename}"
                upload_result = self.storage_client.upload(output_path, destination)
                public_url = upload_result.public_url
                self.logger.info(
                    f"Uploaded in {(time.time() - step_start)*1000:.0f}ms",
                    extra={"public_url": public_url}
                )
            else:
                self.logger.info("[6/6] Skipping upload (disabled)")

            duration_ms = (time.time() - start_time) * 1000
            self.logger.info(
                f"Video generation complete for {brand_config.slug}",
                extra={
                    "duration_ms": duration_ms,
                    "output_path": str(output_path),
                    "public_url": public_url
                }
            )

            return GenerationResult(
                success=True,
                video_path=output_path,
                public_url=public_url,
                duration_ms=duration_ms
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            error_msg = str(e)
            self.logger.error(
                f"Video generation failed for {brand_config.slug}: {error_msg}",
                extra={"duration_ms": duration_ms},
                exc_info=True
            )
            return GenerationResult(
                success=False,
                error=error_msg,
                duration_ms=duration_ms
            )

        finally:
            # CRITICAL: Always clean up compositor resources
            if compositor is not None:
                try:
                    compositor.cleanup()
                    self.logger.debug("Compositor cleanup complete")
                except Exception as e:
                    self.logger.warning(f"Compositor cleanup failed: {e}")

            # Clean up any tracked temp files
            self._cleanup_temp_files(temp_files)

    def generate_batch(
        self,
        brand_config: BrandConfig,
        count: int = 1,
        upload: bool = True,
    ) -> BatchResult:
        """Generate multiple videos for a brand.

        Each video is isolated - a failure in one video does not affect others.
        Garbage collection runs after each video to prevent memory accumulation.

        Args:
            brand_config: Brand configuration
            count: Number of videos to generate
            upload: Whether to upload videos to storage

        Returns:
            BatchResult with all individual results and aggregate stats
        """
        if count <= 0:
            return BatchResult(results=[], total_duration_ms=0.0)

        self.logger.info(
            f"Starting batch generation for {brand_config.slug}",
            extra={"count": count, "upload": upload}
        )

        batch_start = time.time()
        results: List[GenerationResult] = []

        for i in range(count):
            self.logger.info(
                f"Generating video {i + 1}/{count} for {brand_config.slug}"
            )

            # Use unique topic seed for each video
            topic_seed = f"{i}_{time.time()}"

            try:
                result = self.generate_one(brand_config, topic_seed=topic_seed, upload=upload)
                results.append(result)

                if result.success:
                    self.logger.info(
                        f"Video {i + 1}/{count} succeeded",
                        extra={"duration_ms": result.duration_ms}
                    )
                else:
                    self.logger.warning(
                        f"Video {i + 1}/{count} failed: {result.error}"
                    )

            except Exception as e:
                # Belt-and-suspenders: generate_one should catch all errors
                self.logger.error(
                    f"Unexpected error in video {i + 1}/{count}: {e}",
                    exc_info=True
                )
                results.append(GenerationResult(
                    success=False,
                    error=str(e),
                    duration_ms=0.0
                ))

            finally:
                # Force garbage collection after each video
                gc.collect()

        batch_duration_ms = (time.time() - batch_start) * 1000
        batch_result = BatchResult(
            results=results,
            total_duration_ms=batch_duration_ms
        )

        self.logger.info(
            f"Batch complete for {brand_config.slug}",
            extra={
                "success_count": batch_result.success_count,
                "failure_count": batch_result.failure_count,
                "total_duration_ms": batch_duration_ms,
                "success_rate": f"{batch_result.success_rate:.1%}"
            }
        )

        return batch_result

    def generate_for_brands(
        self,
        brand_slugs: List[str],
        count_per_brand: int = 1,
        upload: bool = True,
    ) -> Dict[str, BatchResult]:
        """Generate videos for multiple brands.

        Loads each brand config and generates videos. A failure in one brand
        does not affect processing of other brands.

        Args:
            brand_slugs: List of brand slugs to process
            count_per_brand: Number of videos per brand
            upload: Whether to upload videos to storage

        Returns:
            Dictionary mapping brand slug to BatchResult
        """
        self.logger.info(
            f"Starting multi-brand generation",
            extra={
                "brands": brand_slugs,
                "count_per_brand": count_per_brand
            }
        )

        loader = BrandLoader()
        results: Dict[str, BatchResult] = {}

        for slug in brand_slugs:
            try:
                self.logger.info(f"Loading brand config for {slug}")
                brand_config = loader.load(slug)
                batch_result = self.generate_batch(
                    brand_config,
                    count=count_per_brand,
                    upload=upload
                )
                results[slug] = batch_result

            except Exception as e:
                self.logger.error(
                    f"Failed to process brand {slug}: {e}",
                    exc_info=True
                )
                # Record failed brand with empty BatchResult
                results[slug] = BatchResult(
                    results=[GenerationResult(success=False, error=str(e))],
                    total_duration_ms=0.0
                )

        # Log summary
        total_success = sum(r.success_count for r in results.values())
        total_failure = sum(r.failure_count for r in results.values())
        self.logger.info(
            f"Multi-brand generation complete",
            extra={
                "brands_processed": len(results),
                "total_success": total_success,
                "total_failure": total_failure
            }
        )

        return results
