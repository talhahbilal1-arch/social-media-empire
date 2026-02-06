#!/usr/bin/env python3
"""
Diagnostic script to test all API connections.
Run this to identify which services need attention.

Usage:
    python scripts/diagnose_apis.py

Or with specific tests:
    python scripts/diagnose_apis.py --test late_api
    python scripts/diagnose_apis.py --test youtube
"""

import os
import sys
import argparse
import requests
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def print_header(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_result(name: str, success: bool, message: str = ""):
    icon = "✅" if success else "❌"
    print(f"  {icon} {name}: {message}")


def test_gemini():
    """Test Gemini API connection."""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return False, "GEMINI_API_KEY not set"

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content("Say 'API test successful' in 3 words or less")
        return True, f"Working - got response: {response.text[:50]}..."
    except Exception as e:
        return False, f"Error: {str(e)[:100]}"


def test_pexels():
    """Test Pexels API connection."""
    api_key = os.environ.get('PEXELS_API_KEY')
    if not api_key:
        return False, "PEXELS_API_KEY not set"

    try:
        response = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": api_key},
            params={"query": "test", "per_page": 1},
            timeout=10
        )
        if response.status_code == 200:
            return True, f"Working - found {response.json().get('total_results', 0)} results"
        return False, f"HTTP {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return False, f"Error: {str(e)[:100]}"


def test_creatomate():
    """Test Creatomate API connection."""
    api_key = os.environ.get('CREATOMATE_API_KEY')
    if not api_key:
        return False, "CREATOMATE_API_KEY not set"

    try:
        response = requests.get(
            "https://api.creatomate.com/v1/templates",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        if response.status_code == 200:
            templates = response.json()
            return True, f"Working - found {len(templates)} templates"
        elif response.status_code == 402:
            return False, "402 Payment Required - check Creatomate billing/subscription"
        elif response.status_code == 401:
            return False, "401 Unauthorized - API key invalid"
        return False, f"HTTP {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return False, f"Error: {str(e)[:100]}"


def test_late_api(key_env: str = "LATE_API_KEY"):
    """Test Late API connection for Pinterest."""
    api_key = os.environ.get(key_env)
    if not api_key:
        return False, f"{key_env} not set"

    try:
        response = requests.get(
            "https://getlate.dev/api/v1/accounts",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        if response.status_code == 200:
            accounts = response.json()
            accounts_list = accounts if isinstance(accounts, list) else accounts.get('data', [])
            pinterest_accounts = [a for a in accounts_list if a.get('platform') == 'pinterest']
            if pinterest_accounts:
                usernames = [a.get('username', 'unknown') for a in pinterest_accounts]
                return True, f"Working - Pinterest accounts: {', '.join(usernames)}"
            return False, "No Pinterest accounts connected to Late API"
        elif response.status_code == 403:
            return False, "403 Forbidden - API key expired or invalid. Regenerate at getlate.dev"
        elif response.status_code == 401:
            return False, "401 Unauthorized - API key invalid"
        return False, f"HTTP {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return False, f"Error: {str(e)[:100]}"


def test_youtube():
    """Test YouTube OAuth connection."""
    client_id = os.environ.get('YOUTUBE_CLIENT_ID')
    client_secret = os.environ.get('YOUTUBE_CLIENT_SECRET')
    refresh_token = os.environ.get('YOUTUBE_REFRESH_TOKEN')

    if not all([client_id, client_secret, refresh_token]):
        missing = []
        if not client_id: missing.append("YOUTUBE_CLIENT_ID")
        if not client_secret: missing.append("YOUTUBE_CLIENT_SECRET")
        if not refresh_token: missing.append("YOUTUBE_REFRESH_TOKEN")
        return False, f"Missing: {', '.join(missing)}"

    try:
        # Try to refresh the access token
        response = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token"
            },
            timeout=10
        )

        if response.status_code == 200:
            access_token = response.json().get("access_token")

            # Test API access with the token
            channel_response = requests.get(
                "https://www.googleapis.com/youtube/v3/channels",
                headers={"Authorization": f"Bearer {access_token}"},
                params={"part": "snippet", "mine": "true"},
                timeout=10
            )

            if channel_response.status_code == 200:
                channels = channel_response.json().get("items", [])
                if channels:
                    channel_name = channels[0].get("snippet", {}).get("title", "Unknown")
                    return True, f"Working - Channel: {channel_name}"
                return True, "Token valid but no channels found"
            elif channel_response.status_code == 403:
                error_msg = channel_response.json().get("error", {}).get("message", "")
                if "quotaExceeded" in error_msg:
                    return False, "403 Quota exceeded - wait 24 hours or increase quota"
                elif "accessNotConfigured" in error_msg or "disabled" in error_msg:
                    return False, "YouTube API not enabled in Google Cloud Console"
                elif "access" in error_msg.lower():
                    return False, "403 - OAuth app may be in Testing mode. Publish to Production in Google Cloud Console"
                return False, f"403 Forbidden: {error_msg[:100]}"
            return False, f"Channel check failed: HTTP {channel_response.status_code}"

        elif response.status_code == 400:
            error = response.json().get("error", "unknown")
            error_desc = response.json().get("error_description", "")
            if error == "invalid_grant":
                return False, "Refresh token expired or revoked. Re-authorize OAuth"
            return False, f"400 Bad Request: {error} - {error_desc}"

        return False, f"Token refresh failed: HTTP {response.status_code}"
    except Exception as e:
        return False, f"Error: {str(e)[:100]}"


