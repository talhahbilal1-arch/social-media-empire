# Architecture Research

**Domain:** Video Automation CLI System
**Researched:** 2026-01-22
**Confidence:** HIGH

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI Interface Layer                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  cli.py (Argument Parser + Command Router)           │   │
│  └────────────────────┬─────────────────────────────────┘   │
│                       ↓                                      │
├─────────────────────────────────────────────────────────────┤
│                   Orchestration Layer                        │
│  ┌────────────────────────────────────────────────────┐     │
│  │  VideoGenerator (Pipeline Coordinator)              │     │
│  └──┬───────────┬──────────┬──────────┬────────────┬──┘     │
│     ↓           ↓          ↓          ↓            ↓        │
├─────────────────────────────────────────────────────────────┤
│                     Service Layer                            │
│  ┌─────────┐  ┌────────┐  ┌────────┐  ┌────────┐ ┌───────┐ │
│  │ Script  │  │ Video  │  │ Audio  │  │ Video  │ │Upload │ │
│  │Generator│  │Fetcher │  │Synth   │  │Composer│ │Service│ │
│  └────┬────┘  └───┬────┘  └───┬────┘  └───┬────┘ └───┬───┘ │
│       ↓           ↓           ↓            ↓          ↓     │
├─────────────────────────────────────────────────────────────┤
│                   External API Clients                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │  Gemini  │  │  Pexels  │  │ Edge-TTS │  │ Supabase │    │
│  │  Client  │  │  Client  │  │  Client  │  │  Client  │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
├─────────────────────────────────────────────────────────────┤
│                Configuration & Data Layer                    │
│  ┌───────────────────┐  ┌────────────────────────────┐      │
│  │  Brand Configs    │  │  Templates & Assets        │      │
│  │  (color, voice,   │  │  (fonts, layouts, timing)  │      │
│  │   topics, CTAs)   │  │                            │      │
│  └───────────────────┘  └────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| **CLI Interface** | Parse arguments, validate inputs, route to orchestrator | Python `argparse` or `click` library |
| **VideoGenerator** | Coordinate full pipeline: script → video → audio → composite → upload | Main orchestration class with async/sequential control |
| **ScriptGenerator** | Generate brand-appropriate scripts via Gemini API | Service wrapping Gemini client, applies brand templates |
| **VideoFetcher** | Search and download stock video from Pexels | Service wrapping Pexels client, handles caching/validation |
| **AudioSynthesizer** | Generate voiceover from script using Edge-TTS | Service wrapping TTS client, outputs timestamped audio |
| **VideoComposer** | Composite background + text overlays + audio using MoviePy | MoviePy wrapper, handles rendering pipeline |
| **UploadService** | Upload final video to Supabase storage | Supabase client wrapper, manages metadata & URLs |
| **BrandConfig** | Store brand-specific settings (colors, topics, voice, CTA) | YAML/JSON config files or Python dataclasses |
| **API Clients** | Abstract external APIs with consistent interfaces | Thin wrappers over HTTP clients with error handling |

## Recommended Project Structure

```
social-media-empire/
├── cli.py                      # Entry point: argument parsing + command routing
├── config/                     # Configuration layer
│   ├── brands/                 # Brand-specific configs
│   │   ├── brand_a.yaml
│   │   ├── brand_b.yaml
│   │   └── brand_c.yaml
│   ├── settings.py             # Global settings (API keys, paths)
│   └── templates.py            # Text overlay templates, timing configs
├── src/
│   ├── orchestration/          # Pipeline coordinators
│   │   └── video_generator.py # Main VideoGenerator class
│   ├── services/               # Business logic layer
│   │   ├── script_generator.py
│   │   ├── video_fetcher.py
│   │   ├── audio_synthesizer.py
│   │   ├── video_composer.py
│   │   └── upload_service.py
│   ├── clients/                # External API wrappers
│   │   ├── gemini_client.py
│   │   ├── pexels_client.py
│   │   ├── tts_client.py
│   │   └── supabase_client.py
│   ├── models/                 # Data models & domain objects
│   │   ├── brand.py            # Brand dataclass
│   │   ├── script.py           # Script dataclass
│   │   ├── video_spec.py       # VideoSpec dataclass
│   │   └── render_config.py    # RenderConfig dataclass
│   └── utils/                  # Shared utilities
│       ├── logging.py
│       ├── file_utils.py
│       └── validators.py
├── assets/                     # Static assets
│   ├── fonts/
│   └── watermarks/
├── output/                     # Generated videos (gitignored)
│   └── temp/                   # Temporary files during processing
├── tests/
│   ├── unit/
│   └── integration/
├── requirements.txt
└── README.md
```

