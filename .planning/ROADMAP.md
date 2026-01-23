# Roadmap: Social Media Empire

## Overview

This roadmap transforms the social media video automation concept into a production system that generates brand-consistent vertical videos at zero monthly cost. We build from the foundation up: environment validation and brand configuration, then the core video composition engine, followed by AI/API integrations for content generation, pipeline orchestration, CLI interface, and finally GitHub Actions automation for hands-free operation.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Environment & Foundation** - Setup Python 3.11, MoviePy 2.0, FFmpeg, project structure
- [x] **Phase 2: Brand Configuration System** - Three brand configs with colors, voices, CTAs in YAML
- [x] **Phase 3: Core Video Composition** - MoviePy pipeline: background + text overlays + audio → vertical MP4
- [x] **Phase 4: API Client Layer** - Gemini, Pexels, Edge-TTS, Supabase clients with retry logic
- [ ] **Phase 5: Content Generation Services** - Script, Video, Audio services with file-based caching
- [ ] **Phase 6: Pipeline Orchestration** - VideoGenerator coordinates services with error recovery
- [ ] **Phase 7: CLI Interface** - Command-line interface with batch processing and progress display
- [ ] **Phase 8: GitHub Actions Automation** - Scheduled workflow running 2x daily with secrets management

## Phase Details

### Phase 1: Environment & Foundation
**Goal**: Establish working development environment with validated dependencies and project structure
**Depends on**: Nothing (first phase)
**Requirements**: None explicitly mapped (foundational setup)
**Success Criteria** (what must be TRUE):
  1. Python 3.11 environment installed with MoviePy 2.2.1+ and all dependencies
  2. FFmpeg with libx264 codec can encode test video successfully
  3. MoviePy TextClip can render text overlays without ImageMagick errors
  4. Project structure created with folders for output, cache, configs, services
**Plans**: 2 plans

Plans:
- [x] 01-01-PLAN.md - Create project folder structure, requirements.txt, .gitignore, .env.example
- [x] 01-02-PLAN.md - Create environment validation script and MoviePy test video generation

### Phase 2: Brand Configuration System
**Goal**: Three brands configured with distinct visual identities, voices, and CTAs
**Depends on**: Phase 1
**Requirements**: BRAND-01, BRAND-02, BRAND-03, BRAND-04, BRAND-05
**Success Criteria** (what must be TRUE):
  1. Menopause Planner brand loads from YAML with sage green/dusty rose colors and Etsy CTA
  2. Daily Deal Darling brand loads from YAML with coral/teal colors and website CTA
  3. Fitness Made Easy brand loads from YAML with blue/lime colors and TBD CTA
  4. Each brand specifies distinct TTS voice selection
  5. CLI can load any brand by name and access all configuration properties
**Plans**: 2 plans

Plans:
- [x] 02-01-PLAN.md - Create BrandConfig Pydantic model with color validation
- [x] 02-02-PLAN.md - Create three brand YAML configs and BrandLoader utility

### Phase 3: Core Video Composition
**Goal**: Working video compositing engine producing 1080x1920 vertical MP4s with synced audio
**Depends on**: Phase 2
**Requirements**: COMP-01, COMP-02, COMP-03, COMP-04, COMP-05, COMP-06
**Success Criteria** (what must be TRUE):
  1. Compositor accepts 16:9 stock video and outputs 1080x1920 vertical video without black bars
  2. Text overlays appear as sentence blocks with brand colors positioned in safe zones (120px from edges)
  3. Text overlays sync to audio timing within 100ms accuracy throughout 60-second duration
  4. Audio track plays continuously without drift at video end
  5. Memory cleanup verified across 10 consecutive video generations without leak
**Plans**: 4 plans

Plans:
- [x] 03-01-PLAN.md - Create VideoCompositor class with 16:9 to 9:16 aspect ratio conversion
- [x] 03-02-PLAN.md - Create text overlay system with safe zone positioning and brand colors
- [x] 03-03-PLAN.md - Create audio-text synchronization using edge-tts word boundaries
- [x] 03-04-PLAN.md - Wire composition pipeline and verify all success criteria

### Phase 4: API Client Layer
**Goal**: Working API clients for all external services with error handling and retry logic
**Depends on**: Phase 1
**Requirements**: None explicitly mapped (infrastructure layer supporting services)
**Success Criteria** (what must be TRUE):
  1. GeminiClient generates text from prompts and handles 429 rate limit errors with exponential backoff
  2. PexelsClient searches and downloads videos, respecting rate limit headers
  3. TTSClient generates audio files from text using Edge-TTS with configurable voices
  4. SupabaseClient uploads videos and returns public URLs with resumable upload for large files
  5. All clients log API call metadata (duration, status, errors) for debugging