def test_supabase():
    """Test Supabase connection."""
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')

    if not url or not key:
        missing = []
        if not url: missing.append("SUPABASE_URL")
        if not key: missing.append("SUPABASE_KEY")
        return False, f"Missing: {', '.join(missing)}"

    try:
        response = requests.get(
            f"{url}/rest/v1/",
            headers={
                "apikey": key,
                "Authorization": f"Bearer {key}"
            },
            timeout=10
        )
        if response.status_code in [200, 404]:  # 404 is ok, means connected but no default table
            return True, "Working - connected to Supabase"
        return False, f"HTTP {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return False, f"Error: {str(e)[:100]}"


def test_resend():
    """Test Resend API connection (without sending email)."""
    api_key = os.environ.get('RESEND_API_KEY')
    if not api_key:
        return False, "RESEND_API_KEY not set"

    try:
        response = requests.get(
            "https://api.resend.com/domains",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        if response.status_code == 200:
            domains = response.json().get("data", [])
            return True, f"Working - {len(domains)} domains configured"
        elif response.status_code == 401:
            return False, "401 Unauthorized - API key invalid. Regenerate at resend.com"
        return False, f"HTTP {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return False, f"Error: {str(e)[:100]}"


def test_convertkit():
    """Test ConvertKit API connection."""
    api_key = os.environ.get('CONVERTKIT_API_KEY')
    if not api_key:
        return False, "CONVERTKIT_API_KEY not set"

    try:
        response = requests.get(
            "https://api.convertkit.com/v3/account",
            params={"api_key": api_key},
            timeout=10
        )
        if response.status_code == 200:
            account = response.json()
            name = account.get("name", "Unknown")
            return True, f"Working - Account: {name}"
        return False, f"HTTP {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return False, f"Error: {str(e)[:100]}"


def run_all_tests():
    """Run all diagnostic tests."""
    print(f"\n🔍 Social Media Empire - API Diagnostics")
    print(f"   Run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = {}

    # Content Generation APIs
    print_header("Content Generation APIs")

    success, msg = test_gemini()
    print_result("Gemini (AI Content)", success, msg)
    results["gemini"] = success

    success, msg = test_pexels()
    print_result("Pexels (Stock Media)", success, msg)
    results["pexels"] = success

    success, msg = test_creatomate()
    print_result("Creatomate (Video Rendering)", success, msg)
    results["creatomate"] = success

    # Social Platform APIs
    print_header("Social Platform APIs")

    success, msg = test_youtube()
    print_result("YouTube (OAuth)", success, msg)
    results["youtube"] = success

    # Test all Late API keys
    for i, key_name in enumerate(["LATE_API_KEY", "LATE_API_KEY_2", "LATE_API_KEY_3", "LATE_API_KEY_4"]):
        success, msg = test_late_api(key_name)
        account_label = ["Default", "DailyDealDarlin", "FitOver35", "MenopausePlanner"][i]
        print_result(f"Late API ({account_label})", success, msg)
        results[f"late_api_{i+1}"] = success

    # Infrastructure APIs
    print_header("Infrastructure APIs")

    success, msg = test_supabase()
    print_result("Supabase (Database)", success, msg)
    results["supabase"] = success

    success, msg = test_resend()
    print_result("Resend (Email Alerts)", success, msg)
    results["resend"] = success

    success, msg = test_convertkit()
    print_result("ConvertKit (Email Marketing)", success, msg)
    results["convertkit"] = success

    # Summary
    print_header("SUMMARY")

    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed

    print(f"\n  Passed: {passed}/{total}")
    print(f"  Failed: {failed}/{total}")

    if failed > 0:
        print("\n  ⚠️  ACTION REQUIRED:")

        if not results.get("creatomate"):
            print("     - Creatomate: Check billing at creatomate.com/dashboard")

        if not results.get("youtube"):
            print("     - YouTube: Publish OAuth app to Production in Google Cloud Console")
            print("       1. Go to console.cloud.google.com")
            print("       2. APIs & Services → OAuth consent screen")
            print("       3. Click 'PUBLISH APP'")

        late_failures = [k for k in results if k.startswith("late_api_") and not results[k]]
        if late_failures:
            print("     - Late API: Regenerate API keys at getlate.dev/dashboard")
            print("       Then update GitHub secrets: LATE_API_KEY, LATE_API_KEY_2, etc.")

        if not results.get("resend"):
            print("     - Resend: Regenerate API key at resend.com/api-keys")
            print("       Then: gh secret set RESEND_API_KEY -b 'your_new_key'")

    print()
    return 0 if failed == 0 else 1


def main():
    parser = argparse.ArgumentParser(description="Diagnose API connections")
    parser.add_argument("--test", help="Run specific test (gemini, pexels, creatomate, youtube, late_api, supabase, resend, convertkit)")
    args = parser.parse_args()

    if args.test:
        tests = {
            "gemini": test_gemini,
            "pexels": test_pexels,
            "creatomate": test_creatomate,
            "youtube": test_youtube,
            "late_api": lambda: test_late_api("LATE_API_KEY"),
            "supabase": test_supabase,
            "resend": test_resend,
            "convertkit": test_convertkit
        }

        if args.test not in tests:
            print(f"Unknown test: {args.test}")
            print(f"Available: {', '.join(tests.keys())}")
            return 1

        success, msg = tests[args.test]()
        print_result(args.test, success, msg)
        return 0 if success else 1

    return run_all_tests()


if __name__ == "__main__":
    sys.exit(main())
