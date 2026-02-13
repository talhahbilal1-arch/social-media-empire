# Phase 4: API Client Layer - Research

**Researched:** 2026-01-23
**Domain:** Python API client development with external services (Gemini, Pexels, Edge-TTS, Supabase)
**Confidence:** HIGH

## Summary

This phase involves building robust API clients for four external services: Google Gemini (text generation), Pexels (video search/download), Edge-TTS (text-to-speech), and Supabase Storage (file uploads). The research reveals a clear standard stack centered on the official SDKs where available (`google-genai`, `supabase`), supplemented with robust HTTP clients (`httpx` or `requests`) for services without official Python SDKs. Critical success factors include implementing exponential backoff with jitter for rate limit handling, using streaming downloads for large files, proper environment variable management for API keys, and structured logging for debugging.

The landscape changed significantly in December 2025 when Google reduced Gemini API free tier limits by 50-80% (from 15 RPM to 5 RPM), making robust retry logic essential rather than optional. Edge-TTS offers high-quality TTS without API keys or costs, while Supabase requires the TUS protocol for resumable uploads of files >6MB. All clients should follow a common architecture pattern with base classes, connection pooling, and consistent error handling.

**Primary recommendation:** Use official SDKs (`google-genai`, `supabase`) for Gemini and Supabase, build thin wrappers around `requests` for Pexels (no official SDK), use `edge-tts` library directly for TTS, implement exponential backoff with `backoff` library for all HTTP operations, and use `httpx.Client()` with connection pooling for services making multiple requests to the same host.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| google-genai | 1.60.0 | Google Gemini API access | Official SDK, GA since May 2025, handles auth/retries, supports async |
| supabase | 2.27.2 | Supabase Storage uploads | Official Python client, includes storage methods, actively maintained |
| edge-tts | 7.2.7 | Text-to-speech generation | Free Microsoft Edge TTS, no API key needed, neural voices, async support |
| requests | 2.31+ | HTTP client for Pexels | Industry standard for sync HTTP, simple API, wide adoption |
| backoff | 2.2.1 | Exponential backoff/retry | Decorator-based retry logic, full jitter support, battle-tested |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| httpx | 0.28.1 | Modern HTTP client | When async support needed, HTTP/2 required, or connection pooling essential |
| tuspy | 1.1.0 | TUS resumable uploads | For Supabase files >6MB, implements TUS protocol |
| python-dotenv | 1.0+ | Environment variable loading | Development environments, load .env files |
| structlog | 25.5+ | Structured logging | Production logging with metadata, async-safe context |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| google-genai | Direct REST API | Lose retry logic, type safety, official support |
| requests | httpx | Gain async but more complex, use httpx if making many concurrent requests |
| backoff | tenacity | Similar features, backoff simpler for basic cases, tenacity more configurable |
| edge-tts | Google Cloud TTS, AWS Polly | Cost money, require cloud setup, better quality/control |

**Installation:**
```bash
pip install google-genai supabase edge-tts requests backoff httpx tuspy python-dotenv structlog
```

## Architecture Patterns

### Recommended Project Structure
```
src/
├── clients/
│   ├── __init__.py
│   ├── base.py              # BaseClient with common retry/logging
│   ├── gemini.py            # GeminiClient
│   ├── pexels.py            # PexelsClient
│   ├── tts.py               # TTSClient
│   └── storage.py           # SupabaseClient
├── config/
│   └── settings.py          # Environment variable loading
└── utils/
    └── logging.py           # Structured logging setup
```

### Pattern 1: Base Client with Shared Retry Logic
**What:** Abstract base class providing common HTTP client initialization, retry decorators, and logging
**When to use:** When building multiple API clients that share error handling patterns

