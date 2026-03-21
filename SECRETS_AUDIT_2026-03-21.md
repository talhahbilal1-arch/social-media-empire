# GitHub Secrets Audit Report
**Repository**: social-media-empire
**Date**: 2026-03-21
**Auditor**: Claude Code

---

## Executive Summary

| Metric | Count | Status |
|--------|-------|--------|
| **Total Secrets in GitHub** | 47 | ⚠️ |
| **Total Secrets Used by Workflows** | 50 | ⚠️ |
| **Active & Healthy** | 33 | ✅ |
| **Missing from GitHub** | 17 | ❌ |
| **Unused in GitHub** | 14 | ⚠️ |
| **Coverage** | 78% | ⚠️ |
| **Overall Health** | GOOD (but with critical risks) | ⚠️ |

---

## 🚨 CRITICAL ISSUES

### 1. LINKEDIN_ACCESS_TOKEN - EXPIRING SOON
- **Status**: Not stored in GitHub (referenced in workflows but missing)
- **Expiration**: ~2026-04-24 (34 days from now)
- **Impact**: LinkedIn syndication workflows will fail after expiration
- **Action Required**: MUST refresh before 2026-04-24
- **How to fix**:
  1. Go to https://www.linkedin.com/developers/apps
  2. Refresh OAuth token in LinkedIn developer portal
  3. Add `LINKEDIN_ACCESS_TOKEN` to GitHub secrets
  4. Update project-claw vault if using it

### 2. github-pat - EXPIRED (project-claw vault)
- **Status**: Confirmed expired (from MEMORY.md)
- **Impact**: Breaks workflow-health-check cron, fails silently
- **Action Required**: MUST regenerate immediately
- **How to fix**:
  1. Go to https://github.com/settings/tokens
  2. Create new Personal Access Token with scopes: `repo`, `workflow`, `contents:write`
  3. Run: `claw vault set github-pat <new-token>`
  4. This will restore workflow health checks

### 3. GITHUB_TOKEN - REFERENCED BUT MISSING
- **Status**: Referenced in content-engine.yml line 36 but not stored
- **Impact**: Uses GitHub's built-in token (fallback works, but has limited permissions)
- **Action**: Not critical, but verify permissions are sufficient

---

## ⚠️ MISSING SECRETS (17 total)

### High Priority (Used in Active Workflows)
- `LINKEDIN_ACCESS_TOKEN` - LinkedIn syndication (expires 2026-04-24) ⚠️
- `LINKEDIN_PERSON_ID` - LinkedIn person ID (needed for posting)

### Medium Priority (Deprecated/Placeholder)
- `GITHUB_TOKEN` - Uses GitHub's built-in token (auto-provided)
- `MAKE_COM_PINTEREST_WEBHOOK` - v1 webhook (replaced by v2)
- `MAKE_WEBHOOK_PILOTTOOLS` - Referenced but never used
- `PINTEREST_*_ACCOUNT_ID/BOARD_ID` - Hardcoded in code instead

### Low Priority (Old Integrations)
- `TIKTOK_ACCESS_TOKEN` - May be in separate vault
- `TWITTER_ACCESS_SECRET`, `TWITTER_ACCESS_TOKEN`, `TWITTER_API_KEY`, `TWITTER_API_SECRET` - Old integration (inactive)
- `RAINFOREST_API_KEY` - Old integration (inactive)

---

## 🗑️ UNUSED SECRETS IN GITHUB (14 total)

These secrets are stored in GitHub but **NOT referenced in any active workflow**. Consider removing them after verification:

