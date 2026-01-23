# Pitfalls Research

**Domain:** Python Video Automation (MoviePy, FFmpeg, TTS, API Integration)
**Researched:** 2026-01-22
**Confidence:** HIGH

## Critical Pitfalls

### Pitfall 1: Memory Leaks with VideoFileClip and Concatenation

**What goes wrong:**
MoviePy doesn't fully release memory when closing VideoFileClips. When concatenating multiple clips, memory usage grows dramatically - users report consuming all 8GB RAM by the 50th clip when processing 1000 clips totaling only 3.65GB. Memory remains elevated even after calling `.close()` and deleting clips.

**Why it happens:**
VideoFileClip has a reference cycle due to its `__del__` method, causing Python's garbage collector to ignore instances. When using `concatenate_videoclips()`, processes can allocate 1.5GB RAM but only 0.5GB is freed afterward.

**How to avoid:**
- Use `ImageSequenceClip` instead of loading all frames in memory
- Process videos in smaller batches (10-20 clips max) and write intermediate outputs
- Explicitly call `clip.close()` and `del clip` after each composite
- Use `gc.collect()` to force garbage collection between batches
- Monitor memory usage and restart process if exceeding thresholds
- For GitHub Actions: Use smaller runner instances and process sequentially

**Warning signs:**
- Memory usage climbing steadily during multi-clip processing
- BrokenPipeError when writing videos on memory-constrained systems
- Process killed by OOM (Out of Memory) killer
- Slower performance as script progresses

**Phase to address:**
Phase 2 (Core Video Pipeline) - implement memory-efficient compositing patterns before scaling to multiple videos per day.

---

### Pitfall 2: ImageMagick Dependency Hell for Text Rendering

**What goes wrong:**
MoviePy's `TextClip` requires ImageMagick but often fails to detect it even when installed. Common errors: "MoviePy Error missing magick font", "fontconfig delegate missing", or TextClip only showing basic system fonts. Upgrading from ImageMagick 6 to 7 breaks compatibility.

**Why it happens:**
MoviePy may require ImageMagick 6 specifically, not version 7. The fontconfig delegate library is often missing from ImageMagick installations. Font detection depends on system-specific paths that vary between OS environments.

**How to avoid:**
- Install ImageMagick 6 specifically, not version 7
- Verify fontconfig delegate is installed: `convert -list configure | grep DELEGATES`
- On macOS: Install Ghostscript via brew for font support: `brew install ghostscript`
- Set IMAGEMAGICK_BINARY environment variable explicitly in code
- Test TextClip with basic fonts during setup phase
- For GitHub Actions: Install ImageMagick 6 and fontconfig in workflow setup
- Consider using PIL/Pillow for text rendering as fallback (no ImageMagick dependency)

**Warning signs:**
- "MoviePy Error missing magick font" when creating TextClip
- TextClip only showing Arial/Courier but not custom fonts
- Different behavior between local dev and CI/CD environment
- "This error can be due to the fact that ImageMagick is not installed"

**Phase to address:**
Phase 1 (Environment Setup) - validate ImageMagick installation and font rendering before writing video pipeline code.

---

### Pitfall 3: Audio-Video Sync Drift in Long Videos

**What goes wrong:**
Audio progressively drifts out of sync in concatenated videos. A 10-minute video can have audio 3-5 seconds behind by the end. The drift is linear and increases with video duration, becoming very noticeable in 60-second videos composed of multiple subclips.

**Why it happens:**
Frame rate mismatches between source video and output video cause accumulated timing errors. Rounding errors in frame timing compound when concatenating multiple clips. MoviePy's audio/video synchronization algorithm doesn't compensate for drift over long durations.

**How to avoid:**
- Set explicit `fps` parameter on all VideoFileClips and output: `clip.with_fps(30)`
- Use consistent frame rate throughout pipeline (30fps recommended for social media)
- For 15-60 second videos: composite as single timeline, not concatenation
- Test sync at video end, not just beginning
- If linear drift detected, adjust audio length proportionally before composite
- Use `audio_fps=44100` consistently across all audio clips
- Prefer single background video over concatenated clips

**Warning signs:**
- Audio sync perfect at start but off by end of video
- Drift magnitude proportional to video length
- Different drift amounts with different background videos
- Voiceover ending before/after video ends

**Phase to address:**
Phase 2 (Core Video Pipeline) - implement strict FPS control and sync testing before deploying automation.

---

### Pitfall 4: Edge-TTS Rate Limiting and Voice Inconsistency