**Plans**: 5 plans

Plans:
- [x] 04-01-PLAN.md - Update dependencies, create Settings module and BaseClient with retry logic
- [x] 04-02-PLAN.md - Create GeminiClient with rate limit handling
- [x] 04-03-PLAN.md - Create PexelsClient with streaming downloads
- [x] 04-04-PLAN.md - Create TTSClient with word timing extraction
- [x] 04-05-PLAN.md - Create SupabaseClient with TUS resumable uploads

### Phase 5: Content Generation Services
**Goal**: Script, video, and audio generation services with file-based caching to prevent quota exhaustion
**Depends on**: Phase 4
**Requirements**: SCRIPT-01, SCRIPT-02, SCRIPT-03, SCRIPT-04, VIDEO-01, VIDEO-02, VIDEO-03, AUDIO-01, AUDIO-02, AUDIO-03, STOR-02, STOR-03
**Success Criteria** (what must be TRUE):
  1. ScriptGenerator creates brand-appropriate topics and voiceover scripts with CTAs naturally integrated
  2. VideoFetcher retrieves Pexels videos matching script topics and caches by search term hash
  3. AudioSynthesizer generates TTS audio with brand-specific voices and caches by script hash
  4. Cache hit prevents API call (verified by monitoring API request logs)
  5. Generated content adapts to brand voice and tone (wellness/deals/fitness distinct)
**Plans**: TBD

Plans:
- [ ] TBD during planning

### Phase 6: Pipeline Orchestration
**Goal**: VideoGenerator coordinates full pipeline with per-video error recovery and temp file cleanup
**Depends on**: Phase 3, Phase 5
**Requirements**: CLI-05, STOR-01
**Success Criteria** (what must be TRUE):
  1. VideoGenerator coordinates services sequentially: script → video → audio → composite → upload
  2. One video failure in batch does not crash entire generation (graceful error handling)
  3. Temp files cleaned up after each video regardless of success or failure
  4. Batch of 5 videos completes with mixed success/failure and reports final counts
  5. Memory returns to baseline between videos in batch (no progressive leak)
**Plans**: TBD

Plans:
- [ ] TBD during planning

### Phase 7: CLI Interface
**Goal**: Command-line interface enabling batch video generation for specified brands
**Depends on**: Phase 6
**Requirements**: CLI-01, CLI-02, CLI-03, CLI-04
**Success Criteria** (what must be TRUE):
  1. User runs `python cli.py --brand menopause --count 1` and generates 1 Menopause Planner video
  2. User runs `python cli.py --brand all --count 2` and generates 2 videos per brand (6 total)
  3. CLI shows progress during generation with status for each video
  4. CLI displays summary table showing success/failure counts per brand
  5. CLI exits with appropriate status code (0 for all success, 1 for any failures)
**Plans**: TBD

Plans:
- [ ] TBD during planning

### Phase 8: GitHub Actions Automation
**Goal**: Scheduled workflow running 2x daily with zero-touch operation
**Depends on**: Phase 7
**Requirements**: AUTO-01, AUTO-02, AUTO-03, AUTO-04
**Success Criteria** (what must be TRUE):
  1. GitHub Actions workflow installs FFmpeg and dependencies successfully
  2. Workflow runs CLI on cron schedule (2x daily)
  3. API keys loaded from GitHub Secrets without hardcoding
  4. Workflow completes successfully and uploads videos to Supabase
  5. Manual workflow dispatch triggers video generation on demand
**Plans**: TBD

Plans:
- [ ] TBD during planning

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Environment & Foundation | 2/2 | Complete | 2026-01-23 |
| 2. Brand Configuration System | 2/2 | Complete | 2026-01-23 |
| 3. Core Video Composition | 4/4 | Complete | 2026-01-23 |
| 4. API Client Layer | 5/5 | Complete | 2026-01-23 |
| 5. Content Generation Services | 0/TBD | Not started | - |
| 6. Pipeline Orchestration | 0/TBD | Not started | - |
| 7. CLI Interface | 0/TBD | Not started | - |
| 8. GitHub Actions Automation | 0/TBD | Not started | - |

---
*Roadmap created: 2026-01-22*
*Last updated: 2026-01-23 after Phase 4 complete*