### Structure Rationale

- **config/brands/:** Separate YAML files per brand enable easy addition of new brands without code changes. Each brand config contains color palette, voice settings, topic domains, and CTA URLs.

- **src/orchestration/:** Pipeline coordination logic isolated from business logic. VideoGenerator orchestrates services in sequence, handles errors, and manages state.

- **src/services/:** Each service is a single-responsibility module wrapping one pipeline step. Services are testable independently and reusable across different orchestration flows.

- **src/clients/:** Thin API wrappers provide consistent error handling, retries, and response parsing. Clients are swappable (e.g., replace Pexels with another stock video API without changing services).

- **src/models/:** Dataclasses define contracts between layers. Brand, Script, VideoSpec, and RenderConfig are passed between services, ensuring type safety and clarity.

- **assets/ vs output/:** Static assets (fonts, watermarks) are version-controlled, while generated videos are ephemeral (uploaded to Supabase, then deleted locally).

## Architectural Patterns

### Pattern 1: Service Layer Architecture

**What:** Separate business logic into service classes that are independent of CLI, with each service performing one pipeline step.

**When to use:** Always for CLI tools with multi-step workflows. Keeps CLI thin (just argument parsing), services testable, and business logic reusable.

**Trade-offs:**
- **Pros:** Clear boundaries, easy testing, reusable across interfaces (CLI, web API, scheduled jobs)
- **Cons:** More boilerplate than putting logic directly in CLI commands

**Example:**
```python
# services/script_generator.py
class ScriptGenerator:
    def __init__(self, gemini_client: GeminiClient):
        self.gemini_client = gemini_client

    def generate(self, brand: Brand, topic: str | None = None) -> Script:
        """Generate brand-appropriate script via Gemini API."""
        prompt = self._build_prompt(brand, topic)
        response = self.gemini_client.generate_text(prompt)
        return Script(
            topic=response.topic,
            text=response.text,
            duration_seconds=response.duration
        )

    def _build_prompt(self, brand: Brand, topic: str | None) -> str:
        # Prompt engineering based on brand tone, topics
        ...
```

### Pattern 2: Pipeline Orchestrator

**What:** Single class coordinates sequential execution of services, passing data between steps and handling errors.

**When to use:** Multi-step workflows where each step depends on the previous output. Common in video pipelines, ETL jobs, deployment automation.

**Trade-offs:**
- **Pros:** Centralized error handling, clear execution flow, easy to add hooks (logging, metrics)
- **Cons:** Can become a "God object" if too much logic is added; keep it thin (just coordination)

**Example:**
```python
# orchestration/video_generator.py
class VideoGenerator:
    def __init__(
        self,
        script_gen: ScriptGenerator,
        video_fetcher: VideoFetcher,
        audio_synth: AudioSynthesizer,
        video_composer: VideoComposer,
        uploader: UploadService
    ):
        self.script_gen = script_gen
        self.video_fetcher = video_fetcher
        self.audio_synth = audio_synth
        self.video_composer = video_composer
        self.uploader = uploader

    def generate(self, brand: Brand) -> str:
        """Execute full pipeline, return uploaded video URL."""
        # Step 1: Generate script
        script = self.script_gen.generate(brand)

        # Step 2: Fetch background video
        video_path = self.video_fetcher.fetch(script.search_terms)

        # Step 3: Synthesize audio
        audio_path = self.audio_synth.synthesize(script.text, brand.voice)

        # Step 4: Composite video
        final_video = self.video_composer.compose(
            background=video_path,
            script=script,
            audio=audio_path,
            brand=brand
        )

        # Step 5: Upload to Supabase
        url = self.uploader.upload(final_video, brand)

        # Cleanup temp files
        self._cleanup([video_path, audio_path, final_video])

        return url
```