**What goes wrong:**
Microsoft implements undocumented rate limiting on Edge-TTS, causing 403 blocks from same IP with too many requests. Voice quality and inflection patterns change unexpectedly as Microsoft updates voices. Long text strings produce incomplete audio files with arbitrary cutoff points.

**Why it happens:**
Edge-TTS uses unofficial Microsoft Edge online TTS endpoint (not Azure Speech API), making it less stable. Microsoft can change voices, add rate limits, or deprecate access without notice. Service prioritizes Edge browser users over API users.

**How to avoid:**
- Implement request caching: save generated audio files by text hash, reuse for identical scripts
- Add delays between TTS requests (2-3 seconds minimum) for same IP
- For 2x daily automation: rate limiting unlikely but still cache audio
- Monitor for 403 errors and implement exponential backoff
- Test voice samples regularly to detect quality changes
- Keep audio generation separate from video generation (fail fast)
- Consider Azure Speech API as paid fallback ($4/month for 1M chars)
- For long scripts: split into sentences and concatenate audio

**Warning signs:**
- 403 Forbidden errors from Edge-TTS
- Audio files cutting off mid-sentence
- Voice suddenly sounds different (inflection changes)
- Inconsistent pronunciation between generations

**Phase to address:**
Phase 3 (Audio Integration) - implement caching and error handling before running scheduled automation.

---

### Pitfall 5: Pexels API Quota Exhaustion

**What goes wrong:**
Pexels free tier has 200 requests/hour and 20,000 requests/month limits. Each video download counts as request. With poor search terms, you may request same video multiple times or exhaust quota testing. Hitting limit stops video generation completely.

**Why it happens:**
Default limits are shared across all API keys in same project. Testing with different search terms consumes quota. No local caching means re-downloading same videos. 2 videos/day = 60/month (well under limit), but development/testing can exhaust quota.

**How to avoid:**
- Implement local video cache: hash search terms, store downloaded videos
- Check cache before API request
- Request unlimited quota (free but requires approval) if doing extensive testing
- Use `X-Ratelimit-Remaining` header to monitor quota
- Limit video search results to 5-10 options, pick randomly
- For testing: use same set of pre-downloaded videos, not live API
- Track API usage in logs to detect quota leaks
- Implement fallback: retry with different search terms if quota exceeded

**Warning signs:**
- HTTP 429 (Too Many Requests) from Pexels API
- Quota exhausted during development/testing phase
- Same videos downloaded repeatedly
- Multiple failed API requests in logs

**Phase to address:**
Phase 4 (Stock Video Integration) - implement caching and quota monitoring before connecting to scheduled workflow.

---

### Pitfall 6: Gemini API Rate Limit Changes (December 2025 Update)

**What goes wrong:**
Gemini API quota was adjusted on December 7, 2025, causing unexpected 429 errors. Free tier now limited to 5-15 RPM depending on model. Rate limits are per Google Cloud Project, not per API key, so multiple keys don't multiply quota. Four dimensions (RPM, TPM, RPD, IPM) each enforced separately.

**Why it happens:**
Google adjusted quotas recently with minimal notice. Token bucket algorithm enforces limits strictly. Developers assume multiple API keys = multiple quotas (incorrect - project-level limits). Exceeding any single dimension triggers 429.

**How to avoid:**
- Implement exponential backoff for 429 errors (required for Gemini API)
- For 2x daily automation: Rate limits not an issue (5 RPM >> 2 requests/day)
- Track which dimension triggered 429 (check error message)
- Generate scripts in batch: get 7 days of scripts in one session vs daily
- Cache successful script generations by topic/brand
- Monitor TPM (tokens per minute) not just RPM - long scripts consume more tokens
- Consider upgrading to Paid Tier 1 (150-300 RPM) if scaling beyond 2x daily

**Warning signs:**
- HTTP 429 with "quota metric exceeded" error
- Intermittent failures that resolve after waiting
- Errors mentioning RPM, TPM, RPD, or IPM limits
- Different behavior after December 2025

**Phase to address:**
Phase 5 (AI Script Generation) - implement rate limit handling before scheduled automation.

---

### Pitfall 7: FFmpeg Codec and Preset Compatibility

**What goes wrong:**
MoviePy's `write_videofile()` throws "Unrecognized option 'preset'" error with incompatible FFmpeg versions. BrokenPipeError occurs when FFmpeg process crashes mid-write. Setting codec parameter incorrectly causes "MoviePy couldn't find the codec associated with the filename" error. The `pixel_format` option gets ignored when using libx264.

