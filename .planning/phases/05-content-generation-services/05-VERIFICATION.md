---
phase: 05-content-generation-services
verified: 2026-01-24T05:30:00Z
status: gaps_found
score: 4/5 must-haves verified
gaps:
  - truth: "Generated content adapts to brand voice and tone (wellness/deals/fitness distinct)"
    status: partial
    reason: "BRAND_VOICES dictionaries use short slugs (menopause) but YAML configs use full slugs (menopause-planner)"
    artifacts:
      - path: "src/services/script_generator.py"
        issue: "BRAND_VOICES keys don't match actual brand slugs from YAML"
      - path: "src/clients/tts.py"
        issue: "BRAND_VOICES keys don't match actual brand slugs - for_brand() falls back to DEFAULT_VOICE"
    missing:
      - "Update BRAND_VOICES keys in script_generator.py to match YAML slugs: menopause-planner, daily-deal-darling, fitness-made-easy"
      - "Update BRAND_VOICES keys in tts.py to match YAML slugs"
      - "OR: Normalize slug before lookup (strip suffix, replace hyphens with underscores)"
---

# Phase 5: Content Generation Services Verification Report

**Phase Goal:** Script, video, and audio generation services with file-based caching to prevent quota exhaustion
**Verified:** 2026-01-24T05:30:00Z
**Status:** gaps_found
**Re-verification:** No - initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | ScriptGenerator creates brand-appropriate topics and voiceover scripts with CTAs naturally integrated | VERIFIED | `src/services/script_generator.py` (263 lines) uses GeminiClient with prompts that include CTA from brand_config, parses VOICEOVER/SEARCH_TERMS from response |
| 2 | VideoFetcher retrieves Pexels videos matching script topics and caches by search term hash | VERIFIED | `src/services/video_fetcher.py` (226 lines) uses PexelsClient, caches with sorted term hash keys, validates cached files exist |
| 3 | AudioSynthesizer generates TTS audio with brand-specific voices and caches by script hash | VERIFIED | `src/services/audio_synthesizer.py` (195 lines) uses TTSClient, caches with voice+text hash, includes word timings |
| 4 | Cache hit prevents API call (verified by monitoring API request logs) | VERIFIED | All three services check cache.get() before API calls: script_generator.py:216, video_fetcher.py:105, audio_synthesizer.py:110 |
| 5 | Generated content adapts to brand voice and tone (wellness/deals/fitness distinct) | PARTIAL | BRAND_VOICES dictionaries use wrong slug format - lookups fall back to DEFAULT_VOICE |