### Pattern 3: Configuration as Code

**What:** Brand settings stored as YAML/JSON files, loaded into typed dataclasses at runtime. Enables adding new brands without code changes.

**When to use:** Multi-tenant or multi-brand systems where each entity has distinct configuration (colors, voices, domains).

**Trade-offs:**
- **Pros:** Non-developers can add brands, easy A/B testing, clear separation of config from code
- **Cons:** Runtime validation needed (type safety weaker than hardcoding)

**Example:**
```python
# config/brands/brand_a.yaml
name: "Brand A"
colors:
  primary: "#FF5733"
  secondary: "#33FF57"
  text: "#FFFFFF"
voice:
  name: "en-US-AriaNeural"
  rate: "+10%"
  pitch: "+5Hz"
topics:
  - "tech gadgets"
  - "productivity tips"
  - "life hacks"
cta:
  text: "Learn More"
  url: "https://brand-a.com"

# models/brand.py
from dataclasses import dataclass
import yaml

@dataclass
class Brand:
    name: str
    colors: dict[str, str]
    voice: dict[str, str]
    topics: list[str]
    cta: dict[str, str]

    @classmethod
    def load(cls, path: str) -> "Brand":
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)
```

### Pattern 4: Thin Client Wrappers

**What:** Wrap external APIs in thin client classes with consistent error handling, retries, and response parsing.

**When to use:** Any system integrating with external APIs. Isolates API-specific quirks from business logic.

**Trade-offs:**
- **Pros:** Swappable clients, centralized retry/error logic, easier mocking in tests
- **Cons:** Extra abstraction layer (but worth it for maintainability)

**Example:**
```python
# clients/pexels_client.py
import requests
from typing import List

class PexelsClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.pexels.com/videos"

    def search_videos(
        self,
        query: str,
        orientation: str = "portrait",
        size: str = "large"
    ) -> List[dict]:
        """Search Pexels for videos matching query."""
        headers = {"Authorization": self.api_key}
        params = {
            "query": query,
            "orientation": orientation,
            "size": size,
            "per_page": 5
        }

        try:
            response = requests.get(
                f"{self.base_url}/search",
                headers=headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json()["videos"]
        except requests.RequestException as e:
            raise PexelsAPIError(f"Pexels API failed: {e}")

    def download_video(self, url: str, output_path: str) -> str:
        """Download video from URL to local path."""
        response = requests.get(url, stream=True)
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return output_path
```

## Data Flow

### Request Flow

```
User Command: python cli.py --brand brand_a --count 1
    ↓
CLI Parser (argparse)
    ↓
Load Brand Config (brand_a.yaml → Brand dataclass)
    ↓
VideoGenerator.generate(brand)
    ↓
┌─────────────────────────────────────────────────┐
│ Pipeline Execution (Sequential)                 │
├─────────────────────────────────────────────────┤
│ 1. ScriptGenerator.generate(brand)              │
│    → GeminiClient.generate_text(prompt)         │
│    → Returns: Script(topic, text, duration)     │
│                                                  │
│ 2. VideoFetcher.fetch(script.search_terms)      │
│    → PexelsClient.search_videos(query)          │
│    → PexelsClient.download_video(url)           │
│    → Returns: /tmp/background_12345.mp4         │
│                                                  │
│ 3. AudioSynthesizer.synthesize(script, voice)   │
│    → TTSClient.generate_audio(text, voice)      │
│    → Returns: /tmp/voiceover_12345.mp3          │
│                                                  │
│ 4. VideoComposer.compose(background, script,    │
│                           audio, brand)          │
│    → MoviePy: Load background video              │
│    → MoviePy: Add text overlays (brand colors)  │
│    → MoviePy: Composite audio track              │
│    → Render to: /tmp/final_12345.mp4            │
│                                                  │
│ 5. UploadService.upload(final_video, brand)     │
│    → SupabaseClient.upload_file(path, metadata) │
│    → Returns: https://supabase.../video.mp4     │
│                                                  │
│ 6. Cleanup temp files                           │
└─────────────────────────────────────────────────┘
    ↓
Return: Video URL
    ↓
CLI: Print success message + URL
```