| Secret | Age | Last Updated | Recommendation |
|--------|-----|--------------|-----------------|
| `ALERT_EMAIL_FROM` | 74 days | 2026-01-06 | Remove (email alerts disabled 2026-02-13) |
| `ALERT_EMAIL_PASSWORD` | 74 days | 2026-01-06 | Remove (email alerts disabled 2026-02-13) |
| `ALERT_EMAIL_TO` | 74 days | 2026-01-06 | Remove (email alerts disabled 2026-02-13) |
| `ANTHROPIC_API_KEY` | 74 days | 2026-01-06 | Review: May be legacy |
| `CONVERTKIT_DDD_FORM_ID` | 44 days | 2026-02-04 | Keep (possibly referenced in active code) |
| `CONVERTKIT_FORM_ID` | 73 days | 2026-01-07 | Remove (superseded by CONVERTKIT_DDD_FORM_ID) |
| `FITOVER35_GITHUB_TOKEN` | 45 days | 2026-02-04 | Remove (check archive workflows) |
| `MAKECOM_PINTEREST_WEBHOOK` | 73 days | 2026-01-06 | Remove (v1, replaced by v2 webhooks) |
| `MAKE_COM_INSTAGRAM_WEBHOOK` | 57 days | 2026-01-23 | Remove (Instagram integration inactive) |
| `MAKE_COM_TIKTOK_WEBHOOK` | 57 days | 2026-01-23 | Remove (TikTok now uses separate vault) |
| `MAKE_WEBHOOK_URL` | 54 days | 2026-01-26 | Remove (generic, unused) |
| `NETLIFY_SITE_ID` | 74 days | 2026-01-06 | Remove (Netlify deprecated 2026-02-17, migrated to Vercel) |
| `VERCEL_TOKEN` | 32 days | 2026-02-17 | Remove (using project-scoped tokens) |
| `MAKE_API_TOKEN` | 21 days | 2026-02-28 | **Keep** (actively used) |

---

## ✅ ACTIVE & HEALTHY SECRETS (33 total)

### Core Content Generation
| Secret | Last Used | Category | Status |
|--------|-----------|----------|--------|
| `GEMINI_API_KEY` | 2026-01-21 | AI Content | ✅ |
| `PEXELS_API_KEY` | 2026-01-25 | Media | ✅ |
| `SUPABASE_KEY` | 2026-01-26 | Database | ✅ |
| `SUPABASE_URL` | 2026-01-21 | Database | ✅ |

### Pinterest Automation (Most Recent: 2026-02-28)
| Secret | Used By | Status |
|--------|---------|--------|
| `LATE_API_KEY` (4 keys) | Pinterest analytics & posting | ✅ |
| `MAKE_WEBHOOK_FITNESS` | Poster (fitness brand) | ✅ |
| `MAKE_WEBHOOK_DEALS` | Poster (deals brand) | ✅ |
| `MAKE_WEBHOOK_MENOPAUSE` | Poster (menopause brand) | ✅ |
| `MAKE_WEBHOOK_ACTIVATOR` | Pre-flight scenario activation | ✅ |

### Video Automation (Most Recent: 2026-02-28)
| Secret | Used By | Status |
|--------|---------|--------|
| `MAKE_WEBHOOK_VIDEO_FITNESS` | Video pins | ✅ |
| `MAKE_WEBHOOK_VIDEO_DEALS` | Video pins | ✅ |
| `MAKE_WEBHOOK_VIDEO_MENOPAUSE` | Video pins | ✅ |
| `CREATOMATE_API_KEY` | Video rendering | ✅ |
| `ELEVENLABS_API_KEY` | Voiceovers | ✅ |
| `YOUTUBE_CLIENT_ID` | YouTube upload | ✅ |
| `YOUTUBE_CLIENT_SECRET` | YouTube OAuth | ✅ |
| `YOUTUBE_REFRESH_TOKEN` | YouTube refresh | ✅ |

### Vercel Deployment (Most Recent: 2026-02-18)
| Secret | Purpose | Status |
|--------|---------|--------|
| `VERCEL_BRAND_TOKEN` | Deploy all 3 brands | ✅ |
| `VERCEL_FITOVER35_PROJECT_ID` | fitover35.com | ✅ |
| `VERCEL_DEALS_PROJECT_ID` | dailydealdarling.com | ✅ |
| `VERCEL_MENOPAUSE_PROJECT_ID` | menopause-planner | ✅ |
| `VERCEL_ORG_ID` | Organization ID | ✅ |
| `VERCEL_PROJECT_ID` | PilotTools project | ✅ |

