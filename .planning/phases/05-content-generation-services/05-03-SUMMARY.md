---
phase: 05-content-generation-services
plan: 03
subsystem: content-services
tags: [pexels, video, caching, stock-footage]
depends_on:
  requires: [05-01]
  provides: [VideoFetcher service with Pexels integration and caching]
  affects: [06-pipeline-orchestration]
tech-stack:
  added: []
  patterns: [cache-key-generation, search-term-fallback, duration-matching]
key-files:
  created:
    - src/services/video_fetcher.py
  modified:
    - src/services/__init__.py
decisions:
  - "Order-independent cache keys via sorted search terms"
  - "Duration bounds: 0.8x to 1.5x target duration for flexibility"
  - "Landscape orientation preferred for 9:16 vertical cropping"
  - "Cache invalidation when file missing despite metadata entry"
metrics:
  duration: 103s
  completed: 2026-01-24
---

# Phase 05 Plan 03: VideoFetcher Service Summary

**One-liner:** VideoFetcher with Pexels search, duration matching, and file-based caching using sorted search term keys.

## What Was Built

### VideoFetcher Service (`src/services/video_fetcher.py`)

A service that wraps PexelsClient with intelligent caching and search term handling:

```python
class VideoFetcher:
    def fetch(
        self,
        search_terms: List[str],
        target_duration: float = 30.0,
        min_height: int = None
    ) -> Path:
        """Fetch video matching search terms with appropriate duration."""
```

**Key features:**
- **Cache-first strategy**: Checks metadata cache before any API calls
- **Order-independent cache keys**: `["nature", "wellness"]` and `["wellness", "nature"]` produce same key
- **Duration matching**: Searches for videos in 0.8x to 1.5x target duration range
- **Search term fallback**: Tries each term in order until success
- **Landscape preference**: Requests landscape orientation for better 9:16 cropping
- **Cache invalidation**: Automatically clears stale entries when video files missing

**Cache architecture:**
- Metadata cache: `FileCache("video_metadata")` stores video ID, path, duration, search terms
- Video files: Stored in `cache/videos/` directory as `pexels_{id}.mp4`
- Cache key: sorted terms joined with underscore (e.g., `nature_wellness`)

## Implementation Details

### Cache Key Generation
```python
def _cache_key(self, search_terms: List[str]) -> str:
    sorted_terms = sorted([t.lower().strip() for t in search_terms])
    return "_".join(sorted_terms)
```

### Duration Bounds Calculation
```python
min_duration = max(10, int(target_duration * 0.8))  # At least 10s
max_duration = min(60, int(target_duration * 1.5))  # At most 60s
```

For a 30s target: searches 24-45s videos. This flexibility ensures good matches while keeping videos appropriate length.

### Video Selection Criteria
1. Duration within calculated bounds
2. Landscape orientation (better for vertical cropping)
3. At least 720p height for quality
4. First video with suitable file selected

## Commits

| Hash | Type | Description |
|------|------|-------------|
| 8d7d96d | feat | Create VideoFetcher with Pexels integration and caching |
| 59ae79d | feat | Export VideoFetcher from services package |

## Files Changed

| File | Change | Lines |
|------|--------|-------|
| `src/services/video_fetcher.py` | Created | 225 |
| `src/services/__init__.py` | Modified | +2 |

## Verification Results

- VideoFetcher imports successfully
- Cache key order independence verified
- Duration bounds calculation correct (30s target -> 24-45s range)
- All required methods present: fetch, _search_and_select, _download_and_cache, clear_cache

## Deviations from Plan

None - plan executed exactly as written.

## Dependencies

### Uses
- `src/clients/pexels.py`: PexelsClient, PexelsVideo for API access
- `src/utils/cache.py`: FileCache for metadata persistence

### Provides
- `VideoFetcher` class for pipeline orchestration
- Caching layer preventing redundant Pexels API calls

## Next Phase Readiness

VideoFetcher is ready for integration in Phase 06 pipeline:
- Accepts search terms from script generation
- Returns video path for composition
- Caching reduces API calls in production

**Integration pattern:**
```python
fetcher = VideoFetcher()
video_path = fetcher.fetch(
    search_terms=["nature", "wellness", "meditation"],
    target_duration=script.estimated_duration
)
```