**Why it happens:**
Different FFmpeg versions support different presets. Some FFmpeg builds lack libx264 codec. MoviePy doesn't validate codec compatibility before writing. FFmpeg process can fail silently, causing broken pipe.

**How to avoid:**
- Always specify codec explicitly: `write_videofile('out.mp4', codec='libx264')`
- Use `preset='ultrafast'` for GitHub Actions (fastest render, acceptable quality)
- Validate FFmpeg installation with: `ffmpeg -version` and `ffmpeg -codecs | grep libx264`
- Set fps explicitly: `clip.with_fps(30).write_videofile()`
- For vertical video: specify pixel format: `pixel_format='yuv420p'`
- Test write_videofile with short clip before processing full video
- Catch BrokenPipeError and log FFmpeg output for debugging
- GitHub Actions: Use ubuntu-latest which has compatible FFmpeg

**Warning signs:**
- "Unrecognized option 'preset'" in error output
- BrokenPipeError: [Errno 32] Broken pipe
- "MoviePy couldn't find the codec" ValueError
- Video file created but unplayable (codec mismatch)

**Phase to address:**
Phase 2 (Core Video Pipeline) - validate codec/preset compatibility during environment setup.

---

### Pitfall 8: Vertical Video Aspect Ratio and Text Safe Zones

**What goes wrong:**
Stock videos from Pexels are typically 16:9 landscape (1920x1080), but output must be 9:16 portrait (1080x1920). Improper scaling causes black bars or cropped content. Text overlays placed too close to edges get obscured by platform UI (Instagram profile pic, TikTok buttons, captions).

**Why it happens:**
FFmpeg/MoviePy will letterbox (black bars) if you don't explicitly crop/scale. Developers test without platform UI and don't notice unsafe text placement. Each platform has different safe zone dimensions.

**How to avoid:**
- For landscape source: crop to center square first, then scale to 1080x1920
- Use MoviePy `resize()` with `height=1920` and crop width to 1080 center
- Test safe zones (2026 guidelines):
  - Instagram Reels: 250px buffer top/bottom (safe zone: 910x1386)
  - TikTok: 131px from top, 367px from bottom, 120px from sides
  - YouTube Shorts: 672px from bottom, 192px from right
- Position text in upper-middle third (300-800px from top)
- Keep text 120px from all edges minimum
- Use background rectangles behind text for readability
- Test output on actual devices with platform apps before deploying

**Warning signs:**
- Black bars on left/right of vertical video
- Stretched/squished video content
- Text obscured by platform UI elements
- Content cut off at edges

**Phase to address:**
Phase 2 (Core Video Pipeline) - implement proper aspect ratio handling and Phase 6 (Text Overlays) - enforce safe zone positioning.

---

### Pitfall 9: MoviePy Version 2.0 Breaking Changes

**What goes wrong:**
Code written for MoviePy v1.x breaks completely in v2.0. The `moviepy.editor` namespace no longer exists. Methods changed from `set_duration()` to `with_duration()`. Effects are now classes instead of functions. All "set_" methods renamed to "with_" and work out-of-place (return new clip instead of modifying in-place).

**Why it happens:**
MoviePy 2.0 restructured API for consistency and immutability. Breaking changes were necessary for better architecture. Many tutorials and Stack Overflow answers use v1.x syntax.

**How to avoid:**
- Pin MoviePy version in requirements.txt: `moviepy>=2.0.0,<3.0.0`
- Use v2.0 syntax from start:
  - `clip.with_duration(5)` not `clip.set_duration(5)`
  - `from moviepy import VideoFileClip` not `from moviepy.editor import VideoFileClip`
  - Chain immutable operations: `clip.with_duration(5).with_fps(30)`
- Read v2.0 migration guide: https://zulko.github.io/moviepy/getting_started/updating_to_v2.html
- Be cautious with tutorials/examples - check MoviePy version they use
- Remember: methods don't modify in-place, they return new clips

**Warning signs:**
- ImportError: cannot import from 'moviepy.editor'
- AttributeError: 'VideoFileClip' object has no attribute 'set_duration'
- Unexpected behavior where clip modifications don't persist
- Code works locally but breaks in CI/CD (version mismatch)

