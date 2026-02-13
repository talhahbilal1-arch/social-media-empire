# Social Media Empire

## What This Is

An automated video generation system that creates 15-60 second vertical videos (1080x1920) for Pinterest Idea Pins and YouTube Shorts. The system serves three distinct brands, using AI to generate scripts, match stock video backgrounds, and create voiceovers — all running on GitHub Actions at zero monthly cost.

## Core Value

Generate engaging, brand-consistent short-form video content automatically without manual intervention or ongoing costs.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] AI script generation via Gemini API (topical tips per brand)
- [ ] Stock video background selection via Pexels API (AI-matched to script)
- [ ] Text-to-speech voiceover via Edge-TTS
- [ ] Sentence block text overlays synced to audio
- [ ] CTAs spoken naturally in voiceover
- [ ] 1080x1920 vertical video output (9:16 aspect ratio)
- [ ] Three brand configurations (colors, voice tone, topic domain, CTA)
- [ ] CLI interface: `python cli.py --brand all --count 1` produces 3 videos
- [ ] Cloud storage upload to Supabase
- [ ] GitHub Actions automation (2x daily)
- [ ] $0/month operational cost (all free-tier tools)

### Out of Scope

- Auto-upload to Pinterest/YouTube — manual upload preferred for now
- Real-time analytics/tracking — keep it simple
- Exercise demonstration videos — tips/motivation format only
- Specific product deal scraping — general category advice only
- OAuth/social media API integrations — cloud storage only

## Context

**Brands:**

1. **Menopause Planner** — wellness tips for women 45-60
   - Colors: sage green, dusty rose
   - CTA: Etsy shop link
   - Tone: warm, supportive, knowledgeable

2. **Daily Deal Darling** — product recommendations for women 25-55
   - Colors: coral, teal
   - CTA: dailydealdarling.com
   - Tone: friendly, enthusiastic, helpful

3. **Fitness Made Easy** — fitness tips/motivation for busy women
   - Colors: blue, lime
   - CTA: TBD
   - Tone: energetic, encouraging, practical

**Video Format:**
- Length: 15-60 seconds (content-driven)
- Resolution: 1080x1920 (9:16 vertical)
- Components: stock video background + sentence block text + AI voiceover
- Output: MP4 to Supabase storage

**Pipeline:**
1. Gemini generates brand-appropriate script with topic
2. Gemini suggests Pexels search terms for background
3. Pexels API retrieves matching stock video
4. Edge-TTS generates voiceover audio
5. MoviePy composites video: background + text overlays + audio
6. Video uploaded to Supabase storage

## Constraints

- **Tech stack**: Python 3.11, MoviePy, FFmpeg, Edge-TTS, Gemini API, Pexels API
- **Cost**: $0/month — all free-tier services only
- **Runtime**: GitHub Actions (free tier limits)
- **Storage**: Supabase free tier
- **Output location**: `video_automation/` folder

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Edge-TTS over other TTS | Free, good quality, multiple voices | — Pending |
| Supabase for storage | Free tier, already have account | — Pending |
| Sentence blocks over word-by-word | Simpler to implement, cleaner look | — Pending |
| AI-generated topics | Reduces manual work, keeps content fresh | — Pending |

---
*Last updated: 2026-01-22 after initialization*