### State Management

This is a **stateless CLI** with no persistent state between runs. Each execution:
1. Loads brand config from disk
2. Executes pipeline in memory
3. Uploads result to Supabase
4. Deletes temp files
5. Exits

**No database needed.** All state is either in config files (brands) or in Supabase (uploaded videos).

### Key Data Flows

1. **Brand Config → All Services:** Brand dataclass flows through entire pipeline, providing colors, voice settings, topics, and CTAs to each service.

2. **Script → Downstream Services:** Generated script contains text (for audio synthesis), search terms (for video fetching), and timing (for video composition).

3. **File Paths → Temp File Management:** Each service returns local file paths. Orchestrator tracks these paths and deletes them after upload succeeds.

4. **Error Propagation:** Services raise specific exceptions (GeminiAPIError, PexelsAPIError, etc.). Orchestrator catches and logs errors, cleans up partial artifacts, and exits with informative error messages.

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| **1-10 videos/day** | Current architecture is perfect. Sequential pipeline, local temp storage, no optimization needed. |
| **10-100 videos/day** | Add parallel processing: use `asyncio` or `multiprocessing` to generate multiple videos concurrently. Pre-fetch stock videos to avoid Pexels rate limits. |
| **100-1000 videos/day** | Move to queue-based architecture (Celery + Redis). Each pipeline step becomes a Celery task. Add video caching layer (S3/R2) for frequently used backgrounds. Monitor Gemini/Pexels quotas. |
| **1000+ videos/day** | Consider distributed rendering (AWS MediaConvert or similar). Separate orchestration (lightweight) from rendering (heavyweight). Add observability (metrics, traces). |

### Scaling Priorities

1. **First bottleneck: MoviePy rendering**
   - **What breaks:** MoviePy is CPU-intensive. Rendering 100 videos sequentially takes hours.
   - **How to fix:** Use `multiprocessing.Pool` to render videos in parallel (one per CPU core). Move to cloud rendering service (AWS MediaConvert, GCP Transcoder API) for massive scale.

2. **Second bottleneck: API rate limits**
   - **What breaks:** Gemini and Pexels have rate limits. Generating 100 videos hits these limits.
   - **How to fix:** Add retry logic with exponential backoff. Cache Pexels videos (download once, reuse). Use multiple API keys (round-robin). Implement request throttling.

3. **Third bottleneck: GitHub Actions runtime limits**
   - **What breaks:** GitHub Actions has 6-hour max runtime per job. Large batches may timeout.
   - **How to fix:** Split into multiple jobs (matrix strategy). Use self-hosted runners with no time limits. Move to dedicated cron service (AWS Lambda, GCP Cloud Run).

## Anti-Patterns

### Anti-Pattern 1: Mixing Business Logic in CLI Command Handler

**What people do:** Put all video generation logic directly in the CLI command function.

**Why it's wrong:**
- Impossible to test without invoking CLI
- Cannot reuse logic in web API, scheduled jobs, or other interfaces
- Hard to mock external APIs for testing
- Violates Single Responsibility Principle

**Do this instead:**
```python
# BAD: All logic in CLI
@click.command()
@click.option("--brand", required=True)
def generate(brand):
    # Directly call APIs here, no services
    response = requests.post("https://api.gemini.com/...", ...)
    # ... 200 lines of video generation logic

# GOOD: Thin CLI delegates to orchestrator
@click.command()
@click.option("--brand", required=True)
def generate(brand_name):
    brand = Brand.load(f"config/brands/{brand_name}.yaml")
    orchestrator = build_video_generator()  # DI factory
    url = orchestrator.generate(brand)
    click.echo(f"Video uploaded: {url}")
```

### Anti-Pattern 2: Hardcoding Brand Configuration in Code

**What people do:** Define brand colors, voices, topics as constants in Python files.

**Why it's wrong:**
- Adding a new brand requires code changes (violates Open/Closed Principle)
- Non-developers cannot add brands
- Difficult to A/B test brand variations
- Config is mixed with logic, harder to reason about

