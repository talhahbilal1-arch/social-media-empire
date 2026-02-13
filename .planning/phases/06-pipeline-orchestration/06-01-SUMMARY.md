---
phase: "06"
plan: "01"
subsystem: "orchestration"
tags: [orchestration, pipeline, batch-processing, error-handling]
dependency-graph:
  requires: [05-01, 05-02, 05-03, 05-04]
  provides: [video-generation-pipeline, batch-processing, generate-one, generate-batch]
  affects: [07-CLI, 08-automation]
tech-stack:
  added: []
  patterns: [pipeline-orchestration, error-isolation, resource-cleanup, dependency-injection]
key-files:
  created:
    - src/orchestration/video_generator.py
    - tests/test_video_generator.py
  modified:
    - src/orchestration/__init__.py
decisions:
  - key: try-finally-cleanup
    choice: "Compositor cleanup in finally block"
    reason: "Ensures cleanup runs even on exceptions"
  - key: gc-between-videos
    choice: "gc.collect() after each video in batch"
    reason: "Prevents memory accumulation during batch processing"
  - key: lazy-storage-client
    choice: "Create SupabaseClient lazily on first upload"
    reason: "Avoids credential validation errors during testing"
  - key: sentence-split-regex
    choice: "Split on . ! ? followed by space"
    reason: "Keeps punctuation with sentence for natural reading"
metrics:
  duration: "10.4 min"
  tasks-completed: 3
  tests-passed: 23
  completed: "2026-01-24"
---

# Phase 6 Plan 1: Pipeline Orchestration Summary

**One-liner:** VideoGenerator orchestrates script -> video -> audio -> composite -> upload with per-video error isolation and try/finally cleanup

## What Was Built

### VideoGenerator Class (`src/orchestration/video_generator.py`)

Complete pipeline orchestrator that coordinates all Phase 5 services into a working video generation system.

**Key Methods:**

1. **`generate_one(brand_config, topic_seed, upload)`**
   - 6-step pipeline: script -> video -> audio -> timing -> composite -> upload
   - Returns `GenerationResult` with success/failure status, video path, public URL
   - try/finally ensures compositor.cleanup() always runs
   - Logs timing for each step

2. **`generate_batch(brand_config, count, upload)`**
   - Generates multiple videos for a single brand
   - Each video isolated with try/except
   - gc.collect() runs after each video
   - Returns `BatchResult` with success/failure counts

3. **`generate_for_brands(brand_slugs, count_per_brand, upload)`**
   - Processes multiple brands in sequence
   - Loads brand configs via BrandLoader
   - Brand failures don't stop other brands
   - Returns Dict[str, BatchResult]

**Dataclasses:**

```python
@dataclass
class GenerationResult:
    success: bool = False
    video_path: Optional[Path] = None
    public_url: Optional[str] = None
    error: Optional[str] = None
    duration_ms: float = 0.0

@dataclass
class BatchResult:
    results: List[GenerationResult]
    total_duration_ms: float = 0.0

    @property
    def success_count(self) -> int
    @property
    def failure_count(self) -> int
    @property
    def success_rate(self) -> float
```

### Integration Tests (`tests/test_video_generator.py`)

23 tests verifying all Phase 6 success criteria:

- **TestGenerationResult** (3 tests): Dataclass behavior
- **TestBatchResult** (5 tests): Count calculations, success rate
- **TestVideoGeneratorInit** (2 tests): Directory creation, dependency injection
- **TestPipelineCoordination** (2 tests): Execution order, upload skip
- **TestErrorIsolation** (3 tests): Single failure isolation, error capture
- **TestTempFileCleanup** (3 tests): Cleanup on success, failure, early failure
- **TestBatchCompletion** (3 tests): Final counts, gc.collect() calls
- **TestMultiBrandGeneration** (2 tests): Multi-brand processing

## Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Cleanup pattern | try/finally block | Compositor cleanup must run even on exceptions |
| Memory management | gc.collect() after each video | Prevents memory growth in batch processing |
| Storage client | Lazy initialization | Allows testing without credentials |
| Error isolation | try/except per video | One failure doesn't crash batch |
| Sentence splitting | Regex on `. ` `! ` `? ` | Natural punctuation preservation |
| Topic seed | `{index}_{time.time()}` | Unique content per batch video |

## Service Integration Map

```
VideoGenerator
    |
    +-- ScriptGenerator.generate() --> Script
    |       (topic, voiceover, search_terms)
    |
    +-- VideoFetcher.fetch() --> Path
    |       (stock video based on search_terms)
    |
    +-- AudioSynthesizer.synthesize() --> AudioResult
    |       (TTS audio with word timings)
    |
    +-- group_words_into_sentences() --> List[SentenceTiming]
    |       (text overlay timing)
    |
    +-- VideoCompositor.compose_video() --> void
    |       (final MP4 with overlays and audio)
    |
    +-- SupabaseClient.upload() --> UploadResult
            (public URL for distribution)
```

## Verification Results

All success criteria verified:

- [x] VideoGenerator class exists in src/orchestration/video_generator.py (507 lines)
- [x] generate_one() coordinates script -> video -> audio -> composite -> upload
- [x] generate_batch() processes multiple videos with error isolation
- [x] Compositor cleanup() called in finally block (always runs)
- [x] gc.collect() called after each video in batch
- [x] GenerationResult and BatchResult dataclasses with proper fields
- [x] All 23 integration tests pass
- [x] Imports work: `from src.orchestration import VideoGenerator`

## Commits

| Hash | Message |
|------|---------|
| d2313c3 | feat(06-01): create VideoGenerator with generate_one() |
| de777dc | test(06-01): add integration tests for VideoGenerator |

## Deviations from Plan

None - plan executed exactly as written.

## Next Phase Readiness

Phase 6 complete. Ready for:
- **Phase 7 (CLI):** `src/orchestration/video_generator.py` provides the core orchestration that CLI will wrap
- **Phase 8 (Automation):** VideoGenerator.generate_for_brands() is the main entry point for scheduled runs

### Files for Phase 7

```python
# CLI can use:
from src.orchestration import VideoGenerator, GenerationResult, BatchResult

# Main entry points:
generator = VideoGenerator()
result = generator.generate_one(brand_config)  # Single video
batch = generator.generate_batch(brand_config, count=3)  # Batch for brand
results = generator.generate_for_brands(['brand-a', 'brand-b'])  # Multi-brand
```