**Example:**
```python
# Source: https://bhomnick.net/design-pattern-python-api-client/
import logging
import backoff
import httpx
from typing import Optional

class BaseClient:
    """Base class for API clients with retry logic and logging."""

    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url
        self.logger = logging.getLogger(self.__class__.__name__)
        self.client = httpx.Client(
            base_url=base_url,
            timeout=30.0,
            headers={"Authorization": f"Bearer {api_key}"} if api_key else {}
        )

    @backoff.on_exception(
        backoff.expo,
        (httpx.HTTPStatusError, httpx.RequestError),
        max_tries=5,
        max_time=60,
        giveup=lambda e: isinstance(e, httpx.HTTPStatusError) and e.response.status_code < 500
    )
    def _request(self, method: str, endpoint: str, **kwargs):
        """Make HTTP request with automatic retry on transient errors."""
        import time
        start = time.time()

        try:
            response = self.client.request(method, endpoint, **kwargs)
            response.raise_for_status()

            duration = time.time() - start
            self.logger.info(
                f"{method} {endpoint}",
                extra={"duration_ms": duration * 1000, "status": response.status_code}
            )
            return response
        except Exception as e:
            duration = time.time() - start
            self.logger.error(
                f"{method} {endpoint} failed",
                extra={"duration_ms": duration * 1000, "error": str(e)}
            )
            raise

    def close(self):
        """Close the HTTP client connection pool."""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
```

### Pattern 2: Rate Limit Header Parsing (Pexels)
**What:** Extract rate limit information from response headers and log/warn before limits exceeded
**When to use:** APIs that provide rate limit headers (X-Ratelimit-*)

**Example:**
```python
# Source: https://help.pexels.com/hc/en-us/articles/900005368726
def _check_rate_limits(self, response: httpx.Response):
    """Parse and log Pexels rate limit headers."""
    limit = response.headers.get("X-Ratelimit-Limit")
    remaining = response.headers.get("X-Ratelimit-Remaining")
    reset = response.headers.get("X-Ratelimit-Reset")

    if remaining and int(remaining) < 10:
        self.logger.warning(
            "Approaching rate limit",
            extra={
                "remaining": remaining,
                "limit": limit,
                "reset_timestamp": reset
            }
        )

    return {
        "limit": limit,
        "remaining": remaining,
        "reset": reset
    }
```

### Pattern 3: Streaming Download for Large Files
**What:** Download files in chunks to avoid loading entire file into memory
**When to use:** Downloading videos, large images, or any file >10MB

**Example:**
```python
# Source: https://realpython.com/python-download-file-from-url/
import requests
from pathlib import Path

def download_file(url: str, destination: Path, chunk_size: int = 8192):
    """Download file with streaming to handle large files efficiently."""
    with requests.get(url, stream=True) as response:
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0

        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                f.write(chunk)
                downloaded += len(chunk)

                # Optional: log progress for large files
                if total_size and downloaded % (1024 * 1024) == 0:  # Every 1MB
                    progress = (downloaded / total_size) * 100
                    logging.info(f"Download progress: {progress:.1f}%")
```

### Pattern 4: Environment Variable Configuration
**What:** Load API keys from environment variables, never hardcode secrets
**When to use:** Always, for all API clients

**Example:**
```python
# Source: https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if exists (development)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

class Settings:
    """Application settings loaded from environment variables."""

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    PEXELS_API_KEY: str = os.getenv("PEXELS_API_KEY", "")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

    def validate(self):
        """Validate all required API keys are present."""
        missing = []
        for key in ["GEMINI_API_KEY", "PEXELS_API_KEY", "SUPABASE_URL", "SUPABASE_KEY"]:
            if not getattr(self, key):
                missing.append(key)

        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

settings = Settings()
```

### Pattern 5: Resumable Upload with TUS (Supabase)
**What:** Use TUS protocol for uploading large files with automatic resume capability
**When to use:** Uploading files >6MB to Supabase Storage