**Do this instead:**
```python
# BAD: Hardcoded brands
BRANDS = {
    "brand_a": {
        "colors": {"primary": "#FF5733"},
        "voice": "en-US-AriaNeural",
        # ...
    }
}

# GOOD: Load from config files
brand = Brand.load("config/brands/brand_a.yaml")
```

### Anti-Pattern 3: Not Cleaning Up Temp Files

**What people do:** Generate temp files during processing but don't delete them, assuming disk is infinite.

**Why it's wrong:**
- GitHub Actions runners have limited disk (14GB SSD)
- Generating 100 videos can fill disk (1GB per video × 100 = 100GB)
- Leaves sensitive data on disk (scripts may contain private info)

**Do this instead:**
```python
# GOOD: Always cleanup in finally block
def generate(brand: Brand) -> str:
    temp_files = []
    try:
        video_path = self.video_fetcher.fetch(...)
        temp_files.append(video_path)

        audio_path = self.audio_synth.synthesize(...)
        temp_files.append(audio_path)

        final_video = self.video_composer.compose(...)
        temp_files.append(final_video)

        url = self.uploader.upload(final_video)
        return url
    finally:
        for path in temp_files:
            if os.path.exists(path):
                os.remove(path)
```

### Anti-Pattern 4: No Error Recovery in Pipeline

**What people do:** Let exceptions bubble up and crash the entire batch. If generating 10 videos and video #3 fails, lose all progress.

**Why it's wrong:**
- Wastes time/money (re-run entire batch)
- Hard to debug (which video failed?)
- Poor user experience (no partial success)

**Do this instead:**
```python
# GOOD: Graceful error handling
def generate_batch(brands: list[Brand], count: int) -> dict:
    results = {"success": [], "failed": []}

    for brand in brands:
        for i in range(count):
            try:
                url = self.generate(brand)
                results["success"].append({
                    "brand": brand.name,
                    "url": url
                })
            except Exception as e:
                logger.error(f"Failed {brand.name} video {i}: {e}")
                results["failed"].append({
                    "brand": brand.name,
                    "error": str(e)
                })

    return results
```

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| **Gemini API** | REST API via `requests` | Requires API key in env var `GEMINI_API_KEY`. Rate limit: 60 req/min. Retry on 429/503. |
| **Pexels API** | REST API via `requests` | Requires API key in env var `PEXELS_API_KEY`. Rate limit: 200 req/hour. Cache videos to avoid re-download. |
| **Edge-TTS** | Python library `edge-tts` | No API key needed (uses Edge browser TTS). Fully async API. Generate audio with `edge_tts.Communicate(text, voice).save(path)`. |
| **Supabase Storage** | REST API via `supabase-py` | Requires project URL + anon key. Upload to `videos/` bucket. Return public URL for uploaded file. |
| **MoviePy/FFmpeg** | Python library `moviepy` | FFmpeg must be installed on system (`brew install ffmpeg` or GitHub Actions apt-get). MoviePy wraps FFmpeg, handles video/audio encoding. |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| **CLI ↔ Orchestrator** | Direct function call | CLI passes `Brand` dataclass, receives video URL string. CLI handles argparse, orchestrator handles pipeline. |
| **Orchestrator ↔ Services** | Direct function calls | Orchestrator injects dependencies (clients) into services via constructor. Services return domain objects (`Script`, file paths, URLs). |
| **Services ↔ Clients** | Direct function calls | Services call client methods, clients return parsed responses. Clients handle retries, errors, and API-specific logic. |
| **Brand Config ↔ All Layers** | Dataclass passed by reference | `Brand` dataclass loaded once at CLI, passed through entire pipeline. Immutable (no mutations during pipeline). |

## Build Order & Dependencies

### Recommended Build Sequence

**Phase 1: Foundation (No dependencies)**
1. **Project structure** - Create folder hierarchy, `requirements.txt`, `.gitignore`
2. **Brand config system** - `models/brand.py` dataclass + sample YAML configs
3. **Settings management** - `config/settings.py` for API keys, paths

**Phase 2: API Clients (Depends on Phase 1 settings)**
4. **Gemini client** - `clients/gemini_client.py` with text generation
5. **Pexels client** - `clients/pexels_client.py` with video search + download
6. **TTS client** - `clients/tts_client.py` wrapping `edge-tts`
7. **Supabase client** - `clients/supabase_client.py` with upload method

