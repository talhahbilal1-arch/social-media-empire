# Project Research Summary

**Project:** Social Media Empire (Automated Vertical Video Generation)
**Domain:** Automated short-form video generation for social media platforms
**Researched:** 2026-01-22
**Confidence:** HIGH

## Executive Summary

This project is an automated vertical video pipeline for Pinterest Idea Pins and YouTube Shorts. The standard approach in 2026 is a Python-based service layer architecture using MoviePy for video compositing, LLM-driven script generation, and free-tier APIs for stock content. Experts prioritize zero-cost operation through strategic API selection (Gemini, Edge-TTS, Pexels free tiers), CLI-first interfaces for automation, and scheduled GitHub Actions workflows to eliminate server costs.

The recommended architecture follows a pipeline orchestrator pattern: CLI → VideoGenerator → Service Layer (ScriptGenerator, VideoFetcher, AudioSynthesizer, VideoComposer, UploadService) → API Clients (Gemini, Pexels, Edge-TTS, Supabase). Configuration-as-code enables multi-brand support without code changes. Python 3.11 with MoviePy 2.2.1+ provides the best balance of library compatibility and stability, avoiding both Python 3.12 issues and deprecated MoviePy 1.x.

Critical risks center on memory management, API rate limits, and audio-video synchronization. MoviePy has known memory leaks with VideoFileClip concatenation requiring explicit cleanup (`.close()`, `gc.collect()`). Audio-video sync drift occurs without explicit FPS control (always set `fps=30` throughout pipeline). API integrations need caching layers (Pexels quota exhaustion, Edge-TTS rate limiting) and exponential backoff (Gemini 429 errors). Vertical video safe zones must account for platform UI overlays, with text positioned 120px from all edges and tested on actual devices.

## Key Findings

### Recommended Stack

Python 3.11 is the optimal runtime environment, providing broad compatibility across all dependencies while avoiding Python 3.12 issues with MoviePy. The stack leverages free-tier APIs exclusively to achieve zero-cost operation at 2x daily generation rates.

**Core technologies:**
- **MoviePy 2.2.1+**: Video compositing engine — v2.0+ eliminates ImageMagick dependency using pure Pillow, critical for CI/CD reliability. Supports text overlays, audio compositing, transitions.
- **Google GenAI SDK 1.60.0+**: AI script generation — unified SDK replacing deprecated google-generativeai. Free tier provides 15 requests/minute, sufficient for scheduled automation.
- **Edge-TTS 7.2.7+**: Text-to-speech — free neural TTS via Microsoft Edge service, no API key required. Supports multiple voices/languages and generates subtitle files.
- **Pexels API**: Stock video retrieval — free tier provides 200 requests/hour with commercial use rights. High-quality vertical videos for background footage.
- **Supabase 2.27.2+**: Video storage & hosting — free tier with CDN delivery. Simpler developer experience than S3 for small-scale projects.
- **FFmpeg**: Video processing backend — required by MoviePy. Must explicitly install in GitHub Actions using marketplace actions (FedericoCarboni/setup-ffmpeg@v3).

**Critical version notes:**
- Avoid MoviePy 1.x (deprecated, ImageMagick issues), Python 3.12+ (MoviePy compatibility issues), google-generativeai SDK (officially deprecated Nov 2025)
- Pin MoviePy to `>=2.0.0,<3.0.0` to ensure v2.x API consistency
- Use NumPy `<2.0` if encountering MoviePy import errors (v2.x compatibility issues reported)

### Expected Features

Research identifies clear table stakes versus differentiators in the automated video generation landscape of 2026.

**Must have (table stakes):**
- AI script generation — core automation value, expected in all text-to-video platforms by 2026
- Stock video backgrounds — essential for vertical format, Pexels provides free commercial-use content
- Text-to-speech voiceover — 78% of Shorts use audio, auto-voiceover is standard
- Text overlays synced to audio — accessibility and engagement requirement on all platforms
- Vertical format 1080x1920 (9:16) — non-negotiable for Pinterest Idea Pins and YouTube Shorts
- 15-60 second duration — platform requirements (Pinterest 3-60s, Shorts optimal 15-60s)
- Multi-brand support — core differentiator for 3-brand use case, enables brand-specific tone/topics
- Cloud storage upload — videos must be accessible for manual posting

