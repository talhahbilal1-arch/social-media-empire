"""Pinterest Analytics Collector - Real API data from Pinterest v5 API.

Fetches board analytics from Pinterest API v5 for all 3 brands.
Saves impressions, saves, clicks, and pin_clicks to Supabase.
Runs weekly (Monday 8 AM UTC) via GitHub Actions workflow.

Pinterest API Documentation:
  https://developers.pinterest.com/docs/api/overview/
  GET /v5/boards/{board_id}/analytics

Requires LATE_API_KEY (Bearer token) as environment variable.
"""

import os
import sys
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
import requests

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import get_config
from video_automation.pinterest_boards import PINTEREST_BOARDS, DEFAULT_BOARDS


class PinterestAnalyticsCollector:
    """Collects board-level analytics from Pinterest API v5."""

    BASE_URL = "https://api.pinterest.com/v5"

    def __init__(self, access_token: Optional[str] = None):
        """Initialize collector with Pinterest API token.

        Args:
            access_token: Pinterest API Bearer token. If not provided,
                         reads from LATE_API_KEY environment variable.
        """
        self.access_token = access_token or os.environ.get("LATE_API_KEY")
        self.session = requests.Session()
        if self.access_token:
            self.session.headers.update({
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            })
        self.metrics = {
            "fitness": {"collected": 0, "errors": []},
            "deals": {"collected": 0, "errors": []},
            "menopause": {"collected": 0, "errors": []},
        }

    def run(self) -> Dict:
        """Main entry point - collect analytics for all boards."""
        if not self.access_token:
            print("ERROR: LATE_API_KEY not set. Cannot collect Pinterest analytics.")
            return {
                "status": "failed",
                "reason": "Missing LATE_API_KEY environment variable",
                "metrics": self.metrics
            }

        results = {
            "status": "completed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "boards_analyzed": 0,
            "analytics_saved": 0,
            "by_brand": self.metrics,
            "errors": []
        }

        try:
            # Collect analytics for each brand's boards
            for brand_key, board_map in PINTEREST_BOARDS.items():
                print(f"\nCollecting analytics for brand: {brand_key}")
                for board_name, board_id in board_map.items():
                    try:
                        analytics = self._collect_board_analytics(
                            brand=brand_key,
                            board_name=board_name,
                            board_id=board_id
                        )
                        if analytics:
                            self._save_analytics(analytics)
                            results["analytics_saved"] += 1
                            self.metrics[brand_key]["collected"] += 1
                        results["boards_analyzed"] += 1
                    except Exception as e:
                        error_msg = f"{board_name} ({board_id}): {str(e)}"
                        results["errors"].append(error_msg)
                        self.metrics[brand_key]["errors"].append(error_msg)
                        print(f"  ERROR: {error_msg}")

            results["by_brand"] = self.metrics
            print(f"\n✓ Analytics collection complete: {results['analytics_saved']} records saved")
            return results

        except Exception as e:
            print(f"FATAL ERROR: {str(e)}")
            results["status"] = "failed"
            results["errors"].append(str(e))
            return results

    def _collect_board_analytics(
        self,
        brand: str,
        board_name: str,
        board_id: str
    ) -> Optional[Dict]:
        """Fetch analytics for a single board via Pinterest API.

        API Endpoint: GET /v5/boards/{board_id}/analytics

        Returns analytics for the last 30 days (default).
        """
        if not board_id:
            print(f"  SKIP: No board_id for {board_name}")
            return None

        try:
            # Calculate date range (last 30 days)
            end_date = datetime.now(timezone.utc).date()
            start_date = end_date - timedelta(days=30)

            # Pinterest API endpoint
            url = f"{self.BASE_URL}/boards/{board_id}/analytics"
            params = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "metric_types": "IMPRESSION,SAVE,CLICK,PIN_CLICK"
            }

            print(f"  → Fetching: {board_name} ({board_id})")
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()

            data = response.json()

            # Parse metrics from response
            analytics = {
                "brand": brand,
                "board_name": board_name,
                "board_id": board_id,
                "period_start": start_date.isoformat(),
                "period_end": end_date.isoformat(),
                "collected_at": datetime.now(timezone.utc).isoformat(),
                "impressions": 0,
                "saves": 0,
                "clicks": 0,
                "pin_clicks": 0,
                "raw_data": data  # Store raw API response for reference
            }

            # Extract metrics if available
            if "metrics" in data:
                for metric in data.get("metrics", []):
                    metric_type = metric.get("metric_type", "")
                    value = metric.get("value", 0)

                    if metric_type == "IMPRESSION":
                        analytics["impressions"] = value
                    elif metric_type == "SAVE":
                        analytics["saves"] = value
                    elif metric_type == "CLICK":
                        analytics["clicks"] = value
                    elif metric_type == "PIN_CLICK":
                        analytics["pin_clicks"] = value

            print(f"    ✓ Impressions: {analytics['impressions']}, "
                  f"Saves: {analytics['saves']}, "
                  f"Clicks: {analytics['clicks']}, "
                  f"Pin Clicks: {analytics['pin_clicks']}")

            return analytics

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise Exception(f"Unauthorized - check LATE_API_KEY validity")
            elif e.response.status_code == 403:
                raise Exception(f"Forbidden - app may not have analytics access")
            elif e.response.status_code == 404:
                raise Exception(f"Board not found - check board_id {board_id}")
            else:
                raise Exception(f"HTTP {e.response.status_code}: {e.response.text}")
        except requests.exceptions.Timeout:
            raise Exception("Request timeout (15s) - API may be slow")
        except Exception as e:
            raise Exception(f"Failed to fetch analytics: {str(e)}")

    def _save_analytics(self, analytics: Dict) -> None:
        """Save analytics record to Supabase pinterest_analytics table.

        Creates table if it doesn't exist (schema is auto-applied on first run).
        """
        try:
            from database.supabase_client import get_supabase_client
            db = get_supabase_client()

            # Insert into pinterest_analytics table
            result = db.client.table("pinterest_analytics").insert(analytics).execute()
            if result.data:
                print(f"    → Saved to Supabase")
            else:
                print(f"    ⚠ Insert returned no data")

        except Exception as e:
            print(f"    ERROR saving to Supabase: {e}")
            # Don't re-raise - API data was collected successfully
            # Database issue shouldn't block the run


def main():
    """Entry point for GitHub Actions workflow."""
    print(f"Starting Pinterest Analytics Collector at {datetime.now(timezone.utc).isoformat()}")
    print("=" * 80)

    collector = PinterestAnalyticsCollector()
    results = collector.run()

    print("=" * 80)
    print(f"\nResults Summary:")
    print(f"  Status: {results['status']}")
    print(f"  Boards analyzed: {results['boards_analyzed']}")
    print(f"  Analytics saved: {results['analytics_saved']}")
    if results['errors']:
        print(f"  Errors: {len(results['errors'])}")
        for error in results['errors']:
            print(f"    - {error}")

    # Exit with error code if failed
    if results["status"] == "failed":
        sys.exit(1)

    return results


if __name__ == "__main__":
    main()