**Phase to address:**
Phase 1 (Environment Setup) - pin correct MoviePy version and validate API compatibility.

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Skip caching Pexels videos | Faster initial development | Hit API quota during testing, slower generation, potential quota blocks | Never - implement from start |
| Skip caching TTS audio | Simpler code | Hit rate limits, inconsistent voices, wasted API calls | Never - implement from start |
| Use default MoviePy fps | Less code to write | Audio sync issues, unpredictable output quality | Never - always set explicitly |
| Test on desktop only | Faster iteration | Text obscured by mobile UI, poor user experience | Never - test on actual devices |
| Ignore memory cleanup | Simpler code structure | Memory leaks crash GitHub Actions, unreliable automation | Only for single-video scripts (not automation) |
| Use concatenate for multiple clips | Easier than single timeline | Audio sync drift, higher memory usage | Only for <5 clips under 10 seconds total |
| Skip ImageMagick validation | Assume it works | Cryptic font errors in production, CI/CD failures | Never - validate during setup phase |
| Use preset='medium' | Better quality output | 3-5x slower rendering on GitHub Actions | Only if <30 second video and have time budget |

## Integration Gotchas

Common mistakes when connecting to external services.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Pexels API | Not caching downloaded videos, exhausting quota in testing | Implement file-based cache with search term hash as key, check cache before API call |
| Edge-TTS | Assuming unlimited requests, not handling 403 errors | Add 2-3 second delays between requests, implement audio file caching, handle 403 with exponential backoff |
| Gemini API | Using multiple API keys thinking it multiplies quota | Remember quota is per Google Cloud Project, implement exponential backoff for 429 errors |
| Supabase Storage | Using standard upload for large videos (>6MB) | Use resumable upload (TUS protocol) for videos >6MB, use direct storage hostname for better performance |
| FFmpeg via MoviePy | Not specifying codec/fps/preset explicitly | Always set codec='libx264', preset='ultrafast', and fps=30 explicitly in write_videofile() |
| GitHub Actions FFmpeg | Assuming FFmpeg has all codecs | Validate FFmpeg codecs in setup step: `ffmpeg -codecs | grep libx264` |

## Performance Traps

Patterns that work at small scale but fail as usage grows.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Loading entire video into memory | High memory usage, slow processing | Use MoviePy streaming mode, process frame-by-frame only if needed | Videos >1 minute or multiple clips |
| No intermediate file cleanup | Disk space exhaustion | Delete temp files after each video generation, GitHub Actions workspace limit 14GB | After 10-20 video generations |
| Synchronous API calls | Slow generation time | Batch Gemini requests for multiple scripts, parallel Pexels searches | When scaling beyond 2x daily |
| Regenerating identical content | Wasted API quota and time | Cache by content hash: script text → audio file, search terms → video file | After 30 days of 2x daily (60 videos) |
| Processing videos sequentially | Long GitHub Actions runtime | Process multiple brands in parallel using matrix strategy | When scaling to 5+ brands |
| No error recovery | One failure stops all generation | Implement per-video try-catch, continue on failure, report errors | When running multiple videos per workflow |

## Security Mistakes

Domain-specific security issues beyond general web security.

| Mistake | Risk | Prevention |
|---------|------|------------|
| Committing API keys to git | Keys leaked publicly, quota theft, account compromise | Use GitHub Secrets for all API keys (Gemini, Pexels, Supabase, Edge-TTS if needed) |
| Storing videos in public Supabase bucket | Brand content accessible to anyone with URL | Use private buckets with signed URLs, set appropriate RLS policies |
| No input validation on AI-generated scripts | Inappropriate content in videos, brand damage | Implement content filter checking for profanity/banned words before TTS/video generation |
| Hardcoded brand secrets in code | Accidental exposure in logs or errors | Store brand-specific config in GitHub Secrets or encrypted Supabase table |
| Logging full API responses | Sensitive data in GitHub Actions logs | Log only status codes and error messages, not full response bodies |
| No rate limit handling | API keys blocked/banned after exceeding limits | Implement exponential backoff, respect rate limit headers, monitor usage |

## UX Pitfalls

