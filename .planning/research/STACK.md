# Stack Research

**Domain:** Automated Short-Form Video Generation
**Researched:** 2026-01-22
**Confidence:** HIGH

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.11 | Runtime environment | User-specified; excellent balance of performance and library compatibility. Python 3.11 is widely supported by all core dependencies in 2026. |
| MoviePy | 2.2.1+ | Video compositing engine | Industry standard for programmatic video editing in Python. V2.0+ (released May 2025) uses pure Pillow for image manipulation, eliminating ImageMagick dependency. Perfect for automated workflows. Supports text overlays, audio compositing, and transitions. |
| FFmpeg | Latest stable | Video processing backend | Required by MoviePy for encoding/decoding. Universal multimedia framework used by virtually all Python video libraries. MoviePy automatically leverages FFmpeg for optimal performance. |
| Edge-TTS | 7.2.7+ | Text-to-speech generation | Free, high-quality neural TTS using Microsoft Edge's online service. No API key required, no cost, supports multiple voices/languages/styles, and can generate subtitle files (SRT/VTT) for accessibility. |
| Google GenAI SDK | 1.60.0+ | AI script generation | Unified SDK for Gemini API (replaces deprecated google-generativeai). Supports both Gemini Developer API and Vertex AI. Python 3.10+ required, but project uses 3.11 which is compatible. |
| Pexels API | N/A (REST API) | Stock video retrieval | Free tier provides high-quality stock videos for commercial use. Simple REST API with multiple Python client libraries available. |
| Supabase | 2.27.2+ (Python client) | Video storage & hosting | Free tier storage with CDN delivery. Python client provides simple upload/download API. Alternative to S3 with better DX for small projects. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Pillow | 12.1.0+ | Image manipulation & text rendering | Required by MoviePy 2.0+ for TextClip overlays. Also used for pre-processing images, creating custom graphics, and brand-specific visual elements. |
| requests | 2.32.5+ | HTTP client for API calls | Fetching from Pexels API and uploading to Supabase. More user-friendly than urllib3 for standard REST API interactions. |
| numpy | Latest (2.x compatible) | Array processing | Automatic dependency of MoviePy. Used internally for pixel manipulation and video frame processing. |
| imageio | Latest | Media I/O | Automatic dependency of MoviePy. Handles reading/writing various media formats. |
| proglog | Latest | Progress logging | MoviePy dependency. Provides progress bars for rendering operations. |
| decorator | Latest | Function decorators | MoviePy dependency for internal function wrapping. |
| imageio-ffmpeg | Latest | FFmpeg wrapper | Provides FFmpeg binaries for imageio. Ensures consistent FFmpeg availability across platforms. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| GitHub Actions | CI/CD and scheduled video generation | Free tier sufficient for this workload. FFmpeg setup available via marketplace actions (FedericoCarboni/setup-ffmpeg@v3 or AnimMouse/setup-ffmpeg). |
| pyproject.toml | Dependency management | Modern Python packaging standard. Use with pip or uv for reproducible builds. |
| pytest | Testing framework | For unit tests on script generation, video assembly logic, and API integrations. |
| black | Code formatting | Python community standard for consistent formatting. |
| ruff | Linting | Fast Python linter, replacing flake8/pylint. |

## Installation