**Should have (competitive advantage):**
- CLI-first interface — developer-friendly, scriptable, version-controllable (rare among GUI competitors)
- GitHub Actions automation — free scheduled generation without servers (2000 min/month free tier)
- Batch generation — generate multiple videos per command (--count flag), enables content stockpiling
- Brand-aware content — AI understands brand voice and avoids off-brand topics
- Zero-cost operation — free APIs eliminate per-video costs ($0.01-$0.50/sec for premium AI video)
- Local generation option — no vendor lock-in, can test locally before CI/CD deployment
- Transparent pipeline — each step visible and debuggable (vs black-box GUI platforms)

**Defer (v2+):**
- Direct platform posting — Pinterest/YouTube APIs create OAuth complexity and ban risk, manual posting safer
- Custom AI video generation — Runway/Kling costs $0.60-$30 per 60s video, destroys zero-cost model
- Multi-language support — 10x complexity increase, launch English-only and add based on demand
- Music background tracks — copyright/licensing complexity, defer until voiceover-only proves limiting
- Advanced analytics — defer until posting automation exists

### Architecture Approach

The architecture follows a service layer pattern with clear separation of concerns. A thin CLI interface routes commands to a VideoGenerator orchestrator, which coordinates five domain services (ScriptGenerator, VideoFetcher, AudioSynthesizer, VideoComposer, UploadService) operating on shared domain models (Brand, Script, VideoSpec). Each service wraps thin API clients providing consistent error handling and retry logic. This stateless design requires no database—all state lives in config files (brands) or Supabase (uploaded videos).

**Major components:**
1. **CLI Interface** — argument parsing (argparse/click), brand config loading, command routing to orchestrator
2. **VideoGenerator (Orchestrator)** — pipeline coordination: script → video → audio → composite → upload, error handling, temp file cleanup
3. **Service Layer** — ScriptGenerator (Gemini), VideoFetcher (Pexels), AudioSynthesizer (Edge-TTS), VideoComposer (MoviePy), UploadService (Supabase)
4. **API Clients** — thin wrappers with retry logic, rate limit handling, response parsing
5. **Brand Config System** — YAML files per brand (colors, voice, topics, CTAs) loaded into dataclasses, enabling non-dev brand additions
6. **Temp File Management** — track all intermediate files, cleanup in finally block to avoid disk exhaustion (GitHub Actions 14GB limit)

**Key patterns:**
- Configuration-as-code: brand settings in YAML, loaded to typed dataclasses (enables adding brands without code changes)
- Bottom-up build order: clients → services → orchestrator → CLI (allows layer-by-layer testing)
- Immutable pipeline: MoviePy 2.0 methods return new clips (.with_duration()) rather than mutating in-place

### Critical Pitfalls

Research identified nine critical pitfalls with high impact on automation reliability. Top five by severity:

1. **Memory leaks with VideoFileClip** — MoviePy doesn't fully release memory when closing clips due to reference cycles. Processing 50+ clips can exhaust 8GB RAM. **Prevention:** Explicit `.close()` + `del clip` + `gc.collect()` after each video, process in small batches (10-20 max), monitor memory usage in GitHub Actions. Test with 10 consecutive generations to verify memory returns to baseline.

2. **Audio-video sync drift** — Audio progressively drifts out of sync in concatenated videos, becoming 3-5 seconds off by end of 60s video. **Prevention:** Set explicit `fps=30` on all clips and output, avoid concatenation (use single timeline), use consistent `audio_fps=44100`, test sync at video END not just start. Single background video preferred over concatenated clips.

3. **Vertical video aspect ratio and safe zones** — Stock videos are 16:9 landscape but output must be 9:16 portrait. Improper scaling creates black bars or cropping. Text too close to edges gets obscured by platform UI (Instagram profile pic, TikTok buttons). **Prevention:** Crop landscape source to center square then scale to 1080x1920, keep text 120px from all edges minimum, position in upper-middle third (300-800px from top), test on actual devices with platform apps before deploying.

4. **Pexels API quota exhaustion** — Free tier: 200 requests/hour, 20,000/month. Development testing can exhaust quota quickly. **Prevention:** Implement local video cache with search term hash as key, check cache before API call, request unlimited quota (free but requires approval), use pre-downloaded videos for testing not live API.