Common user experience mistakes in this domain.

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Text overlay too small | Unreadable on mobile devices | Minimum 60pt font size for 1080x1920, test on actual phone |
| White text on light backgrounds | Illegible text, poor engagement | Use contrasting text colors or semi-transparent background rectangles |
| Voiceover too fast | Users can't keep up, poor retention | Limit script to ~150 words for 60 seconds, test pacing before deploying |
| No text/voiceover sync | Confusing viewing experience | Time text overlays to match voiceover pacing, use subtitle-style timing |
| Ignoring platform safe zones | Text cut off by UI elements | Follow 2026 safe zone guidelines, keep critical content in center 70-80% |
| Generic stock footage | Low engagement, feels impersonal | Use Gemini to suggest highly specific search terms related to script content |
| Jarring transitions | Unprofessional appearance | Use fade transitions or ensure visual continuity between clips |
| Inconsistent branding | Users can't recognize brand | Define brand colors, fonts, logos in config, apply consistently across all videos |

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **Video compositing:** Video plays correctly but check: audio sync at END of video (not just start), text within safe zones on actual devices, memory released after generation
- [ ] **Text overlays:** Text appears but verify: readable on mobile 6" screen, not obscured by Instagram/TikTok UI, sufficient contrast with all background videos, timing matches voiceover
- [ ] **API integrations:** Successful response but check: implemented rate limit handling, added exponential backoff for errors, caching responses to avoid repeated calls, monitoring quota usage
- [ ] **Error handling:** Try-catch added but verify: specific exception types caught, errors logged with context, graceful degradation (continue on failure), notification on repeated failures
- [ ] **GitHub Actions automation:** Workflow runs but check: secrets properly configured, intermediate files cleaned up, total runtime under limits, failure in one video doesn't stop others
- [ ] **Memory management:** Clips created but verify: `.close()` called on all VideoFileClips, explicit `del` for large objects, `gc.collect()` between videos, memory usage doesn't grow across iterations
- [ ] **Font rendering:** Text appears locally but check: ImageMagick installed on GitHub Actions, font files available in CI environment, fallback font if custom font missing
- [ ] **Vertical video:** Renders at 1080x1920 but verify: no black bars on sides, content not stretched/squished, aspect ratio maintained from source, cropping focuses on important content

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Memory leak crashes GitHub Actions | LOW | Add explicit `clip.close()` and `gc.collect()` calls, reduce batch size, restart process between videos |
| ImageMagick missing in production | LOW | Add ImageMagick 6 + fontconfig installation to GitHub Actions setup step, or switch to PIL/Pillow for text |
| Audio sync drift detected | MEDIUM | Re-render with explicit fps matching, or post-process with FFmpeg to adjust audio tempo proportionally |
| Edge-TTS rate limited | LOW | Wait 1 hour for rate limit reset, implement 2-3 second delays between future requests, add audio caching |
| Pexels quota exhausted | LOW | Wait for hour/month reset, request unlimited quota (free), implement video caching, use cached videos for testing |
| Gemini API 429 errors | LOW | Implement exponential backoff (doubles delay each retry), batch requests, or wait for minute/day reset |
| FFmpeg codec error | LOW | Install FFmpeg with libx264: `sudo apt-get install ffmpeg`, or use alternative codec like libvpx for webm |
| Text outside safe zones | MEDIUM | Recalculate positions using safe zone guidelines, re-render all affected videos with corrected positioning |
| Supabase upload timeout | LOW | Switch to resumable upload (TUS protocol) for videos >6MB, use direct storage hostname for better performance |
| MoviePy v1/v2 syntax mismatch | MEDIUM | Update all imports to MoviePy 2.0 syntax, replace set_* with with_* methods, pin version in requirements.txt |

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Memory leaks with VideoFileClip | Phase 2 (Core Video Pipeline) | Run 10 consecutive video generations, verify memory returns to baseline |
| ImageMagick dependency missing | Phase 1 (Environment Setup) | Test TextClip rendering in CI/CD environment, verify fonts available |
| Audio-video sync drift | Phase 2 (Core Video Pipeline) | Generate 60-second video, verify audio sync at 0s, 30s, and 60s marks |
| Edge-TTS rate limiting | Phase 3 (Audio Integration) | Implement caching, test 50 consecutive TTS requests with delays |
| Pexels quota exhaustion | Phase 4 (Stock Video Integration) | Implement caching, verify cache hit before API call, monitor quota |
| Gemini rate limits | Phase 5 (AI Script Generation) | Implement exponential backoff, test 429 error handling |
| FFmpeg codec errors | Phase 2 (Core Video Pipeline) | Validate FFmpeg codecs in setup, test write_videofile with libx264 |
| Aspect ratio/safe zones | Phase 6 (Text Overlays) | Test on actual devices with Instagram/TikTok apps, verify no UI obstruction |
| MoviePy v2.0 breaking changes | Phase 1 (Environment Setup) | Pin MoviePy version, verify imports and method syntax |
| Supabase upload failures | Phase 7 (Storage Integration) | Test uploading 20MB+ video, verify resumable upload works |

