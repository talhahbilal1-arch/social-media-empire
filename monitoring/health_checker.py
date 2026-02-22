"""Health checking for all Social Media Empire services and APIs."""

import logging
from datetime import datetime, timezone
from typing import Optional
from dataclasses import dataclass, field
import requests

from utils.config import get_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class HealthCheckResult:
    """Result of a single health check."""
    service: str
    status: str  # "healthy", "degraded", "unhealthy"
    response_time_ms: Optional[float] = None
    error: Optional[str] = None
    details: dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class HealthChecker:
    """Checks health of all integrated services."""

    timeout_seconds: int = 10

    def check_all(self) -> dict:
        """Run all health checks and return summary."""
        checks = [
            self.check_anthropic(),
            self.check_supabase(),
            self.check_supabase_tiktok(),
            self.check_gemini(),
            self.check_pexels(),
            self.check_pexels_video(),
            self.check_creatomate(),
            self.check_resend(),
            self.check_convertkit(),
            self.check_youtube(),
            self.check_make_webhook_deals(),
            self.check_make_webhook_menopause(),
            self.check_late_api(),
            self.check_elevenlabs(),
            self.check_netlify(),
            self.check_github_api(),
            self.check_website_dailydealdarling(),
            self.check_website_fitover35(),
        ]

        # Summarize
        healthy = sum(1 for c in checks if c.status == "healthy")
        degraded = sum(1 for c in checks if c.status == "degraded")
        unhealthy = sum(1 for c in checks if c.status == "unhealthy")

        overall_status = "healthy"
        if unhealthy > 0:
            overall_status = "unhealthy"
        elif degraded > 0:
            overall_status = "degraded"

        return {
            "overall_status": overall_status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "healthy": healthy,
                "degraded": degraded,
                "unhealthy": unhealthy,
                "total": len(checks)
            },
            "checks": [
                {
                    "service": c.service,
                    "status": c.status,
                    "response_time_ms": c.response_time_ms,
                    "error": c.error,
                    "details": c.details
                }
                for c in checks
            ]
        }

    def check_supabase(self) -> HealthCheckResult:
        """Check Supabase database connectivity."""
        config = get_config()

        if not config.supabase_url:
            return HealthCheckResult(
                service="supabase",
                status="unhealthy",
                error="SUPABASE_URL not configured"
            )

        try:
            start = datetime.now()
            # Health check endpoint
            response = requests.get(
                f"{config.supabase_url}/rest/v1/",
                headers={
                    "apikey": config.supabase_key,
                    "Authorization": f"Bearer {config.supabase_key}"
                },
                timeout=self.timeout_seconds
            )
            response_time = (datetime.now() - start).total_seconds() * 1000

            if response.status_code in [200, 204]:
                return HealthCheckResult(
                    service="supabase",
                    status="healthy",
                    response_time_ms=response_time
                )
            else:
                return HealthCheckResult(
                    service="supabase",
                    status="degraded",
                    response_time_ms=response_time,
                    error=f"Status code: {response.status_code}"
                )

        except Exception as e:
            return HealthCheckResult(
                service="supabase",
                status="unhealthy",
                error=str(e)
            )

    def check_anthropic(self) -> HealthCheckResult:
        """Check Anthropic Claude API (primary AI dependency)."""
        import os
        api_key = os.environ.get('ANTHROPIC_API_KEY', '')

        if not api_key:
            return HealthCheckResult(
                service="anthropic",
                status="unhealthy",
                error="ANTHROPIC_API_KEY not configured"
            )

        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)

            start = datetime.now()
            resp = client.messages.create(
                model='claude-sonnet-4-5-20250929',
                max_tokens=10,
                messages=[{'role': 'user', 'content': 'ping'}]
            )
            response_time = (datetime.now() - start).total_seconds() * 1000

            if resp.content:
                return HealthCheckResult(
                    service="anthropic",
                    status="healthy",
                    response_time_ms=response_time
                )
            else:
                return HealthCheckResult(
                    service="anthropic",
                    status="degraded",
                    response_time_ms=response_time,
                    error="Empty response"
                )

        except Exception as e:
            return HealthCheckResult(
                service="anthropic",
                status="unhealthy",
                error=str(e)
            )

    def check_gemini(self) -> HealthCheckResult:
        """Check Google Gemini API."""
        config = get_config()

        if not config.gemini_api_key:
            return HealthCheckResult(
                service="gemini",
                status="unhealthy",
                error="GEMINI_API_KEY not configured"
            )

        try:
            from google import genai

            client = genai.Client(api_key=config.gemini_api_key)

            start = datetime.now()
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents="Say 'ok'",
            )
            response_time = (datetime.now() - start).total_seconds() * 1000

            if response.text:
                return HealthCheckResult(
                    service="gemini",
                    status="healthy",
                    response_time_ms=response_time
                )
            else:
                return HealthCheckResult(
                    service="gemini",
                    status="degraded",
                    response_time_ms=response_time,
                    error="Empty response"
                )

        except Exception as e:
            return HealthCheckResult(
                service="gemini",
                status="unhealthy",
                error=str(e)
            )

    def check_pexels(self) -> HealthCheckResult:
        """Check Pexels API."""
        config = get_config()

        if not config.pexels_api_key:
            return HealthCheckResult(
                service="pexels",
                status="unhealthy",
                error="PEXELS_API_KEY not configured"
            )

        try:
            start = datetime.now()
            response = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": config.pexels_api_key},
                params={"query": "test", "per_page": 1},
                timeout=self.timeout_seconds
            )
            response_time = (datetime.now() - start).total_seconds() * 1000

            if response.status_code == 200:
                data = response.json()
                return HealthCheckResult(
                    service="pexels",
                    status="healthy",
                    response_time_ms=response_time,
                    details={"photos_found": len(data.get("photos", []))}
                )
            else:
                return HealthCheckResult(
                    service="pexels",
                    status="unhealthy",
                    response_time_ms=response_time,
                    error=f"Status code: {response.status_code}"
                )

        except Exception as e:
            return HealthCheckResult(
                service="pexels",
                status="unhealthy",
                error=str(e)
            )

    def check_creatomate(self) -> HealthCheckResult:
        """Check Creatomate API."""
        config = get_config()

        if not config.creatomate_api_key:
            return HealthCheckResult(
                service="creatomate",
                status="degraded",
                error="CREATOMATE_API_KEY not configured"
            )

        try:
            start = datetime.now()
            response = requests.get(
                "https://api.creatomate.com/v1/templates",
                headers={"Authorization": f"Bearer {config.creatomate_api_key}"},
                timeout=self.timeout_seconds
            )
            response_time = (datetime.now() - start).total_seconds() * 1000

            if response.status_code == 200:
                return HealthCheckResult(
                    service="creatomate",
                    status="healthy",
                    response_time_ms=response_time
                )
            else:
                return HealthCheckResult(
                    service="creatomate",
                    status="degraded",
                    response_time_ms=response_time,
                    error=f"Status code: {response.status_code}"
                )

        except Exception as e:
            return HealthCheckResult(
                service="creatomate",
                status="unhealthy",
                error=str(e)
            )

    def check_resend(self) -> HealthCheckResult:
        """Check Resend email API."""
        config = get_config()

        if not config.resend_api_key:
            return HealthCheckResult(
                service="resend",
                status="degraded",
                error="RESEND_API_KEY not configured"
            )

        try:
            start = datetime.now()
            response = requests.get(
                "https://api.resend.com/domains",
                headers={"Authorization": f"Bearer {config.resend_api_key}"},
                timeout=self.timeout_seconds
            )
            response_time = (datetime.now() - start).total_seconds() * 1000

            if response.status_code == 200:
                return HealthCheckResult(
                    service="resend",
                    status="healthy",
                    response_time_ms=response_time
                )
            else:
                return HealthCheckResult(
                    service="resend",
                    status="degraded",
                    response_time_ms=response_time,
                    error=f"Status code: {response.status_code}"
                )

        except Exception as e:
            return HealthCheckResult(
                service="resend",
                status="unhealthy",
                error=str(e)
            )

    def check_convertkit(self) -> HealthCheckResult:
        """Check ConvertKit API."""
        config = get_config()

        if not config.convertkit_api_key:
            return HealthCheckResult(
                service="convertkit",
                status="degraded",
                error="CONVERTKIT_API_KEY not configured"
            )

        try:
            start = datetime.now()
            response = requests.get(
                "https://api.convertkit.com/v3/account",
                params={"api_secret": config.convertkit_api_secret or config.convertkit_api_key},
                timeout=self.timeout_seconds
            )
            response_time = (datetime.now() - start).total_seconds() * 1000

            if response.status_code == 200:
                return HealthCheckResult(
                    service="convertkit",
                    status="healthy",
                    response_time_ms=response_time
                )
            else:
                return HealthCheckResult(
                    service="convertkit",
                    status="degraded",
                    response_time_ms=response_time,
                    error=f"Status code: {response.status_code}"
                )

        except Exception as e:
            return HealthCheckResult(
                service="convertkit",
                status="unhealthy",
                error=str(e)
            )

    def check_youtube(self) -> HealthCheckResult:
        """Check YouTube API (OAuth)."""
        config = get_config()

        if not config.youtube_refresh_token:
            return HealthCheckResult(
                service="youtube",
                status="degraded",
                error="YOUTUBE_REFRESH_TOKEN not configured"
            )

        try:
            # Try to refresh the access token
            start = datetime.now()
            response = requests.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": config.youtube_client_id,
                    "client_secret": config.youtube_client_secret,
                    "refresh_token": config.youtube_refresh_token,
                    "grant_type": "refresh_token"
                },
                timeout=self.timeout_seconds
            )
            response_time = (datetime.now() - start).total_seconds() * 1000

            if response.status_code == 200:
                return HealthCheckResult(
                    service="youtube",
                    status="healthy",
                    response_time_ms=response_time
                )
            else:
                return HealthCheckResult(
                    service="youtube",
                    status="unhealthy",
                    response_time_ms=response_time,
                    error=f"Token refresh failed: {response.status_code}"
                )

        except Exception as e:
            return HealthCheckResult(
                service="youtube",
                status="unhealthy",
                error=str(e)
            )

    def _check_make_webhook(self, name: str, webhook_url: str) -> HealthCheckResult:
        """Check a Make.com webhook URL is valid and reachable."""
        if not webhook_url:
            return HealthCheckResult(
                service=name,
                status="degraded",
                error=f"{name} webhook not configured"
            )

        if not webhook_url.startswith("https://"):
            return HealthCheckResult(
                service=name,
                status="degraded",
                error="Webhook URL format appears invalid"
            )

        # Verify the URL is reachable with a HEAD request (won't trigger the scenario)
        try:
            start = datetime.now()
            response = requests.head(webhook_url, timeout=self.timeout_seconds, allow_redirects=True)
            response_time = (datetime.now() - start).total_seconds() * 1000

            # Make.com webhooks return 200 on HEAD when active
            if response.status_code in [200, 204, 405]:
                return HealthCheckResult(
                    service=name,
                    status="healthy",
                    response_time_ms=response_time,
                    details={"webhook_configured": True}
                )
            else:
                return HealthCheckResult(
                    service=name,
                    status="degraded",
                    response_time_ms=response_time,
                    error=f"Webhook returned status {response.status_code}"
                )
        except Exception as e:
            return HealthCheckResult(
                service=name,
                status="unhealthy",
                error=str(e)
            )

    def check_make_webhook_deals(self) -> HealthCheckResult:
        """Check Make.com webhook for Daily Deal Darling Pinterest posting."""
        config = get_config()
        return self._check_make_webhook("make_webhook_deals", config.make_webhook_deals)

    def check_make_webhook_menopause(self) -> HealthCheckResult:
        """Check Make.com webhook for Menopause Planner Pinterest posting."""
        config = get_config()
        return self._check_make_webhook("make_webhook_menopause", config.make_webhook_menopause)

    def check_late_api(self) -> HealthCheckResult:
        """Check Late API keys used for Pinterest posting across all brands.

        Checks all configured Late API keys (LATE_API_KEY through LATE_API_KEY_4)
        since each brand uses a different key.
        """
        import os
        config = get_config()

        # Map of brand to their Late API key env var
        key_map = {
            "primary": ("LATE_API_KEY", config.late_api_key),
            "deals": ("LATE_API_KEY_2", os.environ.get("LATE_API_KEY_2", "")),
            "fitness": ("LATE_API_KEY_3", os.environ.get("LATE_API_KEY_3", "")),
            "menopause": ("LATE_API_KEY_4", os.environ.get("LATE_API_KEY_4", "")),
        }

        configured_keys = {name: (env, key) for name, (env, key) in key_map.items() if key}

        if not configured_keys:
            return HealthCheckResult(
                service="late_api",
                status="unhealthy",
                error="No Late API keys configured (need at least LATE_API_KEY)",
                details={"keys_checked": list(key_map.keys()), "keys_configured": 0}
            )

        healthy_keys = []
        failed_keys = []

        for name, (env_var, key) in configured_keys.items():
            try:
                response = requests.get(
                    "https://getlate.dev/api/v1/accounts",
                    headers={"Authorization": f"Bearer {key}"},
                    timeout=self.timeout_seconds
                )
                if response.status_code == 200:
                    healthy_keys.append(name)
                else:
                    failed_keys.append(f"{name}({env_var}): HTTP {response.status_code}")
            except Exception as e:
                failed_keys.append(f"{name}({env_var}): {str(e)[:50]}")

        total = len(configured_keys)
        ok = len(healthy_keys)

        if ok == total:
            return HealthCheckResult(
                service="late_api",
                status="healthy",
                details={"keys_healthy": ok, "keys_total": total, "healthy": healthy_keys}
            )
        elif ok > 0:
            return HealthCheckResult(
                service="late_api",
                status="degraded",
                error=f"{len(failed_keys)}/{total} keys failing: {'; '.join(failed_keys)}",
                details={"keys_healthy": ok, "keys_total": total, "failed": failed_keys}
            )
        else:
            return HealthCheckResult(
                service="late_api",
                status="unhealthy",
                error=f"All {total} configured keys failing: {'; '.join(failed_keys)}",
                details={"keys_healthy": 0, "keys_total": total, "failed": failed_keys}
            )

    def check_elevenlabs(self) -> HealthCheckResult:
        """Check ElevenLabs TTS API (used by TikTok pipeline)."""
        config = get_config()

        if not config.elevenlabs_api_key:
            return HealthCheckResult(
                service="elevenlabs",
                status="degraded",
                error="ELEVENLABS_API_KEY not configured"
            )

        try:
            start = datetime.now()
            response = requests.get(
                "https://api.elevenlabs.io/v1/user",
                headers={"xi-api-key": config.elevenlabs_api_key},
                timeout=self.timeout_seconds
            )
            response_time = (datetime.now() - start).total_seconds() * 1000

            if response.status_code == 200:
                data = response.json()
                return HealthCheckResult(
                    service="elevenlabs",
                    status="healthy",
                    response_time_ms=response_time,
                    details={
                        "character_count": data.get("subscription", {}).get("character_count", 0),
                        "character_limit": data.get("subscription", {}).get("character_limit", 0),
                    }
                )
            elif response.status_code == 401:
                return HealthCheckResult(
                    service="elevenlabs",
                    status="unhealthy",
                    response_time_ms=response_time,
                    error="Invalid API key"
                )
            else:
                return HealthCheckResult(
                    service="elevenlabs",
                    status="degraded",
                    response_time_ms=response_time,
                    error=f"Status code: {response.status_code}"
                )

        except Exception as e:
            return HealthCheckResult(
                service="elevenlabs",
                status="unhealthy",
                error=str(e)
            )

    def check_netlify(self) -> HealthCheckResult:
        """Check Netlify deployment API (ToolPilot site)."""
        config = get_config()

        if not config.netlify_api_token:
            return HealthCheckResult(
                service="netlify",
                status="degraded",
                error="NETLIFY_API_TOKEN not configured"
            )

        try:
            start = datetime.now()
            response = requests.get(
                f"https://api.netlify.com/api/v1/sites/{config.netlify_site_id}",
                headers={"Authorization": f"Bearer {config.netlify_api_token}"},
                timeout=self.timeout_seconds
            )
            response_time = (datetime.now() - start).total_seconds() * 1000

            if response.status_code == 200:
                data = response.json()
                return HealthCheckResult(
                    service="netlify",
                    status="healthy",
                    response_time_ms=response_time,
                    details={
                        "site_name": data.get("name", ""),
                        "published_deploy": data.get("published_deploy", {}).get("id", ""),
                        "ssl_url": data.get("ssl_url", ""),
                    }
                )
            elif response.status_code == 401:
                return HealthCheckResult(
                    service="netlify",
                    status="unhealthy",
                    response_time_ms=response_time,
                    error="Invalid API token"
                )
            else:
                return HealthCheckResult(
                    service="netlify",
                    status="degraded",
                    response_time_ms=response_time,
                    error=f"Status code: {response.status_code}"
                )

        except Exception as e:
            return HealthCheckResult(
                service="netlify",
                status="unhealthy",
                error=str(e)
            )

    def check_supabase_tiktok(self) -> HealthCheckResult:
        """Check TikTok Supabase project connectivity and storage."""
        config = get_config()

        if not config.supabase_tiktok_url:
            return HealthCheckResult(
                service="supabase_tiktok",
                status="degraded",
                error="SUPABASE_TIKTOK_URL not configured"
            )

        # Skip if same as main Supabase (already checked)
        if config.supabase_tiktok_url == config.supabase_url:
            return HealthCheckResult(
                service="supabase_tiktok",
                status="healthy",
                details={"shared_with_main": True}
            )

        try:
            start = datetime.now()
            response = requests.get(
                f"{config.supabase_tiktok_url}/rest/v1/",
                headers={
                    "apikey": config.supabase_tiktok_key,
                    "Authorization": f"Bearer {config.supabase_tiktok_key}"
                },
                timeout=self.timeout_seconds
            )
            response_time = (datetime.now() - start).total_seconds() * 1000

            if response.status_code in [200, 204]:
                # Also check storage bucket exists
                storage_ok = True
                try:
                    storage_resp = requests.get(
                        f"{config.supabase_tiktok_url}/storage/v1/bucket/tiktok-media",
                        headers={
                            "apikey": config.supabase_tiktok_key,
                            "Authorization": f"Bearer {config.supabase_tiktok_key}"
                        },
                        timeout=self.timeout_seconds
                    )
                    storage_ok = storage_resp.status_code in [200, 404]  # 404 = bucket may not exist yet
                except Exception:
                    storage_ok = False

                return HealthCheckResult(
                    service="supabase_tiktok",
                    status="healthy" if storage_ok else "degraded",
                    response_time_ms=response_time,
                    details={"storage_accessible": storage_ok},
                    error=None if storage_ok else "Storage bucket check failed"
                )
            else:
                return HealthCheckResult(
                    service="supabase_tiktok",
                    status="degraded",
                    response_time_ms=response_time,
                    error=f"Status code: {response.status_code}"
                )

        except Exception as e:
            return HealthCheckResult(
                service="supabase_tiktok",
                status="unhealthy",
                error=str(e)
            )

    def check_pexels_video(self) -> HealthCheckResult:
        """Check Pexels Video API (used by TikTok pipeline for stock footage)."""
        config = get_config()

        if not config.pexels_api_key:
            return HealthCheckResult(
                service="pexels_video",
                status="unhealthy",
                error="PEXELS_API_KEY not configured"
            )

        try:
            start = datetime.now()
            response = requests.get(
                "https://api.pexels.com/videos/search",
                headers={"Authorization": config.pexels_api_key},
                params={"query": "fitness", "per_page": 1, "orientation": "portrait"},
                timeout=self.timeout_seconds
            )
            response_time = (datetime.now() - start).total_seconds() * 1000

            if response.status_code == 200:
                data = response.json()
                videos_found = len(data.get("videos", []))
                return HealthCheckResult(
                    service="pexels_video",
                    status="healthy" if videos_found > 0 else "degraded",
                    response_time_ms=response_time,
                    details={"videos_found": videos_found},
                    error=None if videos_found > 0 else "No portrait videos returned"
                )
            else:
                return HealthCheckResult(
                    service="pexels_video",
                    status="unhealthy",
                    response_time_ms=response_time,
                    error=f"Status code: {response.status_code}"
                )

        except Exception as e:
            return HealthCheckResult(
                service="pexels_video",
                status="unhealthy",
                error=str(e)
            )

    def check_github_api(self) -> HealthCheckResult:
        """Check GitHub API accessibility (used by emergency alert and workflow guardian)."""
        config = get_config()

        if not config.github_token:
            return HealthCheckResult(
                service="github_api",
                status="degraded",
                error="GITHUB_TOKEN not configured"
            )

        try:
            start = datetime.now()
            response = requests.get(
                "https://api.github.com/rate_limit",
                headers={
                    "Authorization": f"Bearer {config.github_token}",
                    "Accept": "application/vnd.github+json"
                },
                timeout=self.timeout_seconds
            )
            response_time = (datetime.now() - start).total_seconds() * 1000

            if response.status_code == 200:
                data = response.json()
                core_remaining = data.get("resources", {}).get("core", {}).get("remaining", 0)
                core_limit = data.get("resources", {}).get("core", {}).get("limit", 0)

                if core_remaining < 100:
                    return HealthCheckResult(
                        service="github_api",
                        status="degraded",
                        response_time_ms=response_time,
                        error=f"Low rate limit remaining: {core_remaining}/{core_limit}",
                        details={"remaining": core_remaining, "limit": core_limit}
                    )

                return HealthCheckResult(
                    service="github_api",
                    status="healthy",
                    response_time_ms=response_time,
                    details={"remaining": core_remaining, "limit": core_limit}
                )
            elif response.status_code == 401:
                return HealthCheckResult(
                    service="github_api",
                    status="unhealthy",
                    response_time_ms=response_time,
                    error="Invalid GitHub token"
                )
            else:
                return HealthCheckResult(
                    service="github_api",
                    status="degraded",
                    response_time_ms=response_time,
                    error=f"Status code: {response.status_code}"
                )

        except Exception as e:
            return HealthCheckResult(
                service="github_api",
                status="unhealthy",
                error=str(e)
            )

    def _check_website_uptime(self, name: str, url: str, min_size: int = 1000) -> HealthCheckResult:
        """Check that a website is up and serving real content (not blank/error)."""
        try:
            start = datetime.now()
            response = requests.get(url, timeout=self.timeout_seconds, allow_redirects=True)
            response_time = (datetime.now() - start).total_seconds() * 1000

            body_size = len(response.content)

            if response.status_code != 200:
                return HealthCheckResult(
                    service=name,
                    status="unhealthy",
                    response_time_ms=response_time,
                    error=f"HTTP {response.status_code}",
                    details={"body_size": body_size}
                )

            if body_size < min_size:
                return HealthCheckResult(
                    service=name,
                    status="unhealthy",
                    response_time_ms=response_time,
                    error=f"Page is only {body_size} bytes (expected >{min_size}) - site may be blank or broken",
                    details={"body_size": body_size}
                )

            # Check that it looks like actual HTML content
            content_start = response.text[:200].lower()
            if "<!doctype html" not in content_start and "<html" not in content_start:
                return HealthCheckResult(
                    service=name,
                    status="degraded",
                    response_time_ms=response_time,
                    error="Response doesn't appear to be HTML",
                    details={"body_size": body_size}
                )

            return HealthCheckResult(
                service=name,
                status="healthy",
                response_time_ms=response_time,
                details={"body_size": body_size}
            )

        except Exception as e:
            return HealthCheckResult(
                service=name,
                status="unhealthy",
                error=str(e)
            )

    def check_website_dailydealdarling(self) -> HealthCheckResult:
        """Check that dailydealdarling.com is up and serving real content."""
        return self._check_website_uptime(
            "website_dailydealdarling",
            "https://dailydealdarling.com",
            min_size=5000
        )

    def check_website_fitover35(self) -> HealthCheckResult:
        """Check that fitover35.com is up and serving real content."""
        return self._check_website_uptime(
            "website_fitover35",
            "https://fitover35.com",
            min_size=5000
        )

    def check_critical_only(self) -> dict:
        """Check only critical services for pin posting pipeline (faster)."""
        checks = [
            self.check_anthropic(),
            self.check_supabase(),
            self.check_pexels(),
            self.check_late_api(),
        ]

        healthy = all(c.status == "healthy" for c in checks)

        return {
            "healthy": healthy,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checks": [
                {"service": c.service, "status": c.status, "error": c.error}
                for c in checks
            ]
        }