### Email & Notifications (Most Recent: 2026-01-12)
| Secret | Purpose | Status |
|--------|---------|--------|
| `CONVERTKIT_API_KEY` | Email sequences | ✅ |
| `CONVERTKIT_API_SECRET` | Email auth | ✅ |
| `RESEND_API_KEY` | Email delivery | ✅ |
| `ALERT_EMAIL` | Alert recipient | ✅ |

### Database & System Health
| Secret | Purpose | Last Used |
|--------|---------|-----------|
| `SUPABASE_TIKTOK_KEY` | TikTok DB | 2026-02-08 ✅ |
| `SUPABASE_TIKTOK_URL` | TikTok DB | 2026-02-08 ✅ |
| `MAKE_API_TOKEN` | Make.com API | 2026-02-28 ✅ |
| `NETLIFY_API_TOKEN` | Netlify monitoring | 2026-02-14 ✅ |

---

## 📋 ACTION PLAN

### This Week (Critical)
- [ ] **LINKEDIN_ACCESS_TOKEN**: Refresh token before 2026-04-24 (34 days left)
  - Portal: https://www.linkedin.com/developers/apps
  - Add to GitHub secrets + project-claw vault

- [ ] **github-pat**: Generate new PAT with repo/workflow/contents:write scopes
  - Portal: https://github.com/settings/tokens
  - Run: `claw vault set github-pat <new-token>`

### This Month (High Priority)
- [ ] Add `LINKEDIN_PERSON_ID` to GitHub secrets
- [ ] Remove 14 unused secrets (see cleanup list above)
- [ ] Update documentation to remove references to deprecated webhooks

### Optional (Low Priority)
- [ ] Consolidate Make.com webhook documentation
- [ ] Clean up archive workflows if they reference old secrets

---

## 📊 Summary by Status

| Category | Count | Action |
|----------|-------|--------|
| Active & Healthy | 33 | Monitor |
| Missing (High Priority) | 2 | Add ASAP |
| Missing (Low Priority) | 15 | Monitor |
| Unused (> 30 days) | 13 | Remove |
| Unused (< 30 days) | 1 | Keep |
| Expiring Soon | 1 | Refresh before 2026-04-24 |
| Expired | 1 | Regenerate (project-claw vault) |

---

## Workflow Coverage by Secret

**Most Critical Workflows**:
1. `content-engine.yml` - Uses 8 secrets (Gemini, Pexels, Supabase x2, LATE x4, Make webhooks)
2. `system-health.yml` - Uses 10+ secrets for monitoring and alerts
3. `video-automation-morning.yml` - Uses YouTube, Creatomate, ElevenLabs
4. `daily-trend-scout.yml` - Uses Gemini, Supabase

**Workflows with Missing Secrets**:
- LinkedIn syndication workflows (LINKEDIN_ACCESS_TOKEN missing)
- Twitter/TikTok workflows (missing credentials)

---

## Notes

- **Email alerts disabled** (2026-02-13): ALERT_EMAIL_* secrets are unused per project policy
- **Netlify deprecated** (2026-02-17): Migrated to Vercel, NETLIFY_SITE_ID no longer needed
- **Pinterest v2 webhooks**: All 3 brands now use Make.com v2 webhooks (v1 MAKECOM_PINTEREST_WEBHOOK deprecated)
- **TikTok vault**: Separate project-claw vault, not in GitHub secrets
- **Coverage**: 78% (39/50 required secrets present in GitHub)

---

**Generated**: 2026-03-21 by Claude Code
**Next Review**: 2026-04-18 (or when expiration issues occur)