**Example:**
```python
# Source: https://supabase.com/docs/guides/storage/uploads/resumable-uploads
from tusclient import client as tus_client

def upload_large_file(file_path: str, bucket_name: str, destination_path: str):
    """Upload large file to Supabase using TUS resumable protocol."""
    # Construct TUS endpoint using direct storage hostname
    project_id = settings.SUPABASE_URL.split("//")[1].split(".")[0]
    tus_endpoint = f"https://{project_id}.storage.supabase.co/upload/resumable"

    # Initialize TUS client with Supabase auth
    client = tus_client.TusClient(
        tus_endpoint,
        headers={
            "Authorization": f"Bearer {settings.SUPABASE_KEY}",
            "x-upsert": "true"  # Overwrite if exists
        }
    )

    # Upload with 5MB chunks (recommended for large files)
    uploader = client.uploader(file_path, chunk_size=5 * 1024 * 1024)
    uploader.upload()

    return uploader.url
```

### Pattern 6: Gemini Rate Limit Handling
**What:** Handle 429 errors with exponential backoff, respecting new December 2025 limits
**When to use:** All Gemini API calls (5 RPM free tier since Dec 2025)

**Example:**
```python
# Source: https://ai.google.dev/gemini-api/docs/quickstart
from google import genai
import backoff

class GeminiClient:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.logger = logging.getLogger(__name__)

    @backoff.on_exception(
        backoff.expo,
        Exception,
        max_tries=8,
        max_time=300,  # 5 minutes max
        giveup=lambda e: "429" not in str(e),  # Only retry on 429
        on_backoff=lambda details: logging.warning(
            "Gemini rate limit hit, backing off",
            extra={"wait_seconds": details['wait'], "tries": details['tries']}
        )
    )
    def generate_text(self, prompt: str, model: str = "gemini-2.0-flash-exp") -> str:
        """Generate text with automatic 429 retry handling."""
        response = self.client.models.generate_content(
            model=model,
            contents=prompt
        )
        return response.text
```

### Anti-Patterns to Avoid

- **Hardcoding API keys in code**: Always use environment variables, never commit keys to version control
- **Loading entire response into memory**: Use streaming for files, especially videos from Pexels
- **Ignoring rate limit headers**: Parse and respect X-Ratelimit-* headers to avoid hitting limits
- **Using requests in async contexts**: Use httpx or aiohttp for async code, not requests
- **Not setting timeouts**: Always set explicit timeouts to prevent hanging connections
- **Creating new HTTP client per request**: Use client instances with connection pooling
- **Retry on 4xx client errors**: Only retry 429, 5xx, and network errors; 400, 401, 404 should fail immediately
- **No jitter in backoff**: Always use jitter to prevent thundering herd problem

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Exponential backoff | Custom sleep calculations | `backoff` library | Handles jitter, max time, conditional retry, logging hooks |
| Resumable uploads | Custom chunking logic | `tuspy` (TUS protocol) | Handles resume from interruption, chunk tracking, metadata |
| HTTP connection pooling | Session management | `httpx.Client()` or `requests.Session()` | Reuses TCP connections, manages timeouts, thread-safe |
| Text-to-speech | Audio processing pipeline | `edge-tts` library | Free, 100+ neural voices, SSML support, no API key |
| API key management | Custom config loading | `python-dotenv` + env vars | Standard pattern, .gitignore compatible, 12-factor app |
| Structured logging | String formatting | `structlog` | JSON output, async-safe, context preservation, filterable |
| Rate limit parsing | Custom header extraction | Parse X-Ratelimit-* headers | Standard across APIs (Pexels, GitHub, etc.) |

**Key insight:** API client development has well-established patterns for retry logic, streaming, and connection management. Custom implementations almost always miss edge cases (connection pooling cleanup, jitter to prevent thundering herd, proper exception hierarchies). Use battle-tested libraries.

## Common Pitfalls

### Pitfall 1: Gemini Free Tier Rate Limits (Dec 2025 Changes)
**What goes wrong:** Applications suddenly fail with 429 errors after working fine previously
**Why it happens:** Google reduced free tier from 15 RPM to 5 RPM on Dec 7, 2025, without major announcement
**How to avoid:**
- Implement exponential backoff with 8+ retries and 5-minute max_time
- Add logging to track retry attempts
- Consider request batching or queueing for high-volume scenarios
- Monitor daily limits (RPD) in addition to per-minute (RPM)