def run_health_check(full: bool = True) -> dict:
    """Run health checks and return results."""
    checker = HealthChecker()

    if full:
        return checker.check_all()
    else:
        return checker.check_critical_only()


def main():
    """CLI entry point for health checking."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Check service health")
    parser.add_argument("--full", action="store_true", help="Run full health check")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    result = run_health_check(full=args.full)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n{'='*50}")
        print(f"HEALTH CHECK - {result.get('timestamp', 'Unknown')}")
        print(f"{'='*50}")
        print(f"Overall Status: {result.get('overall_status', 'unknown').upper()}")
        print(f"\nSummary:")
        summary = result.get('summary', {})
        print(f"  Healthy: {summary.get('healthy', 0)}")
        print(f"  Degraded: {summary.get('degraded', 0)}")
        print(f"  Unhealthy: {summary.get('unhealthy', 0)}")

        print(f"\nDetails:")
        for check in result.get('checks', []):
            status_icon = "✓" if check['status'] == "healthy" else "!" if check['status'] == "degraded" else "✗"
            print(f"  {status_icon} {check['service']}: {check['status']}")
            if check.get('error'):
                print(f"      Error: {check['error']}")
            if check.get('response_time_ms'):
                print(f"      Response: {check['response_time_ms']:.0f}ms")


if __name__ == "__main__":
    main()