**Phase 3: Services (Depends on Phase 2 clients)**
8. **ScriptGenerator** - `services/script_generator.py` using Gemini client
9. **VideoFetcher** - `services/video_fetcher.py` using Pexels client
10. **AudioSynthesizer** - `services/audio_synthesizer.py` using TTS client
11. **VideoComposer** - `services/video_composer.py` using MoviePy (most complex)
12. **UploadService** - `services/upload_service.py` using Supabase client

**Phase 4: Orchestration (Depends on Phase 3 services)**
13. **VideoGenerator** - `orchestration/video_generator.py` coordinating all services
14. **Error handling** - Graceful failures, temp file cleanup

**Phase 5: CLI Interface (Depends on Phase 4 orchestrator)**
15. **CLI command** - `cli.py` with argparse, brand loading, command routing
16. **Logging setup** - Structured logging to console

**Phase 6: Deployment (Depends on Phase 5 CLI)**
17. **GitHub Actions workflow** - `.github/workflows/generate.yml` with 2x daily cron
18. **Secrets management** - Add API keys to GitHub Secrets

### Dependency Rationale

- **Bottom-up build order:** Start with lowest-level components (clients) and build upwards. This allows testing each layer in isolation.

- **Clients before services:** Services depend on clients to talk to external APIs. Build clients first so services can be tested with real or mocked clients.

- **Services before orchestration:** Orchestrator coordinates services. Services must exist before orchestrator can call them.

- **Orchestration before CLI:** CLI is just a thin wrapper around orchestrator. Build orchestrator first, then add CLI commands.

- **Local testing before CI/CD:** Get full pipeline working locally (`python cli.py --brand brand_a --count 1`) before adding GitHub Actions complexity.

### Critical Path

The **VideoComposer** (MoviePy) is the most complex component and the critical path:
- Requires understanding MoviePy API (clips, compositing, rendering)
- Requires FFmpeg installation and correct configuration
- Requires text overlay positioning (trial and error for good UX)
- Rendering is CPU-intensive (slow iteration cycle)

**Recommendation:** Build VideoComposer early (Phase 3) to de-risk. Use hardcoded test data initially (don't wait for Gemini/Pexels integration).

## Sources

### Architecture Patterns
- [Service Layer Pattern in Python](https://dev.to/alexis_jean/organize-your-code-with-the-service-layer-pattern-a-simple-python-example-2pnn) - Clean separation of business logic
- [Architecture Patterns with Python](https://www.cosmicpython.com/book/appendix_project_structure.html) - Project structure template
- [Clean Architecture in Python](https://www.linkedin.com/pulse/implementation-clean-architecture-python-part-1-cli-watanabe) - CLI implementation patterns

### Video Processing
- [MoviePy Documentation](https://zulko.github.io/moviepy/) - Official MoviePy docs
- [FFmpeg with Python in 2026](https://www.gumlet.com/learn/ffmpeg-python/) - FFmpeg integration best practices
- [MoviePy v2.0 Discussion](https://github.com/Zulko/moviepy/discussions/2241) - Performance considerations and limitations

### Multi-Brand Architecture
- [Multi-Tenant Architecture Guide 2026](https://www.future-processing.com/blog/multi-tenant-architecture/) - Multi-tenant patterns applicable to multi-brand systems
- [Django Multi-Tenant SaaS 2026](https://medium.com/@yogeshkrishnanseeniraj/building-a-multi-tenant-saas-in-django-complete-2026-architecture-e956e9f5086a) - Configuration separation patterns

### API Integration
- [Python API Client Design Pattern](https://bhomnick.net/design-pattern-python-api-client/) - Best practices for API client wrappers
- [API Integration Best Practices](https://www.cosmicpython.com/book/chapter_04_service_layer.html) - Service layer with external APIs

### Build Automation
- [Build Automation Patterns](https://en.wikipedia.org/wiki/Build_automation) - Dependency management and sequencing
- [Video Production Workflows](https://www.ziflow.com/blog/video-production-workflow) - Multi-stage video pipeline patterns

---
*Architecture research for: Video Automation CLI System*
*Researched: 2026-01-22*