**Score:** 4/5 truths verified (1 partial)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/models/content.py` | Script, AudioResult, GeneratedContent dataclasses | VERIFIED | 172 lines, all 3 dataclasses with to_dict/from_dict, imports WordTiming |
| `src/utils/cache.py` | FileCache class with get/set/has methods | VERIFIED | 177 lines, SHA256 hash keys, version prefix, error handling |
| `src/services/script_generator.py` | ScriptGenerator with brand prompts | VERIFIED | 263 lines, BRAND_VOICES dict, cache integration, Gemini prompts |
| `src/services/video_fetcher.py` | VideoFetcher with Pexels caching | VERIFIED | 226 lines, metadata cache, duration matching, search term fallback |
| `src/services/audio_synthesizer.py` | AudioSynthesizer with TTS caching | VERIFIED | 195 lines, word timings, voice-based cache key |
| `src/services/__init__.py` | Exports all services | VERIFIED | Exports ScriptGenerator, VideoFetcher, AudioSynthesizer |
| `src/models/__init__.py` | Exports content models | VERIFIED | Exports Script, AudioResult, GeneratedContent |
| `src/utils/__init__.py` | Exports FileCache | VERIFIED | Exports FileCache |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| ScriptGenerator | GeminiClient | `self.client.generate_text()` | WIRED | Lines 234-235, 244-246 call generate_text with prompts |
| ScriptGenerator | FileCache | `self.cache.get/set()` | WIRED | Line 63 creates cache, lines 216, 252 use it |
| ScriptGenerator | Script | Returns Script dataclass | WIRED | Line 182-189 creates Script, line 261 returns it |
| VideoFetcher | PexelsClient | `self.client.search_videos/download_video()` | WIRED | Lines 149, 183 call client methods |
| VideoFetcher | FileCache | `self.metadata_cache.get/set/delete()` | WIRED | Lines 52, 65, 186 use metadata cache |
| AudioSynthesizer | TTSClient | `TTSClient.for_brand().generate()` | WIRED | Lines 124, 128 create client and generate |
| AudioSynthesizer | FileCache | `self.metadata_cache.get/set/delete()` | WIRED | Lines 51, 58, 138 use metadata cache |
| AudioSynthesizer | AudioResult | Returns AudioResult | WIRED | Lines 131-135 create and return AudioResult |
| content.py | WordTiming | `from src.video.timing import WordTiming` | WIRED | Line 11 imports, AudioResult.word_timings uses it |

### Requirements Coverage

| Requirement | Status | Blocking Issue |
|-------------|--------|----------------|
| SCRIPT-01: System generates brand-appropriate topic for each video | SATISFIED | Topics generated via _build_topic_prompt |
| SCRIPT-02: System generates voiceover script with CTA naturally integrated | SATISFIED | _build_script_prompt includes CTA instructions |
| SCRIPT-03: System generates Pexels search terms matching the script content | SATISFIED | _parse_response extracts SEARCH_TERMS section |
| SCRIPT-04: Script adapts to brand voice (wellness/deals/fitness tone) | BLOCKED | BRAND_VOICES slug mismatch causes fallback to DEFAULT_VOICE |
| VIDEO-01: System fetches stock video from Pexels API matching search terms | SATISFIED | VideoFetcher.fetch() takes search_terms list |
| VIDEO-02: System handles multiple aspect ratios | N/A | Handled by Phase 3 compositor, not this phase |
| VIDEO-03: System selects video length appropriate for script duration | SATISFIED | Duration bounds 0.8x-1.5x target in fetch() |
| AUDIO-01: System generates voiceover audio from script using Edge-TTS | SATISFIED | AudioSynthesizer uses TTSClient |
| AUDIO-02: System uses brand-specific TTS voice for each brand | BLOCKED | TTSClient.for_brand() falls back to DEFAULT_VOICE |
| AUDIO-03: Voiceover speaks CTA naturally within the script | SATISFIED | CTA is part of voiceover text, not TTS issue |
| STOR-02: System can output videos locally without upload | N/A | Upload is Phase 6 |
| STOR-03: System logs metadata per video | SATISFIED | All services log metadata via logger.info extra={} |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| None found | - | - | - | - |

No TODO, FIXME, placeholder patterns, empty returns, or console.log found in service files.

### Human Verification Required

### 1. Cache Hit Behavior
**Test:** Run ScriptGenerator.generate() twice with same brand and seed
**Expected:** Second call returns immediately without Gemini API call (check logs for "Cache HIT")
**Why human:** Requires running code with API keys configured

### 2. Brand Voice Prompts
**Test:** Generate script for each brand and compare prompt tone
**Expected:** Menopause uses "warm/supportive", Daily Deal uses "excited/enthusiastic", Fitness uses "motivational/energetic"
**Why human:** Current code falls back to DEFAULT_VOICE; need to verify after fix

### 3. VideoFetcher Duration Matching
**Test:** Fetch video with 30s target, verify returned video is 24-45s
**Expected:** Video duration within 0.8x-1.5x range
**Why human:** Requires Pexels API call with valid key

### Gaps Summary

**One gap found affecting brand voice adaptation:**

The BRAND_VOICES dictionaries in both `src/services/script_generator.py` and `src/clients/tts.py` use short slugs (`menopause`, `daily_deal`, `fitness`) but the actual brand YAML configs define slugs as `menopause-planner`, `daily-deal-darling`, `fitness-made-easy`.

When the services look up brand voice configuration using `brand_config.slug`, the lookup fails and falls back to DEFAULT_VOICE/DEFAULT_VOICE. This means:

1. **Script prompts** will use generic "friendly and informative" tone instead of brand-specific tones (warm/supportive for wellness, excited for deals, motivational for fitness)

2. **TTS voices** will all use `en-US-AriaNeural` instead of brand-specific voices (`JennyNeural` for menopause, `SaraNeural` for fitness)

**Fix required:** Update BRAND_VOICES keys to match YAML slugs, or add slug normalization logic.

**Note:** The AudioSynthesizer partially works because it uses `brand_config.tts_voice` directly for the cache key, so the correct voice IS in the cache key. However, TTSClient.for_brand() still does its own lookup which fails.

---

*Verified: 2026-01-24T05:30:00Z*
*Verifier: Claude (gsd-verifier)*