**Warning signs:**
- 429 errors in logs
- "quota exceeded" messages
- Successful requests suddenly failing

### Pitfall 2: Pexels Video Download Memory Exhaustion
**What goes wrong:** Application crashes or becomes unresponsive when downloading HD/4K videos
**Why it happens:** Loading entire video into memory before writing to disk; Pexels videos can be 50-500MB
**How to avoid:**
- Always use `stream=True` in requests.get()
- Use `iter_content(chunk_size=8192)` to process in chunks
- Write chunks to disk immediately, don't accumulate in memory

**Warning signs:**
- High memory usage during downloads
- Out of memory errors
- Slow download completion

### Pitfall 3: Edge-TTS Service Blocking
**What goes wrong:** TTS requests fail or are blocked by Microsoft
**Why it happens:** Too frequent requests without delays, Microsoft detects automated usage patterns
**How to avoid:**
- Add small delays between TTS requests (0.5-1 second)
- Don't make parallel requests to Edge-TTS
- Cache generated audio files to avoid regenerating same text

**Warning signs:**
- TTS requests timing out
- Connection refused errors
- Intermittent failures

### Pitfall 4: Supabase Upload Without MIME Type
**What goes wrong:** Files upload successfully but can't be accessed/displayed in browser
**Why it happens:** Supabase defaults to `text/html` if no content-type specified
**How to avoid:**
- Always set `file_options={"content-type": "video/mp4"}` for uploads
- Use Python's `mimetypes` module to detect type automatically
- Verify uploads return correct content-type in response

**Warning signs:**
- Files download instead of playing
- Browser shows wrong file type
- API returns files as text/html

### Pitfall 5: Connection Pool Exhaustion
**What goes wrong:** Requests slow down or timeout after running for a while
**Why it happens:** Creating new HTTP client for each request, not closing connections
**How to avoid:**
- Use `httpx.Client()` or `requests.Session()` with context manager
- Initialize client once, reuse for multiple requests
- Always call `.close()` or use `with` statement

**Warning signs:**
- Increasing request latency over time
- "Connection pool is full" warnings
- File descriptor limit errors

### Pitfall 6: API Keys in Version Control
**What goes wrong:** API keys leaked in git history, potential security breach/cost
**Why it happens:** Forgetting to add .env to .gitignore, committing keys directly in code
**How to avoid:**
- Add `.env` to `.gitignore` immediately when creating repo
- Use environment variables exclusively, never hardcode keys
- Audit git history before first commit: `git log -p | grep -i "api_key"`
- Use pre-commit hooks to scan for secrets

**Warning signs:**
- Keys visible in GitHub/GitLab UI
- Unexpected API usage charges
- Security alerts from git hosting provider

### Pitfall 7: Not Handling Partial Failures
**What goes wrong:** Entire batch fails if one API call fails, no retry for individual items
**Why it happens:** Processing multiple items in single try/except without granular error handling
**How to avoid:**
- Wrap individual API calls in try/except, not entire batch
- Log failures with context (which item failed)
- Return partial results with error details
- Consider dead-letter queue pattern for failed items

**Warning signs:**
- All-or-nothing behavior in batch operations
- Lost work when one request fails
- No visibility into which items failed

## Code Examples

Verified patterns from official sources:

### Gemini Text Generation
```python
# Source: https://ai.google.dev/gemini-api/docs/quickstart
from google import genai
import os

# Initialize client (picks up GEMINI_API_KEY from environment)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Generate text
response = client.models.generate_content(
    model="gemini-2.0-flash-exp",
    contents="Write a short video script about space exploration"
)

print(response.text)
```

### Pexels Video Search
```python
# Source: https://www.pexels.com/api/documentation/ (via WebSearch findings)
import requests

class PexelsClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.pexels.com/videos"
        self.session = requests.Session()
        self.session.headers.update({"Authorization": api_key})

    def search_videos(self, query: str, per_page: int = 15):
        """Search for videos matching query."""
        response = self.session.get(
            f"{self.base_url}/search",
            params={"query": query, "per_page": per_page}
        )
        response.raise_for_status()

        # Log rate limits
        self.logger.info(
            "Pexels rate limit status",
            extra={
                "remaining": response.headers.get("X-Ratelimit-Remaining"),
                "limit": response.headers.get("X-Ratelimit-Limit")
            }
        )

        return response.json()
```