```bash
# Core dependencies
pip install moviepy==2.2.1
pip install edge-tts==7.2.7
pip install google-genai==1.60.0
pip install pillow==12.1.0
pip install requests==2.32.5
pip install supabase==2.27.2

# Supporting libraries (auto-installed by MoviePy, but explicit for reproducibility)
pip install numpy
pip install imageio
pip install imageio-ffmpeg
pip install proglog
pip install decorator

# Development dependencies
pip install -D pytest black ruff

# FFmpeg installation (system-level, required)
# Ubuntu/Debian: apt-get install ffmpeg
# macOS: brew install ffmpeg
# Windows: choco install ffmpeg
# GitHub Actions: Use FedericoCarboni/setup-ffmpeg@v3
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| MoviePy | OpenCV (cv2) | Use OpenCV if you need real-time video processing, computer vision tasks, or lower-level control. MoviePy is better for scripted, automated video generation. |
| MoviePy | ffmpeg-python | Use ffmpeg-python for complex FFmpeg filter chains. MoviePy provides higher-level abstractions better suited for composition tasks. |
| Edge-TTS | ElevenLabs API | Use ElevenLabs if budget allows ($5-300/month) and you need ultra-realistic voices or voice cloning. Edge-TTS is free and sufficient for most use cases. |
| Edge-TTS | gTTS (Google TTS) | Use gTTS if you need offline TTS or simpler API. Edge-TTS offers better voice quality and more options. |
| Google GenAI SDK | OpenAI API | Use OpenAI (GPT-4) if you need more advanced reasoning or have existing OpenAI credits. Gemini offers competitive quality with generous free tier. |
| Pexels API | Unsplash API | Use Unsplash for photos. Pexels specializes in high-quality stock videos which is critical for this project. |
| Supabase | AWS S3 | Use S3 for large-scale production with predictable costs. Supabase is better for rapid prototyping and free-tier operation. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| MoviePy 1.x | Deprecated as of 2025. Has ImageMagick dependency issues and compatibility problems with modern Pillow versions. | MoviePy 2.2.1+ (latest v2 release) |
| google-generativeai (legacy SDK) | Officially deprecated. All support ended November 30, 2025. Limited to critical bug fixes only. | google-genai 1.60.0+ (unified SDK) |
| Python 3.9 or earlier | While MoviePy supports 3.9+, modern Pillow (12.1.0) and google-genai require Python 3.10+. | Python 3.11 (user-specified, well-supported) |
| Python 3.12+ | MoviePy has reported compatibility issues with Python 3.12 as of late 2025 (ModuleNotFoundError). May stabilize in future. | Python 3.11 (stable, well-tested) |
| pexels-api-py 0.0.5 | Last updated February 2022, likely outdated. Better to use requests directly with Pexels REST API. | requests + manual API calls |
| ImageMagick for TextClip | MoviePy 2.0+ dropped ImageMagick dependency in favor of pure Pillow. Simpler setup, fewer dependency issues. | Pillow (automatic with MoviePy 2.0+) |

## Stack Patterns by Variant

**If generating videos longer than 60 seconds:**
- Consider chunking video processing to avoid memory issues
- Use MoviePy's write_videofile with threads=4 for parallel encoding
- Monitor GitHub Actions runner memory (7GB limit on free tier)

**If text overlays need custom fonts:**
- Install TrueType fonts (.ttf) at system level or package them in repo
- Use absolute paths for font files in TextClip
- Test font rendering locally before deploying to GitHub Actions
- Default to web-safe fonts (Arial, Helvetica) for cross-platform consistency

**If multiple brands with different styles:**
- Create brand configuration files (JSON/YAML) with colors, fonts, voice preferences
- Use dataclasses or Pydantic models for brand configuration validation
- Implement factory pattern for brand-specific video generation pipelines

**If video quality is inconsistent:**
- Use MoviePy's fps parameter explicitly (30 fps for social media)
- Set codec to 'libx264' with preset='medium' for quality/speed balance
- Use bitrate='8000k' for 1080x1920 vertical videos
- Enable audio_codec='aac' for maximum compatibility

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| MoviePy 2.2.1 | Python 3.9, 3.10, 3.11 | Python 3.12+ has known issues. Avoid for now. |
| MoviePy 2.2.1 | Pillow 12.1.0 | MoviePy 2.0+ designed for modern Pillow. V1.x had compatibility issues. |
| MoviePy 2.2.1 | NumPy 2.x | MoviePy may have issues with NumPy 2.x. Use `pip install 'numpy<2'` if encountering import errors. |
| google-genai 1.60.0 | Python 3.10, 3.11, 3.12, 3.13, 3.14 | Requires Python 3.10+. User's Python 3.11 choice is perfect. |
| Pillow 12.1.0 | Python 3.10, 3.11, 3.12, 3.13, 3.14 | Requires Python 3.10+. Compatible with user's Python 3.11. |
| edge-tts 7.2.7 | Python 3.7+ | Wide compatibility range. No issues with Python 3.11. |
| Supabase 2.27.2 | Python 3.9+ | Compatible with Python 3.11. |
| requests 2.32.5 | Python 3.9+ | Supports Python 3.9 through 3.14. |

## Critical Notes

### Python 3.11 Validation
**VERDICT: APPROVED** - Python 3.11 is an excellent choice for this stack. All core dependencies explicitly support it:
- MoviePy 2.2.1: Python 3.9-3.11 ✓
- google-genai 1.60.0: Python 3.10-3.14 ✓
- Pillow 12.1.0: Python 3.10-3.14 ✓
- edge-tts 7.2.7: Python 3.7+ ✓
- Supabase 2.27.2: Python 3.9+ ✓
- requests 2.32.5: Python 3.9+ ✓

### FFmpeg Setup in GitHub Actions
FFmpeg is NOT automatically available in GitHub Actions runners. Use one of these marketplace actions:
```yaml
- uses: FedericoCarboni/setup-ffmpeg@v3
  with:
    ffmpeg-version: release