## Sources

**MoviePy Issues:**
- [MoviePy Releases](https://github.com/Zulko/moviepy/releases)
- [Updating from v1.X to v2.X](https://zulko.github.io/moviepy/getting_started/updating_to_v2.html)
- [Memory Leak In VideoFileClip](https://github.com/Zulko/moviepy/issues/96)
- [Closing video doesn't release memory](https://github.com/Zulko/moviepy/issues/1284)
- [Memory leak in concatenate_videoclips](https://github.com/Zulko/moviepy/issues/1292)
- [Large RAM usage when concatenating](https://github.com/Zulko/moviepy/issues/1535)

**ImageMagick/Font Issues:**
- [ImageMagick not detected by moviepy](https://github.com/Zulko/moviepy/issues/693)
- [MoviePy TextClip Custom Font Not Recognized](https://github.com/ImageMagick/ImageMagick/discussions/6468)
- [No available fonts in moviepy](https://github.com/Zulko/moviepy/issues/426)
- [Mac OSX: MoviePy Error missing magick font](https://tutorials.technology/solved_errors/osx-OSError-MoviePy-Error.html)

**Audio Sync Issues:**
- [Audio Desynchronization with video](https://github.com/Zulko/moviepy/issues/2458)
- [How to synchronize audio and video stream](https://github.com/Zulko/moviepy/issues/1167)

**Edge-TTS Issues:**
- [Common Edge-TTS Errors](https://pyvideotrans.com/edgetts-error)
- [Edge-TTS GitHub Issues](https://github.com/rany2/edge-tts/issues)
- [Edge TTS: The Ultimate Guide](https://www.videosdk.live/developer-hub/ai/edge-tts)

**Pexels API:**
- [Pexels API Documentation](https://www.pexels.com/api/documentation/)
- [What steps to avoid hitting rate limit](https://help.pexels.com/hc/en-us/articles/900006470063-What-steps-can-I-take-to-avoid-hitting-the-rate-limit)
- [How do I get unlimited requests](https://help.pexels.com/hc/en-us/articles/900005852323-How-do-I-get-unlimited-requests)

**Gemini API:**
- [Rate limits](https://ai.google.dev/gemini-api/docs/rate-limits)
- [Gemini API Rate Limits Explained: 2026 Guide](https://www.aifreeapi.com/en/posts/gemini-api-rate-limit-explained)
- [Gemini API Rate Limits Guide 2025](https://blog.laozhang.ai/ai-tools/gemini-api-rate-limits-guide/)

**FFmpeg/Codec Issues:**
- [write_videofile problems](https://github.com/Zulko/moviepy/discussions/2089)
- [Moviepy unable to find ffmpeg libx264](https://github.com/Zulko/moviepy/issues/696)
- [FFmpeg Error Codes](https://ffmpeg.org/doxygen/trunk/group__lavu__error.html)

**Supabase Storage:**
- [Upload file size restrictions](https://supabase.com/docs/guides/troubleshooting/upload-file-size-restrictions-Y4wQLT)
- [Resumable Uploads](https://supabase.com/docs/guides/storage/uploads/resumable-uploads)
- [How to increase timeout when uploading](https://github.com/orgs/supabase/discussions/23218)

**Vertical Video Safe Zones:**
- [Instagram Safe Zone Templates](https://www.jamiesteedman.co.uk/freebies/free-instagram-safe-zone-templates-1080x1920-vertical-for-reels-stories-social-media-videos/)
- [Instagram safe zones explained for 2026](https://zeely.ai/blog/master-instagram-safe-zones/)
- [Safe Zones for TikTok, Meta & Instagram](https://houseofmarketers.com/guide-to-safe-zones-tiktok-facebook-instagram-stories-reels/)

**GitHub Actions:**
- [Let's talk about GitHub Actions](https://github.blog/news-insights/product-news/lets-talk-about-github-actions/)

**FFmpeg Aspect Ratio:**
- [How to change video resolutions using FFmpeg](https://www.mux.com/articles/convert-video-to-different-resolutions-with-ffmpeg)
- [FFmpeg Video Optimization for Different Platforms](https://www.videoscompress.com/blog/FFmpeg-Video-Optimization-for-Different-Platforms)

---
*Pitfalls research for: Python Video Automation with MoviePy, FFmpeg, Edge-TTS, and API integrations*
*Researched: 2026-01-22*