### Edge-TTS Audio Generation
```python
# Source: https://github.com/rany2/edge-tts
import asyncio
import edge_tts

async def generate_audio(text: str, output_path: str, voice: str = "en-US-AriaNeural"):
    """Generate audio file from text using Edge-TTS."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

# Sync wrapper for use in non-async code
def generate_audio_sync(text: str, output_path: str, voice: str = "en-US-AriaNeural"):
    asyncio.run(generate_audio(text, output_path, voice))

# List available voices
async def list_voices():
    voices = await edge_tts.list_voices()
    for voice in voices:
        print(f"{voice['Name']} - {voice['Gender']}")
```

### Supabase Storage Upload with Public URL
```python
# Source: https://supabase.com/docs/reference/python/storage-from-upload
from supabase import create_client

# Initialize Supabase client
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Upload file with correct MIME type
with open("video.mp4", "rb") as f:
    response = supabase.storage.from_("videos").upload(
        path="outputs/video.mp4",
        file=f,
        file_options={"content-type": "video/mp4", "upsert": "true"}
    )

# Get public URL (bucket must be public)
public_url = supabase.storage.from_("videos").get_public_url("outputs/video.mp4")
print(f"Video available at: {public_url}")
```

### Streaming File Download
```python
# Source: https://realpython.com/python-download-file-from-url/
import requests
from pathlib import Path

def download_video(url: str, destination: Path):
    """Download video file with progress logging."""
    with requests.get(url, stream=True, timeout=60) as response:
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0

        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)

                # Log every 5MB
                if downloaded % (5 * 1024 * 1024) < 8192:
                    percentage = (downloaded / total_size * 100) if total_size else 0
                    print(f"Downloaded {downloaded / (1024*1024):.1f}MB ({percentage:.1f}%)")
```