```
OR
```yaml
- uses: AnimMouse/setup-ffmpeg@v1
```

### MoviePy 2.0 Breaking Changes
If migrating from MoviePy 1.x, note these breaking changes:
- ImageMagick dependency removed (now uses Pillow)
- API changes in TextClip initialization
- Different import paths for some functions
- Consult migration guide: https://zulko.github.io/moviepy/getting_started/updating_to_v2.html

### Edge-TTS Limitations
- **Requires internet connection** - Cannot work offline
- **Custom SSML removed** - Microsoft disabled custom SSML support as of v5.0.0
- **Rate limits unknown** - Free service, but undocumented limits. Implement retry logic.
- **No voice cloning** - Limited to Microsoft's pre-trained voices

### Gemini API Considerations
- **Free tier limits**: 15 requests/minute, 1 million tokens/day (as of early 2026)
- **Rate limiting required** - Implement exponential backoff
- **Model selection**: Use 'gemini-2.0-flash-lite' for cost efficiency, 'gemini-3-flash-preview' for quality
- **API key management**: Store in GitHub Secrets, never commit to repo

### Pexels API Best Practices
- **Free tier**: 200 requests/hour, unlimited downloads
- **Attribution**: Not legally required but encouraged
- **Search optimization**: Use specific terms, filter by orientation='portrait' for vertical videos
- **Caching**: Cache search results to reduce API calls during development

## Supporting Libraries Needed

Beyond user-specified stack, these libraries are essential:

1. **Pillow** - Required for text overlays and image manipulation in MoviePy 2.0+
2. **requests** - Standard HTTP client for Pexels API and Supabase interactions
3. **numpy** - Auto-installed by MoviePy, but critical for video processing
4. **imageio-ffmpeg** - Ensures FFmpeg availability across all platforms
5. **python-dotenv** - For managing API keys in development (not in user's list, but recommended)
6. **pydantic** - For validating brand configurations and API responses (optional but recommended)

## Sources

- [MoviePy PyPI](https://pypi.org/project/moviepy/) - Version and dependency information (HIGH confidence)
- [MoviePy GitHub](https://github.com/Zulko/moviepy) - Breaking changes and compatibility notes (HIGH confidence)
- [MoviePy Documentation](https://zulko.github.io/moviepy/) - Official API documentation (HIGH confidence)
- [Edge-TTS PyPI](https://pypi.org/project/edge-tts/) - Version and Python compatibility (HIGH confidence)
- [Edge-TTS GitHub](https://github.com/rany2/edge-tts) - Features and limitations (HIGH confidence)
- [Google GenAI SDK PyPI](https://pypi.org/project/google-genai/) - Latest unified SDK (HIGH confidence)
- [Pillow PyPI](https://pypi.org/project/Pillow/) - Version and Python support (HIGH confidence)
- [requests PyPI](https://pypi.org/project/requests/) - Version information (HIGH confidence)
- [Supabase Python Client PyPI](https://pypi.org/project/supabase/) - Version and compatibility (HIGH confidence)
- [Pexels API Documentation](https://www.pexels.com/api/documentation/) - Official API reference (HIGH confidence)
- [Setup FFmpeg GitHub Action](https://github.com/marketplace/actions/setup-ffmpeg) - CI/CD integration (HIGH confidence)
- [Stack Builders - Python Video Generation](https://www.stackbuilders.com/insights/python-video-generation/) - Best practices (MEDIUM confidence)
- [Gumlet - FFmpeg with Python 2026](https://www.gumlet.com/learn/ffmpeg-python/) - Current integration patterns (MEDIUM confidence)
- [Joyspace - AI Video Tech Stack 2026](https://joyspace.ai/ai-video-tech-stack-marketing-operations-2026) - Industry trends (MEDIUM confidence)

---
*Stack research for: Automated Short-Form Video Generation*
*Researched: 2026-01-22*
