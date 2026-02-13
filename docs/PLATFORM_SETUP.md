# Platform Setup Guide

This guide explains how to fix common API issues and set up platform integrations.

## Quick Diagnostics

Run the diagnostic script to check all API connections:

```bash
python scripts/diagnose_apis.py
```

---

## 1. YouTube OAuth (400 Bad Request)

### Problem
YouTube uploads fail with "400 Bad Request" because the OAuth app is in "Testing" mode.

### Fix
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Select your project
3. Navigate to **APIs & Services** → **OAuth consent screen**
4. Click **PUBLISH APP** button
5. Confirm in the dialog

After publishing, YouTube uploads will work for any user, not just test users.

---

## 2. Creatomate (402 Payment Required)

### Problem
Video rendering fails because Creatomate account needs payment/subscription.

### Current Workaround
The system automatically falls back to using Pexels stock videos when Creatomate fails.

### Fix
1. Go to [Creatomate Dashboard](https://creatomate.com/dashboard)
2. Check your subscription status
3. Add payment method or upgrade plan if needed

---

## 3. Late API / Pinterest (403 Forbidden)

### Problem
Pinterest posting fails because Late API keys are expired or invalid.

### Fix
1. Go to [Late API Dashboard](https://getlate.dev/dashboard)
2. Navigate to **API Keys** section
3. Generate new API keys
4. Update GitHub secrets:

```bash
gh secret set LATE_API_KEY -b "your_new_key_1"
gh secret set LATE_API_KEY_2 -b "your_new_key_2"
gh secret set LATE_API_KEY_3 -b "your_new_key_3"
gh secret set LATE_API_KEY_4 -b "your_new_key_4"
```

### Verify Pinterest Accounts
After regenerating keys, verify Pinterest accounts are still connected:
1. Go to Late API dashboard
2. Check **Accounts** section
3. Reconnect any Pinterest accounts if needed

---

## 4. Resend (401 Unauthorized)

### Problem
Email alerts fail because Resend API key is invalid.

### Fix
1. Go to [Resend API Keys](https://resend.com/api-keys)
2. Generate a new API key
3. Update GitHub secret:

```bash
gh secret set RESEND_API_KEY -b "your_new_key"
```

---

## 5. TikTok & Instagram

### Current Status
These platforms require Make.com webhooks which aren't configured yet.

### Setup (Optional)
1. Create a Make.com account
2. Create scenarios for TikTok and Instagram posting
3. Get webhook URLs
4. Add secrets:

```bash
gh secret set MAKE_COM_TIKTOK_WEBHOOK -b "your_webhook_url"
gh secret set MAKE_COM_INSTAGRAM_WEBHOOK -b "your_webhook_url"
```

---

## Verification

After fixing any issues, verify with:

```bash
# Run full diagnostics
python scripts/diagnose_apis.py

# Test specific service
python scripts/diagnose_apis.py --test youtube
python scripts/diagnose_apis.py --test late_api
python scripts/diagnose_apis.py --test resend

# Trigger a test workflow
gh workflow run video-automation-afternoon.yml --field dry_run=true
```

---

## Current System Status

The video automation system is designed to be resilient:

| Component | Failure Behavior |
|-----------|------------------|
| Creatomate | Falls back to Pexels stock video |
| YouTube | Logs error, continues with other platforms |
| Pinterest | Logs error, continues with other platforms |
| Resend | Logs warning, workflow continues |

Workflows now **succeed** when content is generated, even if some platform postings fail.