### Backoff with Custom Logging
```python
# Source: https://pypi.org/project/backoff/
import backoff
import logging

def log_backoff(details):
    """Custom backoff event handler."""
    logging.warning(
        "Backing off {wait:0.1f} seconds after {tries} tries "
        "calling function {target} with args {args} and kwargs {kwargs}".format(**details)
    )

def log_giveup(details):
    """Custom giveup event handler."""
    logging.error(
        "Gave up after {tries} tries calling function {target}".format(**details)
    )

@backoff.on_exception(
    backoff.expo,
    requests.exceptions.RequestException,
    max_tries=8,
    max_time=60,
    on_backoff=log_backoff,
    on_giveup=log_giveup
)
def api_call_with_retry():
    response = requests.get("https://api.example.com/data")
    response.raise_for_status()
    return response.json()
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `google-generativeai` | `google-genai` | May 2025 (GA) | New SDK is official, better performance, async support |
| Gemini 15 RPM free | Gemini 5 RPM free | Dec 7, 2025 | Must implement robust retry, consider paid tier |
| Manual backoff logic | `backoff` library | Established 2022 | Simpler code, battle-tested jitter algorithms |
| `requests` only | `httpx` for new projects | 2024-2026 trend | Async support, HTTP/2, better connection pooling |
| storage-py separate | supabase-py monorepo | 2024 | Single dependency, unified API |

**Deprecated/outdated:**
- `google-generativeai` library: Use `google-genai` instead (new official SDK as of May 2025)
- `pypexels` library: Last updated 2023, use direct requests to Pexels API with current wrapper
- Assuming high free tier limits: Gemini reduced to 5 RPM in Dec 2025
- Standard uploads for large files: Use TUS resumable for files >6MB

## Open Questions

Things that couldn't be fully resolved:

1. **Pexels Python SDK Status**
   - What we know: `python-pexels` library exists but last updated Jan 2023, may not reflect current API
   - What's unclear: Whether library handles rate limit headers correctly, if it's actively maintained
   - Recommendation: Build thin wrapper around `requests` directly, verify rate limit header parsing

2. **Edge-TTS Rate Limiting**
   - What we know: Service can block excessive usage, needs delays between requests
   - What's unclear: Exact thresholds for blocking, recommended request frequency
   - Recommendation: Start with 1-second delays, monitor for failures, increase if needed

3. **Gemini Error Response Format**
   - What we know: 429 errors occur when rate limits exceeded, backoff needed
   - What's unclear: Exact error message format, whether SDK exposes rate limit info
   - Recommendation: Log full exception details during testing to understand error structure

4. **Supabase TUS Upload Progress**
   - What we know: TUS protocol supports resumable uploads via `tuspy`
   - What's unclear: How to get upload progress callbacks for UI progress bars
   - Recommendation: Check `tuspy` docs for progress callbacks, or calculate from chunk_size

## Sources

### Primary (HIGH confidence)
- [Google GenAI SDK PyPI](https://pypi.org/project/google-genai/) - v1.60.0, Jan 2026
- [Gemini API Quickstart](https://ai.google.dev/gemini-api/docs/quickstart) - Official docs
- [Supabase Python Client PyPI](https://pypi.org/project/supabase/) - v2.27.2, Jan 2026
- [Supabase Storage Upload Reference](https://supabase.com/docs/reference/python/storage-from-upload) - Official docs
- [Supabase Resumable Uploads](https://supabase.com/docs/guides/storage/uploads/resumable-uploads) - TUS protocol guide
- [Edge-TTS PyPI](https://pypi.org/project/edge-tts/) - v7.2.7, Dec 2025
- [Edge-TTS GitHub](https://github.com/rany2/edge-tts) - Official repository
- [Backoff PyPI](https://pypi.org/project/backoff/) - v2.2.1, documented patterns
- [HTTPX Client Documentation](https://www.python-httpx.org/advanced/clients/) - Connection pooling guide
- [TUS Python Client GitHub](https://github.com/tus/tus-py-client) - v1.1.0, Dec 2024

### Secondary (MEDIUM confidence)
- [Gemini API 429 Rate Limit Guide](https://www.aifreeapi.com/en/posts/gemini-api-free-tier-limit) - Community docs, verified Dec 2025 changes
- [Python API Client Design Pattern](https://bhomnick.net/design-pattern-python-api-client/) - Architecture patterns
- [Real Python: Download Files from URLs](https://realpython.com/python-download-file-from-url/) - Streaming patterns
- [Python Secrets Management](https://blog.gitguardian.com/how-to-handle-secrets-in-python/) - API key security
- [HTTPX vs Requests Comparison](https://www.goproxy.com/blog/httpx-vs-requests/) - Library tradeoffs
- [Retry Mechanisms in Python](https://medium.com/@oggy/retry-mechanisms-in-python-practical-guide-with-real-life-examples-ed323e7a8871) - Backoff patterns

### Tertiary (LOW confidence - needs validation)
- [Pexels API Documentation](https://www.pexels.com/api/documentation/) - 403 error on fetch, info from WebSearch only
- [python-pexels PyPI](https://pypi.org/project/python-pexels/) - Last updated Jan 2023, maintenance unclear
- [Pexels Rate Limit Headers](https://help.pexels.com/hc/en-us/articles/900005368726) - 403 error, info from WebSearch

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries verified from PyPI with recent releases, official SDKs confirmed
- Architecture: HIGH - Patterns verified from official docs (Supabase, Google, HTTPX) and authoritative sources
- Pitfalls: MEDIUM - Dec 2025 Gemini changes confirmed from multiple sources, other pitfalls from WebSearch + docs
- Pexels implementation: LOW - No official Python SDK, rate limit header info from WebSearch only (403 on docs)

**Research date:** 2026-01-23
**Valid until:** 2026-02-23 (30 days - Gemini API stability, library updates)
**Re-verify if:** Gemini rate limits change again, new official Pexels SDK released, Supabase storage API updates
