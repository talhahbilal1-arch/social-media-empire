---
phase: 03-core-video-composition
plan: 03
subsystem: video-processing
tags: [edge-tts, audio-sync, timing, word-boundaries, sentence-blocks]

# Dependency graph
requires:
  - phase: 03-core-video-composition
    plan: 01
    provides: VideoCompositor infrastructure
provides:
  - Audio-text synchronization utilities for text overlays
  - WordTiming and SentenceTiming data structures
  - extract_word_timings function to parse edge-tts SubMaker
  - group_words_into_sentences function to aggregate word timings into sentence blocks
affects: [04-text-overlay-system, 06-video-pipeline]

# Tech tracking
tech-stack:
  added: [edge-tts 6.1.18]
  patterns: [dataclass-based timing models, millisecond to second conversion, word-to-sentence aggregation]

key-files:
  created:
    - src/video/timing.py
  modified: []

key-decisions:
  - "Use dataclasses for timing data (WordTiming, SentenceTiming) for type safety"
  - "Convert edge-tts milliseconds to seconds for consistency with MoviePy timing"
  - "Parse SubMaker.offset and SubMaker.subs arrays (not cues - API correction)"
  - "Sentence duration calculated from first word start to last word end"
  - "Handle word count mismatches gracefully by using available words"

patterns-established:
  - "Pattern 1: Timing data structures expose both raw values and computed properties (duration, end)"
  - "Pattern 2: Extract timing from TTS provider, then transform to higher-level blocks"
  - "Pattern 3: Sentence grouping uses word count matching to align timing with script"

# Metrics
duration: 4min
completed: 2026-01-23
---

# Phase 03 Plan 03: Audio-Text Synchronization Summary

**Audio-text synchronization utilities extracting edge-tts word boundaries and grouping into sentence-level timing blocks for text overlays**

## Performance

- **Duration:** 4 min 6 sec
- **Started:** 2026-01-23T15:00:16Z
- **Completed:** 2026-01-23T15:04:22Z
- **Tasks:** 3
- **Files created:** 1

## Accomplishments
- Created timing module with WordTiming and SentenceTiming dataclasses
- Implemented extract_word_timings to parse edge-tts SubMaker (subs and offset arrays)
- Implemented group_words_into_sentences to aggregate word timings into sentence blocks
- Converted timing from milliseconds to seconds for MoviePy compatibility
- Added proper edge case handling for word count mismatches

## Task Commits

Each task was committed atomically:

1. **Task 1: Create timing module with data structures** - `d7acf09` (feat)
2. **Task 2: Implement extract_word_timings function** - `d480b29` (feat)
3. **Task 3: Implement group_words_into_sentences function** - `4fca2f2` (feat)

## Files Created/Modified
- `src/video/timing.py` - Audio-text synchronization utilities (114 lines)

## Decisions Made

**Dataclass-based timing models:**
- WordTiming stores text, start, end with computed duration property
- SentenceTiming stores text, start, duration with computed end property
- Type-safe data structures prevent timing calculation errors
- Properties provide convenient access to computed values

**Edge-tts API integration:**
- Corrected plan assumption: SubMaker uses `subs` and `offset`, not `cues`
- SubMaker.subs contains word strings, SubMaker.offset contains (start_ms, end_ms) tuples
- Convert milliseconds to seconds using division by 1000.0
- Zip subs and offset arrays to construct WordTiming objects

**Sentence grouping algorithm:**
- Split sentences by whitespace to count words
- Consume word timings sequentially based on word count
- Calculate sentence start from first word's start time
- Calculate sentence duration from first word start to last word end
- Handle edge cases where word counts don't match perfectly (use available words)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Missing edge-tts dependency**
- **Found during:** Task 1 verification
- **Issue:** edge_tts module not installed, blocking import verification
- **Fix:** Installed edge-tts==6.1.18 from requirements.txt
- **Files modified:** None (system-level dependency install)
- **Commit:** N/A (not code change)

**2. [Rule 3 - Blocking] Missing moviepy dependency**
- **Found during:** Task 1 verification (indirect import)
- **Issue:** moviepy module not installed, blocking src.video imports
- **Fix:** Installed moviepy and Pillow dependencies
- **Files modified:** None (system-level dependency install)
- **Commit:** N/A (not code change)

**3. [Rule 1 - Bug] Incorrect SubMaker API usage**
- **Found during:** Task 2 implementation
- **Issue:** Plan specified `submaker.cues` but actual API uses `submaker.subs` and `submaker.offset`
- **Fix:** Corrected to use SubMaker.subs (word strings) and SubMaker.offset (timing tuples)
- **Files modified:** src/video/timing.py
- **Commit:** d480b29 (included in Task 2 commit)

## Issues Encountered

**Edge-tts SubMaker API mismatch:**
- **Issue:** Plan documentation referenced `cues` attribute that doesn't exist in edge-tts 6.1.18
- **Resolution:** Inspected SubMaker source code to identify correct attributes (subs, offset)
- **Impact:** Required implementation correction but no design changes
- **Learning:** SubMaker stores words in `subs` list and timing in `offset` list of (start_ms, end_ms) tuples

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

**Ready for next phase:**
- Timing utilities are fully functional and tested
- Word-level timing extraction works with edge-tts SubMaker
- Sentence-level timing aggregation handles edge cases gracefully
- All timing data converted to seconds for MoviePy compatibility

**For upcoming phases:**
- Phase 04 (Text Overlay System) can use SentenceTiming to sync text overlays with audio
- Phase 05 (Audio Integration) can use timing data to coordinate TTS audio with text display
- Phase 06 (Video Pipeline) can orchestrate timing-based text overlay placement

**No blockers or concerns.**

---
*Phase: 03-core-video-composition*
*Completed: 2026-01-23*
