# Requirements: Social Media Empire

**Defined:** 2026-01-22
**Core Value:** Generate engaging, brand-consistent short-form video content automatically without manual intervention or ongoing costs.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Script Generation

- [ ] **SCRIPT-01**: System generates brand-appropriate topic for each video
- [ ] **SCRIPT-02**: System generates voiceover script with CTA naturally integrated
- [ ] **SCRIPT-03**: System generates Pexels search terms matching the script content
- [ ] **SCRIPT-04**: Script adapts to brand voice (wellness/deals/fitness tone)

### Video Sourcing

- [ ] **VIDEO-01**: System fetches stock video from Pexels API matching search terms
- [ ] **VIDEO-02**: System handles multiple aspect ratios (crops/scales to 1080x1920)
- [ ] **VIDEO-03**: System selects video length appropriate for script duration

### Audio Generation

- [ ] **AUDIO-01**: System generates voiceover audio from script using Edge-TTS
- [ ] **AUDIO-02**: System uses brand-specific TTS voice for each brand
- [ ] **AUDIO-03**: Voiceover speaks CTA naturally within the script

### Video Composition

- [ ] **COMP-01**: System composites stock video + text overlay + audio into final video
- [ ] **COMP-02**: Output is 1080x1920 (9:16 vertical) MP4
- [ ] **COMP-03**: Video length is content-driven (15-60 seconds based on script)
- [ ] **COMP-04**: Text overlays appear as sentence blocks synced to audio timing
- [ ] **COMP-05**: Text positioned within safe zones (250px buffer from edges)
- [ ] **COMP-06**: Text uses brand-specific color palette

### Brand Configuration

- [ ] **BRAND-01**: Menopause Planner brand configured (sage green/dusty rose, Etsy CTA)
- [ ] **BRAND-02**: Daily Deal Darling brand configured (coral/teal, dailydealdarling.com CTA)
- [ ] **BRAND-03**: Fitness Made Easy brand configured (blue/lime, TBD CTA)
- [ ] **BRAND-04**: Each brand has distinct TTS voice selection
- [ ] **BRAND-05**: Brand configs stored as editable YAML files

### CLI Interface

- [ ] **CLI-01**: `python cli.py --brand <name>` generates videos for specified brand
- [ ] **CLI-02**: `python cli.py --brand all` generates videos for all brands
- [ ] **CLI-03**: `python cli.py --count <N>` generates N videos per brand
- [ ] **CLI-04**: CLI shows progress and status for each video generated
- [ ] **CLI-05**: Batch continues if one video fails (error recovery)

### Storage & Output

- [ ] **STOR-01**: System uploads completed videos to Supabase storage
- [ ] **STOR-02**: System can output videos locally without upload (--local flag)
- [ ] **STOR-03**: System logs metadata per video (script, video source, timestamps)

### Automation

- [ ] **AUTO-01**: GitHub Actions workflow runs CLI on schedule
- [ ] **AUTO-02**: Automation runs 2x daily
- [ ] **AUTO-03**: Workflow handles secrets (API keys) securely
- [ ] **AUTO-04**: Workflow installs FFmpeg and dependencies

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Enhanced Features

- **ENH-01**: Multiple TTS voice options per brand (variety)
- **ENH-02**: Background music option (royalty-free)
- **ENH-03**: Thumbnail generation for each video
- **ENH-04**: Video preview before upload (dry-run mode)

### Analytics

- **ANAL-01**: Track videos generated per brand over time
- **ANAL-02**: Store generation success/failure rates

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Direct platform posting | Risk of account bans, OAuth complexity, API changes |
| Custom AI video generation (Runway/Sora) | $0.60-$30 per video, destroys zero-cost model |
| Multi-language support | 10x complexity increase; launch English-only |
| Real-time generation | MoviePy takes 30-60s per video; batch is better |
| 100+ video batches | MoviePy memory issues with >100 concurrent sources |
| Automatic viral optimization | Creates generic content; focus on brand consistency |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| SCRIPT-01 | Phase 5 | Pending |
| SCRIPT-02 | Phase 5 | Pending |
| SCRIPT-03 | Phase 5 | Pending |
| SCRIPT-04 | Phase 5 | Pending |
| VIDEO-01 | Phase 5 | Pending |
| VIDEO-02 | Phase 5 | Pending |
| VIDEO-03 | Phase 5 | Pending |
| AUDIO-01 | Phase 5 | Pending |
| AUDIO-02 | Phase 5 | Pending |
| AUDIO-03 | Phase 5 | Pending |
| COMP-01 | Phase 3 | Pending |
| COMP-02 | Phase 3 | Pending |
| COMP-03 | Phase 3 | Pending |
| COMP-04 | Phase 3 | Pending |
| COMP-05 | Phase 3 | Pending |
| COMP-06 | Phase 3 | Pending |
| BRAND-01 | Phase 2 | Pending |
| BRAND-02 | Phase 2 | Pending |
| BRAND-03 | Phase 2 | Pending |
| BRAND-04 | Phase 2 | Pending |
| BRAND-05 | Phase 2 | Pending |
| CLI-01 | Phase 7 | Pending |
| CLI-02 | Phase 7 | Pending |
| CLI-03 | Phase 7 | Pending |
| CLI-04 | Phase 7 | Pending |
| CLI-05 | Phase 6 | Pending |
| STOR-01 | Phase 6 | Pending |
| STOR-02 | Phase 5 | Pending |
| STOR-03 | Phase 5 | Pending |
| AUTO-01 | Phase 8 | Pending |
| AUTO-02 | Phase 8 | Pending |
| AUTO-03 | Phase 8 | Pending |
| AUTO-04 | Phase 8 | Pending |

**Coverage:**
- v1 requirements: 33 total
- Mapped to phases: 33
- Unmapped: 0

---
*Requirements defined: 2026-01-22*
*Last updated: 2026-01-22 after roadmap creation*
