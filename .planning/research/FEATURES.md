# Feature Research

**Domain:** Automated vertical video generation for social media (Pinterest Idea Pins, YouTube Shorts)
**Researched:** 2026-01-22
**Confidence:** HIGH

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **AI script generation** | Core value prop - automated content creation | MEDIUM | Using LLMs (Gemini) for brand-appropriate scripts. Standard in 2026 text-to-video platforms. |
| **Stock video matching** | Background video is essential for vertical video format | LOW | Pexels API provides free, searchable stock footage. Alternative: Unsplash for images. |
| **Text-to-speech voiceover** | Voiceovers are expected in short-form video (78% of Shorts use audio) | LOW | Edge-TTS is free, supports multiple voices. Cloud alternatives: ElevenLabs, Google TTS. |
| **Automatic captions/text overlays** | Auto-captioning is now standard in all 2026 video platforms | MEDIUM | Text overlays synced to audio segments. Essential for accessibility and engagement. |
| **Vertical format (9:16)** | Pinterest Idea Pins and YouTube Shorts require 1080x1920 | LOW | Non-negotiable for platform compatibility. Google Veo 3.1 added native vertical support in Jan 2026. |
| **15-60 second video length** | Platform requirements: Pinterest (3-60s per page), YouTube Shorts (15-60s optimal) | LOW | Longer than 60s loses Shorts classification on YouTube. |
| **MP4 output format** | Universal video format for social platforms | LOW | H.264 encoding standard. Pinterest max: 2GB file, 1GB recommended. |
| **Multi-brand support** | Differentiating colors/tones per brand is core to multi-brand automation | MEDIUM | Brand configs for colors, tone, topics. Critical for the 3-brand use case. |
| **Cloud storage upload** | Videos must be accessible for manual posting to platforms | LOW | Supabase storage integration. Alternative: S3, Google Cloud Storage. |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required, but valuable.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **CLI-first interface** | Developer-friendly, scriptable, version-controllable | LOW | `python cli.py --brand all --count 1` enables automation. GUI platforms dominate market in 2026. |
| **GitHub Actions automation** | Free scheduled generation (2x daily) without servers | MEDIUM | Cron-scheduled workflows. Free for public repos, 2000 min/month for private. Note: 15-30 min execution delays possible. |
| **Batch generation** | Generate multiple videos in one command (--count flag) | MEDIUM | Enables content stockpiling. Competitors focus on single video generation. Requires quality control loop. |
| **Template-based text overlays** | Consistent visual branding with sentence-block sync | MEDIUM | Text blocks synced to voiceover timing. More professional than auto-captions alone. |
| **Brand-aware content generation** | AI understands brand voice, target audience, avoids off-brand topics | HIGH | Fine-tuned prompts per brand. Prevents "menopause tips" on fitness channel. Competitive moat. |
| **Zero-cost operation** | Free APIs (Gemini, Pexels, Edge-TTS, GitHub Actions) = no per-video cost | LOW | Eliminates per-video costs that plague competitors ($0.01-$0.50/sec for premium AI video). |
| **Local generation option** | Can run locally or in CI/CD - no vendor lock-in | MEDIUM | MoviePy runs anywhere Python runs. Enables testing before committing to automation. |
| **Transparent pipeline** | Each step (script → video → audio → composite) is visible and debuggable | LOW | CLI outputs show progress. Developers can inspect intermediate files. GUI platforms are black boxes. |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create problems.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **Direct platform posting** | "Automate everything end-to-end" | Pinterest/YouTube APIs require OAuth, have rate limits, risk account bans for automated posting. Platform policies change unpredictably. | Upload to cloud storage, manual posting gives editorial control. Add webhook notifications when videos ready. |
| **Custom AI video generation** | "Use Runway/Kling/Sora for backgrounds" | Costs $0.01-$0.50/sec, 60s video = $0.60-$30. Destroys zero-cost model. Quality inconsistent for stock footage use case. | Stick with Pexels stock video (free, reliable, curated). Custom AI video is overkill for backgrounds. |
| **Real-time generation** | "Generate on-demand instantly" | MoviePy compositing takes 30-60s per video. Gemini API has rate limits. Encourages expectation of instant results. | Batch generation + scheduling. Pre-generate content library. Async workflows with status tracking. |
| **Automatic viral optimization** | "AI should optimize for virality" | Virality is unpredictable. Chasing trends creates generic content. 80% of workers say AI adds to workload trying to "optimize" everything. | Focus on brand consistency and volume. Let platform algorithms find audience. Quality + quantity > chasing trends. |
| **100+ video batch generation** | "Generate a month of content at once" | MoviePy has memory issues with >100 concurrent sources. Quality control becomes impossible. Storage costs spike. | Cap at 10-20 videos per batch. Smaller batches enable iteration and quality review. |
| **Fully automated editing** | "AI should handle all creative decisions" | Removes human oversight. 5-10% error rate on captions requires review. Bias/mistakes in AI training data perpetuate without checks. | Automation handles 95% of work (compositing, syncing, rendering). Human reviews scripts and final output. |
| **Multi-language support (v1)** | "Support 10+ languages for global reach" | Translation quality varies. Voice synthesis accent quality inconsistent. Complexity explodes (brand voice per language). | Launch with English only. Add languages based on user demand signals. Edge-TTS supports 100+ languages when needed. |
| **Advanced video effects** | "Add transitions, filters, animations" | Increases rendering time. Distracts from content. Trends change quickly (what's "cool" in Jan is dated by March). | Simple, clean overlays. Let content shine. Vertical video users scroll fast - simplicity wins. |

## Feature Dependencies

```
[Multi-brand support]
    └──requires──> [AI script generation]
                       └──requires──> [LLM API access (Gemini)]

[Text overlays synced to audio]
    └──requires──> [Text-to-speech voiceover]
    └──requires──> [Audio duration parsing]

[Batch generation]
    └──requires──> [Cloud storage upload]
    └──enhances──> [GitHub Actions automation]

[GitHub Actions automation]
    └──requires──> [CLI interface]
    └──requires──> [Cloud storage upload]
    └──requires──> [Secrets management for API keys]

[Template-based text overlays]
    └──conflicts──> [Automatic captions only]
        (Choose one approach to avoid visual clutter)
```

### Dependency Notes

- **Multi-brand support requires AI script generation:** Brand-specific prompts must be fed to LLM. Can't have multi-brand without brand-aware content.
- **Text overlays require voiceover:** Timing synced to audio segments. No audio = no sync points.
- **Batch generation enhances GitHub Actions:** Scheduled automation becomes valuable when generating multiple videos per run (2x daily schedule = 4-10 videos/day).
- **Template overlays conflict with auto-captions:** Both add text to video. Combining creates cluttered screen on vertical format. Choose sentence blocks OR captions, not both.

## MVP Definition

### Launch With (v1)

Minimum viable product — what's needed to validate the concept.

- [x] **AI script generation (Gemini)** — Core automation value. Without this, it's just manual video editing.
- [x] **Stock video matching (Pexels)** — Background footage is non-negotiable for vertical video format.
- [x] **Text-to-speech voiceover (Edge-TTS)** — Audio drives engagement. Free TTS is sufficient for MVP.
- [x] **Sentence block text overlays** — Differentiates from basic auto-caption tools. Synced to voiceover.
- [x] **Vertical MP4 output (1080x1920)** — Platform compatibility requirement.
- [x] **Multi-brand support (3 brands)** — Core use case. Validates brand-aware content generation.
- [x] **CLI interface with --brand and --count flags** — Enables scripting and automation.
- [x] **Cloud storage upload (Supabase)** — Makes videos accessible for manual posting.

### Add After Validation (v1.x)

Features to add once core is working.

- [ ] **GitHub Actions scheduled automation** — Add when manual generation proves valuable. Trigger: 20+ manually generated videos.
- [ ] **Call-to-action (CTA) integration** — Spoken CTA in voiceover + visual overlay. Trigger: User feedback requests CTAs.
- [ ] **Video duration control** — Currently fixed at script length. Add min/max duration flags. Trigger: Platform algorithm changes favor specific lengths.
- [ ] **Custom brand templates** — User-defined color schemes, fonts, overlay positions. Trigger: 3+ users want their own brands.
- [ ] **Thumbnail generation** — Extract frame as thumbnail for manual posting. Trigger: Manual thumbnail creation becomes bottleneck.
- [ ] **Quality scoring** — AI evaluates output quality (audio clarity, text readability, topic relevance). Trigger: Batch generation produces inconsistent quality.
- [ ] **Content calendar integration** — Link generation to content themes/events. Trigger: Manual topic planning becomes repetitive.
- [ ] **A/B variant generation** — Generate 2-3 versions with different hooks/visuals. Trigger: User wants to test what performs best.

### Future Consideration (v2+)

Features to defer until product-market fit is established.

- [ ] **Multi-language support** — Defer until English-language PMF proven. Adds 10x complexity.
- [ ] **Custom video backgrounds (upload)** — Defer until stock video limitations identified. Requires storage/processing.
- [ ] **Music background tracks** — Defer until voiceover-only proves limiting. Copyright/licensing complexity.
- [ ] **Advanced analytics** — View tracking, engagement metrics. Defer until posting automation exists.
- [ ] **Webhook notifications** — Notify when batch completes. Defer until async generation needed.
- [ ] **Video editing/regeneration** — "Regenerate script but keep video." Defer until iteration workflow emerges.
- [ ] **Team collaboration features** — Multi-user access, approval workflows. Defer until >1 user.

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| AI script generation | HIGH | MEDIUM | P1 |
| Stock video matching | HIGH | LOW | P1 |
| Text-to-speech voiceover | HIGH | LOW | P1 |
| Text overlays synced to audio | HIGH | MEDIUM | P1 |
| Vertical format (9:16) | HIGH | LOW | P1 |
| Multi-brand support | HIGH | MEDIUM | P1 |
| CLI interface | HIGH | LOW | P1 |
| Cloud storage upload | HIGH | LOW | P1 |
| Batch generation | MEDIUM | MEDIUM | P1 |
| GitHub Actions automation | MEDIUM | MEDIUM | P2 |
| CTA integration | MEDIUM | LOW | P2 |
| Duration control | MEDIUM | LOW | P2 |
| Custom brand templates | MEDIUM | MEDIUM | P2 |
| Thumbnail generation | LOW | LOW | P2 |
| Quality scoring | MEDIUM | HIGH | P2 |
| Multi-language support | LOW | HIGH | P3 |
| Music background tracks | LOW | MEDIUM | P3 |
| Advanced analytics | LOW | HIGH | P3 |

**Priority key:**
- P1: Must have for launch (MVP)
- P2: Should have, add when possible (v1.x)
- P3: Nice to have, future consideration (v2+)

## Competitor Feature Analysis

| Feature | GUI Platforms (InVideo, Pictory) | API Platforms (Creatomate, Runway) | Our Approach |
|---------|----------------------------------|-----------------------------------|--------------|
| **Video generation** | Web UI, drag-and-drop, templates | REST API, webhook callbacks | CLI + Python scripts - developer-first |
| **Pricing model** | $15-60/month subscriptions | $0.01-$0.50 per second generated | Zero-cost (free APIs) |
| **Automation** | Limited - manual triggers in UI | Full API automation, requires dev work | GitHub Actions cron - no servers needed |
| **Content control** | Template library, limited customization | Full programmatic control | Brand configs + transparent pipeline |
| **Stock footage** | Built-in libraries (Storyblocks, Getty) | User provides or API integration | Pexels API (free, adequate quality) |
| **Voiceover** | Premium AI voices (ElevenLabs, Azure) | User provides or premium TTS APIs | Edge-TTS (free, sufficient quality) |
| **Platform posting** | Some offer direct posting (risky) | No direct posting (API focus) | No direct posting - manual control safer |
| **Batch generation** | Generate 1-5 at a time in UI | Programmatic batching via API | CLI flag --count 1-20 |
| **Learning curve** | Low - point and click | High - requires API integration skills | Medium - CLI familiarity needed |
| **Vendor lock-in** | High - proprietary templates/assets | Medium - API dependent | Low - runs locally, standard formats |

## Platform-Specific Feature Requirements

### Pinterest Idea Pins
- **Format:** 1080x1920 (9:16) or 1000x1500 (2:3)
- **File type:** MP4 or MOV
- **Encoding:** H.264 or H.265
- **File size:** 100MB web, 2GB mobile (recommend 1GB)
- **Duration:** 3-60 seconds per page, 2-20 pages per Pin
- **Text:** 250 characters max per frame
- **Special note:** No outbound links - brand building only

### YouTube Shorts
- **Format:** 1080x1920 (9:16) required
- **Duration:** 15-60 seconds (under 60s for Shorts classification)
- **Optimization:** Include #shorts hashtag, front-load topic in first 3 seconds
- **Algorithm:** Prioritizes watch-through percentage (full video views)
- **Monetization:** Requires 1,000 subs + 4,000 watch hours OR 10M Shorts views in 90 days
- **Best practices:** Direct to long-form content, persistent links now supported

## Sources

**Automated video generation landscape:**
- [NVIDIA RTX Accelerates 4K AI Video Generation](https://blogs.nvidia.com/blog/rtx-ai-garage-ces-2026-open-models-video-generation/)
- [5 Bold Predictions for AI Video Generation in 2026](https://higgsfield.ai/blog/top-5-predictions-for-ai-video-generation-in-2026)
- [AI Video Generators, Social Media Trends 2026 | HeyGen](https://www.heygen.com/blog/ai-video-generators-transforming-video-production-2026)
- [Top AI Video Generation Model Comparison in 2026](https://www.pixazo.ai/blog/ai-video-generation-models-comparison-t2v)
- [The Top 10 Video Generation Models of 2026 | DataCamp](https://www.datacamp.com/blog/top-video-generation-models)

**Video automation tools:**
- [10 best video automation softwares [2026]](https://www.plainlyvideos.com/blog/video-automation-softwares)
- [Best AI Video Generator: An Updated Comparison Of 10 Tools](https://massive.io/gear-guides/the-best-ai-video-generator-comparison/)
- [AI Video Editing in 2026: Best Tools, Workflows & Automation](https://cutback.video/blog/ai-video-editing-in-2026-best-tools-workflows-automation-explained)

**Social media automation:**
- [10 Best Social Media Automation Tools for 2026](https://www.eclincher.com/articles/10-best-social-media-automation-tools-for-2026)
- [6 Best AI Video Tools for Social Media in 2026](https://www.capcut.com/resource/6-best-AI-video-tools-for-social-media)
- [How to Dominate TikTok, Instagram Reels & YouTube Shorts in 2026](https://almcorp.com/blog/short-form-video-mastery-tiktok-reels-youtube-shorts-2026/)

**Text-to-video APIs:**
- [Best Text-to-Video API in 2026: Complete Developer Guide](https://wavespeed.ai/blog/posts/best-text-to-video-api-2026/)
- [Complete Guide to AI Video Generation APIs in 2026](https://wavespeed.ai/blog/posts/complete-guide-ai-video-apis-2026/)
- [Text to Video API - Transform Your Text into Engaging Videos](https://www.vadoo.tv/text-to-video-api)

**Platform specifications:**
- [Pinterest Pin Size 2026: The Complete Guide](https://socialrails.com/blog/pinterest-pin-size-dimensions-guide)
- [Pinterest Idea Pins: Complete Guide 2026](https://socialrails.com/social-media-terms/idea-pin-pinterest)
- [Pinterest Video Specs: Key Dimensions for Maximum Engagement](https://www.capcut.com/resource/pinterest-video-specs)

**YouTube Shorts:**
- [How to Make the YouTube Shorts Algorithm Work for You (2026)](https://riverside.com/blog/youtube-shorts-algorithm)
- [YouTube Automations 2026 Guide: AI Workflow & Growth Tips](https://thinkpeak.ai/youtube-automations-2026-guide/)
- [YouTube Shorts: Everything You Need to Know in 2026](https://www.navigatevideo.com/news/a-guide-to-youtube-shorts)

**Vertical video automation:**
- [5 AI Vertical Video Editors to Edit/Make 9:16 Video with AI](https://www.flexclip.com/learn/vertical-video-editor.html)
- [Free AI Vertical Video Generator](https://invideo.io/make/vertical-video/)
- [Google Veo 3.1 vertical video update](https://techcrunch.com/2026/01/13/googles-update-for-veo-3-1-lets-users-create-vertical-videos-through-reference-images/)

**Batch generation pitfalls:**
- [Veo 3.1 Batch Video Generation and Automation](https://skywork.ai/blog/ai-video/veo-3-1-batch-video-generation-and-automation/)
- [The Hidden Downsides of AI-Generated Videos](https://www.digitalbrew.com/the-hidden-downsides-of-ai-generated-videos/)
- [How to Create AI-Generated Videos in Bulk](https://creatomate.com/blog/how-to-create-ai-generated-videos-in-bulk)

**CLI vs GUI:**
- [AI CLI Tools vs GUI Tools: Pros and Cons for Developers](https://vocal.media/futurism/ai-cli-tools-vs-gui-tools-pros-and-cons-for-developers)
- [Git GUI vs. Git CLI: Benefits and drawbacks](https://graphite.com/guides/git-gui-vs-cli)

**GitHub Actions automation:**
- [Automating Your Workflows on a Schedule: GitHub Actions + Cron](https://medium.com/@thibautdonis1998/automating-your-workflows-on-a-schedule-github-actions-cron-fd7e662083c6)
- [How to Run GitHub Actions on a Schedule](https://jackharner.com/blog/github-actions-cron/)
- [Free Cron Jobs with Github Actions](https://www.theanshuman.dev/articles/free-cron-jobs-with-github-actions-31d6)

**MoviePy capabilities:**
- [MoviePy documentation](https://zulko.github.io/moviepy/)
- [moviepy · PyPI](https://pypi.org/project/moviepy/)
- [Unlocking the Power of MoviePy](https://www.oreateai.com/blog/unlocking-the-power-of-moviepy-your-guide-to-video-editing-with-python/f44c76b70acd93a953933d5f3107d079)

---
*Feature research for: Automated vertical video generation for social media*
*Researched: 2026-01-22*
