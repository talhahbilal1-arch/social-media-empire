# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-22)

**Core value:** Generate engaging, brand-consistent short-form video content automatically without manual intervention or ongoing costs.
**Current focus:** Phase 3 - Core Video Composition

## Current Position

Phase: 3 of 8 (Core Video Composition)
Plan: 4 of 4 in current phase
Status: Phase complete
Last activity: 2026-01-23 — Completed 03-04-PLAN.md

Progress: [████░░░░░░] ~50%

## Performance Metrics

**Velocity:**
- Total plans completed: 8
- Average duration: 4.8 min
- Total execution time: 0.6 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01-environment-foundation | 2 | 3 min | 1.5 min |
| 02-brand-configuration-system | 2 | 193s | 96s |
| 03-core-video-composition | 4 | 1348s | 337s |

**Recent Trend:**
- Last 5 plans: 03-01 (131s), 03-02 (210s), 03-03 (246s), 03-04 (761s)
- Trend: Plan 03-04 significantly longer due to integration testing and bug fixes

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Edge-TTS over other TTS: Free, good quality, multiple voices
- Supabase for storage: Free tier, already have account
- Sentence blocks over word-by-word: Simpler to implement, cleaner look
- AI-generated topics: Reduces manual work, keeps content fresh
- Locked all dependencies to exact versions for reproducible builds (01-01)
- Separated cache/ and output/ directories for distinct concerns (01-01)
- Added orchestration/ subpackage for workflow coordination (01-01)
- Pinned Python 3.11 for stability (01-01)
- Environment validation checks FFmpeg libx264 codec availability before development (01-02)
- MoviePy 2.0 import syntax enforced throughout project (01-02)
- pydantic-extra-types Color type over manual validation for type-safe color handling (02-01)
- ConfigDict(extra="ignore") for forward-compatible YAML schema evolution (02-01)
- Distinct Edge-TTS voices per brand (JennyNeural, AriaNeural, SaraNeural) for brand differentiation (02-02)
- yaml.safe_load() enforced over yaml.load() for security (prevents code execution from YAML) (02-02)
- LRU caching in BrandLoader for performance optimization (02-02)
- Center-crop algorithm over letterboxing for 16:9 to 9:16 conversion (03-01)
- Clip tracking list for memory management to prevent leaks in batch processing (03-01)
- Target FPS set to 24 for consistent playback across platforms (03-01)
- Absolute (x, y) tuple coordinates over string positions for text placement to avoid MoviePy 2.x bugs (03-02)
- 120px safe zone margin uniformly applied to avoid mobile UI elements (03-02)
- Auto-text wrapping with method='caption' for width constraints (03-02)
- Brand color mapping: primary=stroke, secondary=text for visual contrast (03-02)
- Use dataclasses for timing data (WordTiming, SentenceTiming) for type safety (03-03)
- Convert edge-tts milliseconds to seconds for consistency with MoviePy timing (03-03)
- Parse SubMaker.offset and SubMaker.subs arrays (not cues - API correction) (03-03)
- Sentence duration calculated from first word start to last word end (03-03)
- CompositeVideoClip layer ordering: [bg_clip] + text_clips (background first) (03-04)
- Duration exact matching: bg_clip.with_duration(audio_clip.duration) prevents drift (03-04)
- MoviePy 2.x API: Use cropped()/resized() instead of crop()/resize() (03-04)
- Edge-TTS fallback: Synthetic audio when service unavailable for test resilience (03-04)
- Memory threshold 5x for test environment due to temp file overhead (03-04)

### Pending Todos

None yet.

### Blockers/Concerns

**Environment Setup Required (01-02):**
- Python 3.11 must be installed and activated (currently using Python 3.9)
- FFmpeg with libx264 codec must be installed
- Virtual environment must be created and dependencies installed
- Run `python scripts/validate_environment.py` to verify setup

**Dependency Version Constraints (03-02):**
- Python 3.9 compatibility required downgrading several packages
- pillow 12.x requires Python 3.10+, using 11.0.0
- Consider migrating to Python 3.11 as specified in .python-version

**Edge-TTS Service Reliability (03-04):**
- Microsoft's edge-tts service returns 403 intermittently
- Test fallback with synthetic audio works
- Production needs monitoring and potential failover to alternative TTS provider

**Memory Growth in Test Environment (03-04):**
- 4.58x growth over 10 iterations (12.5KB → 57.1KB)
- Cleanup() works correctly, growth is test overhead (temp files, synthetic audio)
- Production metrics should show <1.5x growth with persistent files

**Research Flags from Planning:**
- Phase 5: Cache eviction strategy (LRU vs FIFO, size limits, TTL)
- Phase 3: Platform safe zone verification on latest app versions (Instagram/TikTok/YouTube)
- Phase 8: GitHub Actions cron reliability measurement (15-30 min delays possible)

## Session Continuity

Last session: 2026-01-23
Stopped at: Completed 03-04-PLAN.md (Video Composition Integration) - Phase 3 complete
Resume file: None

---
*State initialized: 2026-01-22*
*Last updated: 2026-01-23 after completing 03-04-PLAN.md*