5. **Edge-TTS rate limiting** — Undocumented rate limits cause 403 blocks from same IP with too many requests. Voice quality changes unpredictably as Microsoft updates voices. **Prevention:** Implement audio file caching by text hash, add 2-3 second delays between TTS requests, handle 403 with exponential backoff, monitor for voice quality changes, consider Azure Speech API as paid fallback ($4/month).

**Additional critical pitfalls:**
- **ImageMagick dependency** (MoviePy 2.0+ eliminated this, but verify fontconfig installed)
- **Gemini API rate limits** (15 RPM free tier, implement exponential backoff for 429 errors)
- **FFmpeg codec compatibility** (always specify codec='libx264', preset='ultrafast', fps=30)
- **MoviePy 2.0 breaking changes** (pin version, use .with_* methods not .set_* methods)

## Implications for Roadmap

Based on research findings, the recommended phase structure prioritizes foundational validation before automation complexity. Build order follows dependency graph: environment → clients → services → orchestration → automation.

### Phase 1: Environment & Foundation
**Rationale:** Validate Python 3.11 stack compatibility, MoviePy 2.0 setup, and FFmpeg installation before writing pipeline code. Early validation prevents discovering ImageMagick/codec issues after investing in pipeline development.

**Delivers:** Working development environment with verified dependencies, brand config system, project structure.

