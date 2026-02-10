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
            self.check_gemini(),
            self.check_pexels(),
            self.check_creatomate(),
            self.check_resend(),
            self.check_convertkit(),
            self.check_youtube(),
            self.check_make_webhook(),
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
            import google.generativeai as genai
            genai.configure(api_key=config.gemini_api_key)

            start = datetime.now()
            # Simple test generation
            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(
                "Say 'ok'",
                generation_config=genai.GenerationConfig(max_output_tokens=10)
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

    def check_make_webhook(self) -> HealthCheckResult:
        """Check Make.com webhook (Pinterest)."""
        config = get_config()

        if not config.make_com_pinterest_webhook:
            return HealthCheckResult(
                service="make_webhook",
                status="degraded",
                error="MAKE_COM_PINTEREST_WEBHOOK not configured"
            )

        # Note: We can't actually test the webhook without triggering it
        # Just verify the URL is valid
        webhook_url = config.make_com_pinterest_webhook

        if webhook_url.startswith("https://hook."):
            return HealthCheckResult(
                service="make_webhook",
                status="healthy",
                details={"webhook_configured": True}
            )
        else:
            return HealthCheckResult(
                service="make_webhook",
                status="degraded",
                error="Webhook URL format appears invalid"
            )

    def check_critical_only(self) -> dict:
        """Check only critical services (faster)."""
        checks = [
            self.check_supabase(),
            self.check_gemini(),
            self.check_pexels(),
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
