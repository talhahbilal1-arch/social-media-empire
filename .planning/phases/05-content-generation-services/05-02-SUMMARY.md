---
phase: 05-content-generation-services
plan: 02
subsystem: content-generation
tags: [gemini, script, voiceover, caching, brand-voice]

dependency-graph:
  requires: ["05-01"]
  provides: ["ScriptGenerator service", "brand-specific prompts", "script caching"]
  affects: ["05-04", "06-01", "07-01"]

tech-stack:
  added: []
  patterns: ["service class pattern", "file-based caching", "prompt templates"]

key-files:
  created:
    - src/services/script_generator.py
  modified:
    - src/services/__init__.py

decisions:
  - key: "brand-voice-dict"
    choice: "Class-level BRAND_VOICES dict"
    why: "Easy lookup by brand slug, clear voice definitions"
  - key: "cache-key-format"
    choice: "brand_slug + topic_seed + date"
    why: "Daily freshness while allowing same-day reruns"
  - key: "parsing-format"
    choice: "VOICEOVER/SEARCH_TERMS markers"
    why: "Simple regex-free parsing, clear Gemini instructions"
  - key: "fallback-search-terms"
    choice: "['lifestyle', 'nature', 'wellness']"
    why: "Generic terms that work across brands when parsing fails"

metrics:
  duration: 116s
  completed: 2026-01-24
---

# Phase 05 Plan 02: Script Generator Summary

ScriptGenerator service with brand-specific Gemini prompts and file-based caching for quota protection.

## What Was Built

### ScriptGenerator Class

Created `src/services/script_generator.py` with:

**Brand Voice Configuration:**
- `BRAND_VOICES` dict with menopause (warm/supportive), daily_deal (excited/enthusiastic), fitness (motivational/energetic)
- `DEFAULT_VOICE` fallback for unknown brands (friendly/informative)

**Prompt Building:**
- `_build_topic_prompt()`: Generates engaging video topic based on brand context
- `_build_script_prompt()`: Creates voiceover script with CTA naturally integrated, includes Pexels search terms request

**Caching Strategy:**
- Cache key: `{brand_slug}_{topic_seed}_{date.today()}`
- Daily freshness (date in key) while allowing same-day reruns
- Uses FileCache("scripts") from 05-01

**Response Parsing:**
- Parses VOICEOVER: and SEARCH_TERMS: sections from Gemini response
- Fallback to ["lifestyle", "nature", "wellness"] when parsing fails
- Returns Script dataclass with all required fields

## Key Implementation Details

```python
# Brand voice lookup
voice = self.BRAND_VOICES.get(brand_config.slug, self.DEFAULT_VOICE)

# Word count calculation: ~150 words/min = 2.5 words/sec
word_count = int(target_duration * 2.5)  # 35 sec = 87 words max

# Cache-first pattern
cached = self.cache.get(cache_key)
if cached:
    return Script.from_dict(cached)
```

## Integration Points

| Component | How Used |
|-----------|----------|
| GeminiClient | generate_text() for topic and script |
| FileCache | get/set for script caching |
| Script | Dataclass for structured output |
| BrandConfig | Brand name, slug, CTA info |

## Tasks Completed

| Task | Description | Commit |
|------|-------------|--------|
| 1 | Create ScriptGenerator with brand-specific prompts | e9f624f |
| 2 | Implement generate method with caching | 91e23e7 |

## Verification Results

- ScriptGenerator importable from src.services
- All brand voices configured (menopause, daily_deal, fitness)
- Response parsing works with VOICEOVER/SEARCH_TERMS format
- Fallback search terms work when parsing fails
- File has 262 lines (exceeds 100 minimum)

## Deviations from Plan

None - plan executed exactly as written.

## Next Phase Readiness

**For 05-03 (VideoFetcher):** ScriptGenerator.generate() returns Script with search_terms ready for Pexels queries.

**For 05-04 (AudioSynthesizer):** Script.voiceover contains the text to synthesize.

**For orchestrator:** ScriptGenerator is the first step in content pipeline: Script -> Video -> Audio -> Composite.