**Addresses:**
- MoviePy 2.0 breaking changes (Pitfall #9) — pin version, validate imports
- FFmpeg codec compatibility (Pitfall #7) — test libx264 encoding works
- ImageMagick font rendering (Pitfall #2) — verify TextClip can render fonts
- Brand config foundation — YAML files + dataclass loading

**Key tasks:** Install Python 3.11, MoviePy 2.2.1, FFmpeg with libx264 codec. Test simple VideoFileClip → write_videofile flow. Create Brand dataclass and sample YAML configs. Validate TextClip font rendering.

**Research flag:** Standard setup, no additional research needed (well-documented).

---

### Phase 2: Core Video Pipeline
**Rationale:** VideoComposer is the critical path—most complex component with slow iteration cycles due to rendering time. De-risk early by building with hardcoded test data before integrating AI/API dependencies.

**Delivers:** Working video compositing engine: background video + text overlays + audio → vertical MP4 output.

**Addresses:**
- Memory leaks (Pitfall #1) — implement explicit cleanup, test 10 consecutive renders
- Audio-video sync (Pitfall #3) — enforce fps=30, verify sync at 60-second mark
- Vertical aspect ratio (Pitfall #8) — crop 16:9 to 9:16 properly, no black bars
- FFmpeg preset optimization — use preset='ultrafast' for GitHub Actions speed

**Key tasks:** Build VideoComposer service wrapping MoviePy. Implement crop-to-vertical logic. Add text overlay positioning with brand colors. Test memory cleanup (10 consecutive videos). Verify audio sync at 0s, 30s, 60s marks.

**Research flag:** Standard MoviePy patterns, no additional research needed.

---

### Phase 3: API Client Layer
**Rationale:** Build and test API integrations independently before orchestrating pipeline. Enables mocking clients during service layer development.

**Delivers:** Working API clients for Gemini, Pexels, Edge-TTS, Supabase with error handling and retry logic.

**Addresses:**
- Gemini rate limits (Pitfall #6) — implement exponential backoff for 429 errors
- Edge-TTS rate limiting (Pitfall #4) — add request delays, handle 403 errors
- Pexels quota management (Pitfall #5) — monitor X-Ratelimit-Remaining header
- Supabase upload timeouts — use resumable upload for >6MB videos

**Key tasks:** GeminiClient with text generation + rate limit handling. PexelsClient with video search/download + caching skeleton. TTSClient wrapping edge-tts library. SupabaseClient with upload + metadata.

**Research flag:** Standard API integration, no additional research needed.

---

### Phase 4: Service Layer with Caching
**Rationale:** Services implement business logic on top of clients. Caching is critical to avoid quota exhaustion during development—implement from start, not retrofitted later.

**Delivers:** Five services (ScriptGenerator, VideoFetcher, AudioSynthesizer, VideoComposer, UploadService) with file-based caching.

**Addresses:**
- Pexels quota exhaustion (Pitfall #5) — hash search terms, cache downloaded videos
- Edge-TTS rate limiting (Pitfall #4) — hash script text, cache generated audio
- Duplicate API calls — check cache before every API request
- Brand-aware content — ScriptGenerator applies brand tone/topics to prompts

**Key tasks:** Implement file-based cache (hash → file path mapping). VideoFetcher checks cache before Pexels API. AudioSynthesizer checks cache before TTS call. ScriptGenerator builds brand-specific prompts. Verify cache hit avoids API call.

**Research flag:** Needs light research on cache eviction strategies (LRU, size limits).

---

### Phase 5: Pipeline Orchestration
**Rationale:** Wire services together in VideoGenerator, implementing error handling and graceful failures. One video failure shouldn't crash entire batch.

**Delivers:** VideoGenerator coordinating full pipeline with per-video error recovery.

**Addresses:**
- Error recovery (Anti-Pattern #4) — graceful handling, continue on failure
- Temp file cleanup (Anti-Pattern #3) — track all temp files, cleanup in finally block
- Memory management — explicit cleanup between videos in batch generation
- Logging — structured output showing progress through pipeline

**Key tasks:** VideoGenerator coordinates services sequentially. Dependency injection for services. Try-catch per video in batch. Track temp files, cleanup on success/failure. Test batch of 5 videos with one intentional failure.

**Research flag:** Standard orchestration patterns, no additional research needed.

---

### Phase 6: Text Overlay Safe Zones
**Rationale:** Platform-specific UI overlays require precise positioning. Testing on actual devices is mandatory—desktop previews don't show Instagram profile pics or TikTok buttons.

**Delivers:** Platform-aware text positioning that doesn't get obscured by UI elements.

**Addresses:**
- Safe zones (Pitfall #8) — implement 2026 safe zone guidelines per platform
- Text readability — minimum 60pt font, sufficient contrast
- Text-voiceover sync — time overlays to match audio pacing
- UX pitfalls — test on actual mobile devices before deploying

**Key tasks:** Implement safe zone calculations (Instagram 250px top/bottom, TikTok 131px top/367px bottom). Position text 120px from edges minimum. Test overlays on iPhone/Android with Instagram and TikTok apps. Verify text readable on 6" screen.

**Research flag:** Needs research on 2026 platform UI dimensions (may have changed).

---

### Phase 7: CLI Interface & Batch Generation
**Rationale:** Build CLI after orchestrator works locally. Enables testing full pipeline before adding GitHub Actions complexity.

**Delivers:** CLI with --brand, --count flags, batch processing, structured output.

**Addresses:**
- Batch generation (Feature) — --count flag generates N videos per brand
- Multi-brand support (Feature) — --brand flag or "all" for all brands
- Graceful failures — report success/failure counts, don't crash on one failure
- User experience — progress bars, clear success/error messages

**Key tasks:** argparse command parser with --brand and --count flags. Load brand configs from YAML. Call VideoGenerator.generate_batch(). Display progress during generation. Print summary table (success/failed per brand).

**Research flag:** Standard CLI patterns, no additional research needed.

---

### Phase 8: GitHub Actions Automation
**Rationale:** CI/CD is last piece after full pipeline validated locally. Scheduled cron (2x daily) enables hands-off content generation.

**Delivers:** GitHub Actions workflow with 2x daily scheduled runs, secrets management, artifact storage.

**Addresses:**
- GitHub Actions FFmpeg setup (Stack) — use FedericoCarboni/setup-ffmpeg@v3
- Secrets management (Security) — API keys in GitHub Secrets
- Scheduled generation (Feature) — cron triggers 2x daily
- Runtime limits — 6-hour max per job, batch size must fit within limit

**Key tasks:** Create .github/workflows/generate.yml with cron schedule. Add FFmpeg setup step. Configure GitHub Secrets (GEMINI_API_KEY, PEXELS_API_KEY, SUPABASE_URL, SUPABASE_KEY). Test manual workflow dispatch. Verify scheduled run completes successfully.

**Research flag:** Needs light research on GitHub Actions cron reliability (15-30 min delay possible).

---

### Phase Ordering Rationale

**Bottom-up dependency order:** Environment → Clients → Services → Orchestration → CLI → CI/CD. Each phase depends on previous phases working. Cannot test VideoComposer without working environment. Cannot build services without working clients. Cannot orchestrate without working services.

**De-risk critical path early:** Phase 2 (Core Video Pipeline) tackles VideoComposer—the most complex and slow-to-iterate component—before API integrations. Allows identifying MoviePy issues early with hardcoded test data. Parallel development possible after Phase 3 (different developers can work on different services).

**Caching from start:** Phase 4 implements caching before automation to prevent quota exhaustion during development. Retrofitting caching is painful; building it early is trivial.

**Local validation before CI/CD:** Phases 1-7 produce fully functional local CLI. Phase 8 adds GitHub Actions as deployment layer, not core functionality. Enables thorough local testing before CI/CD complexity.

**Safe zone validation on devices:** Phase 6 requires physical device testing—cannot be simulated. Scheduled late enough that core pipeline works, early enough to avoid rebuilding all videos if positioning wrong.

### Research Flags

**Phases needing deeper research during planning:**
- **Phase 4 (Service Layer with Caching):** Cache eviction strategies—when to purge old videos/audio? Size limits? TTL? Research LRU caching patterns for file-based caches.
- **Phase 6 (Text Overlay Safe Zones):** Verify 2026 platform UI dimensions—Instagram/TikTok may have changed safe zones since research sources published. Test on latest app versions.
- **Phase 8 (GitHub Actions Automation):** Research cron reliability and execution delays (sources mention 15-30 min delays possible). Determine if scheduled triggers acceptable or need alternative (AWS Lambda cron).

**Phases with standard patterns (skip research-phase):**
- **Phase 1 (Environment & Foundation):** Standard Python/MoviePy setup, well-documented.
- **Phase 2 (Core Video Pipeline):** MoviePy patterns extensively documented, common use case.
- **Phase 3 (API Client Layer):** Standard REST API integration patterns.
- **Phase 5 (Pipeline Orchestration):** Service layer orchestration is textbook architecture pattern.
- **Phase 7 (CLI Interface & Batch Generation):** Standard Python CLI patterns (argparse well-documented).

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All recommended packages verified via PyPI with version compatibility checks. Python 3.11 validated against all dependency requirements. MoviePy 2.0 breaking changes documented with migration guide. Sources: official PyPI, GitHub repos, official MoviePy docs. |
| Features | HIGH | Feature landscape based on 2026 platform requirements (Pinterest/YouTube Shorts specs), competitor analysis (InVideo, Pictory, Creatomate), and industry trend reports. Table stakes vs differentiators validated across multiple sources. MVP definition aligned with zero-cost constraint. |
| Architecture | HIGH | Service layer architecture is well-established pattern. Project structure based on Python community standards (Architecture Patterns with Python, Clean Architecture). Multi-brand config-as-code validated across multi-tenant patterns. Build order follows standard dependency graphs. |
| Pitfalls | HIGH | All critical pitfalls sourced from GitHub issues with reproducible symptoms and verified workarounds. Memory leak confirmed in MoviePy #96, #1284, #1292. Audio sync drift in #2458, #1167. Safe zone dimensions from 2026 platform documentation. Rate limits from official API docs (Gemini, Pexels). |

**Overall confidence:** HIGH

Research is grounded in official documentation (PyPI, GitHub, platform specs) with community-validated workarounds for known issues. The 2026 timeframe means all sources are current—no deprecated advice. The recommended stack (Python 3.11, MoviePy 2.2.1, free APIs) has been validated by multiple production use cases documented in research sources.

### Gaps to Address

**Cache eviction strategy:** Research identified need for caching but didn't specify eviction policies. During Phase 4 planning, determine:
- Size limits (prevent cache from consuming all disk)
- TTL (time-to-live) for cached videos/audio
- LRU (least recently used) vs FIFO eviction
- How to handle cache misses gracefully

**Platform safe zone verification:** Safe zone dimensions sourced from 2026 guides but platforms update UI frequently. During Phase 6:
- Test on latest Instagram/TikTok/YouTube app versions
- Verify safe zone dimensions match research findings
- Account for potential platform UI changes since research date
- Test on multiple device sizes (iPhone SE to iPhone Pro Max)

**GitHub Actions cron reliability:** Research mentions 15-30 minute execution delays possible for scheduled workflows. During Phase 8:
- Measure actual delay distribution over 1-2 weeks
- Determine if delays acceptable or need alternative scheduler
- Consider fallback to AWS Lambda/GCP Cloud Scheduler if reliability insufficient

**Gemini prompt engineering:** Research confirms Gemini API works for script generation but didn't detail optimal prompt structure. During Phase 4:
- Experiment with prompt templates for brand-appropriate content
- Test techniques to prevent off-brand topics (e.g., menopause tips on fitness channel)
- Validate script output quality and adjust prompts iteratively

**Batch size optimization:** Research warns against >100 video batches due to memory issues, but didn't specify optimal batch size. During Phase 5:
- Empirically test memory usage with batches of 5, 10, 20, 50 videos
- Measure GitHub Actions runner memory consumption (7GB limit)
- Determine sweet spot balancing throughput vs reliability

## Sources

### Stack Research Sources (HIGH confidence)
- MoviePy PyPI (https://pypi.org/project/moviepy/) — Version and dependency information
- MoviePy GitHub (https://github.com/Zulko/moviepy) — Breaking changes and compatibility
- MoviePy Documentation (https://zulko.github.io/moviepy/) — Official API documentation
- Edge-TTS PyPI (https://pypi.org/project/edge-tts/) — Version and Python compatibility
- Google GenAI SDK PyPI (https://pypi.org/project/google-genai/) — Latest unified SDK
- Pillow PyPI (https://pypi.org/project/Pillow/) — Version and Python support
- Supabase Python Client PyPI (https://pypi.org/project/supabase/) — Version compatibility
- Pexels API Documentation (https://www.pexels.com/api/documentation/) — Official API reference
- Setup FFmpeg GitHub Action (https://github.com/marketplace/actions/setup-ffmpeg) — CI/CD integration

### Features Research Sources (HIGH confidence)
- NVIDIA RTX AI Video Generation (https://blogs.nvidia.com/blog/rtx-ai-garage-ces-2026-open-models-video-generation/) — 2026 trends
- Pinterest Pin Size 2026 Guide (https://socialrails.com/blog/pinterest-pin-size-dimensions-guide) — Platform specs
- YouTube Shorts Algorithm 2026 (https://riverside.fm/blog/youtube-shorts-algorithm) — Platform requirements
- Google Veo 3.1 update (https://techcrunch.com/2026/01/13/googles-update-for-veo-3-1-lets-users-create-vertical-videos-through-reference-images/) — Vertical video trends
- MoviePy documentation (https://zulko.github.io/moviepy/) — Technical capabilities

### Architecture Research Sources (HIGH confidence)
- Service Layer Pattern in Python (https://dev.to/alexis_jean/organize-your-code-with-the-service-layer-pattern-a-simple-python-example-2pnn) — Pattern documentation
- Architecture Patterns with Python (https://www.cosmicpython.com/book/appendix_project_structure.html) — Project structure
- FFmpeg with Python in 2026 (https://www.gumlet.com/learn/ffmpeg-python/) — Integration best practices
- MoviePy v2.0 Discussion (https://github.com/Zulko/moviepy/discussions/2241) — Performance considerations

### Pitfalls Research Sources (HIGH confidence)
- MoviePy GitHub Issues (#96, #1284, #1292, #1535) — Memory leak reports with reproductions
- MoviePy GitHub Issues (#2458, #1167) — Audio sync drift with workarounds
- MoviePy Updating to v2.X Guide (https://zulko.github.io/moviepy/getting_started/updating_to_v2.html) — Breaking changes
- Gemini API Rate Limits (https://ai.google.dev/gemini-api/docs/rate-limits) — Official quota documentation
- Pexels API Documentation (https://help.pexels.com/hc/en-us/articles/900006470063-What-steps-can-I-take-to-avoid-hitting-the-rate-limit) — Rate limit guidance
- Instagram Safe Zone Templates 2026 (https://www.jamiesteedman.co.uk/freebies/free-instagram-safe-zone-templates-1080x1920-vertical-for-reels-stories-social-media-videos/) — Platform UI dimensions
- Supabase Upload Restrictions (https://supabase.com/docs/guides/troubleshooting/upload-file-size-restrictions-Y4wQLT) — File size limits

---
*Research completed: 2026-01-22*
*Ready for roadmap: yes*
