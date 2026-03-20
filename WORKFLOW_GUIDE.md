# PilotTools GitHub Actions Workflows Guide

## Overview
This document outlines all PilotTools marketing automation workflows configured in `.github/workflows/`. These workflows handle content generation, social media posting, email outreach, and site deployment.

## Workflows Summary

### 1. **toolpilot-content.yml** - Daily Content Generation
**Schedule:** Mon-Fri at 6AM UTC (10PM PST previous day)
**Manual trigger:** workflow_dispatch with inputs
**Timeout:** 15 minutes

**What it does:**
- Generates 3 items per run (tools, comparisons, reviews) from the content calendar
- Builds the Next.js site
- Deploys to Vercel (pilottools.ai)
- Repurposes content for social media (content-repurposer)
- Generates lead magnets every Monday
- Commits content and social queue to git
- Pings Google Search Console for re-crawl

**Inputs (workflow_dispatch):**
- `content_type`: 'auto' (default), 'review', or 'comparison'
- `specific_topic`: Optional content calendar slug
- `count`: Default 3 (was 1, now 3 for more output)

---

### 2. **toolpilot-twitter.yml** - Twitter Automation
**Schedule:** Daily at 3x intervals
- 5PM UTC (9AM PST)
- 9PM UTC (1PM PST)
- 2AM UTC (6PM PST)

**Manual trigger:** workflow_dispatch with inputs
**Timeout:** 15 minutes

**What it does:**
- Generates and posts tweets (tips, comparisons, threads, or auto-selected)
- Updates twitter-history.json tracking file
- Commits to git

**Inputs (workflow_dispatch):**
- `type`: 'auto' (default), 'tip', 'comparison', or 'thread'
- `count`: Default 1 (1-3 tweets)

---

### 3. **toolpilot-linkedin.yml** - LinkedIn Automation
**Schedule:** Mon/Wed/Fri at 6PM UTC (10AM PST)
**Manual trigger:** workflow_dispatch
**Timeout:** 15 minutes

**What it does:**
- Posts 1 LinkedIn article/update per run
- Requires: LINKEDIN_ACCESS_TOKEN, LINKEDIN_PERSON_ID secrets
- Updates linkedin-history.json tracking file
- Commits to git

---

### 4. **toolpilot-pinterest.yml** - Pinterest Automation
**Schedule:** Daily at 2 intervals
- 4PM UTC (8AM PST)
- 10PM UTC (2PM PST)

**Manual trigger:** workflow_dispatch with count input
**Timeout:** 15 minutes

**What it does:**
- Generates and posts 3 Pinterest pins per run (default)
- Sends pins to Make.com webhook for scheduling
- Updates pinterest-history.json tracking file
- Commits to git

**Inputs (workflow_dispatch):**
- `count`: Default 3 (1-5 pins)

---

### 5. **toolpilot-repurpose.yml** - Content Repurposer
**Schedule:** Daily at 8AM UTC (12AM PST)
**Manual trigger:** workflow_dispatch
**Timeout:** 15 minutes

**What it does:**
- Runs content repurposer on 3 recent content pieces
- Converts articles/tools into social media posts
- Posts 1 tweet from the social queue
- Updates social-queue.json and twitter-history.json
- Commits to git

**Key feature:** Bridges content engine and social posting - content created by `toolpilot-content.yml` → repurposed → queued for Twitter → posted by this workflow

---

### 6. **toolpilot-outreach.yml** - Backlink Outreach
**Schedule:** Weekly on Monday at 3PM UTC (7AM PST)
**Manual trigger:** workflow_dispatch with inputs
**Timeout:** 20 minutes (longer due to email sending)

**What it does:**
- Generates and sends outreach emails for backlinks/partnerships
- Requires: RESEND_API_KEY secret
- Tracks all outreach attempts in outreach-log.json
- Commits to git

**Inputs (workflow_dispatch):**
- `type`: 'testimonial' (default), 'partnership', or 'feature'
- `count`: Default 5 (1-10 emails)

---

### 7. **toolpilot-weekly.yml** - Weekly Discovery
**Schedule:** Monday 7AM UTC (Sunday 11PM PST)
**Manual trigger:** workflow_dispatch with inputs
**Timeout:** 15 minutes

**What it does:**
- Discovers trending AI topics via Gemini
- Generates 3 content pieces from discoveries
- Builds and deploys to Vercel
- Generates weekly lead magnet
- Commits all new content and config

**Inputs (workflow_dispatch):**
- `skip_discovery`: true/false (skip trend discovery, generate pending only)
- `content_count`: Default 3

---

## Configuration & Secrets

### Required GitHub Secrets
```
GEMINI_API_KEY              # For all content generation
TWITTER_API_KEY             # For Twitter posting
TWITTER_API_SECRET
TWITTER_ACCESS_TOKEN
TWITTER_ACCESS_SECRET
LINKEDIN_ACCESS_TOKEN       # For LinkedIn posting
LINKEDIN_PERSON_ID
RESEND_API_KEY              # For email outreach
MAKE_WEBHOOK_PILOTTOOLS     # For Pinterest posting
VERCEL_BRAND_TOKEN          # Personal access token (NOT project-scoped)
VERCEL_ORG_ID               # Organization ID
VERCEL_PROJECT_ID           # PilotTools project ID
GITHUB_TOKEN                # Auto-provided by GitHub
```

### Config Files (tracked in git)
- `ai-tools-hub/config/content-calendar.json` - Weekly content plan
- `ai-tools-hub/config/twitter-history.json` - Twitter posts archive
- `ai-tools-hub/config/linkedin-history.json` - LinkedIn posts archive
- `ai-tools-hub/config/pinterest-history.json` - Pinterest pins archive
- `ai-tools-hub/config/social-queue.json` - Posts pending for Twitter
- `ai-tools-hub/config/outreach-log.json` - Backlink outreach history

---

## Workflow Execution Order & Dependencies

```
Morning (6AM UTC / 10PM PST):
  └─ toolpilot-content.yml (daily content generation)
     ├─ Generates 3 items
     ├─ Deploys to Vercel
     ├─ Repurposes content
     └─ Monday: Generates lead magnet

Daily (8AM UTC):
  └─ toolpilot-repurpose.yml (content to social queue)
     └─ Posts 1 tweet from queue

9AM PST, 1PM PST, 6PM PST:
  └─ toolpilot-twitter.yml (automated Twitter posting)

10AM PST (Mon/Wed/Fri):
  └─ toolpilot-linkedin.yml (LinkedIn posting)

8AM PST & 2PM PST:
  └─ toolpilot-pinterest.yml (Pinterest posting)

7AM PST (Mondays):
  └─ toolpilot-weekly.yml (trend discovery + lead magnet)

7AM PST (Mondays):
  └─ toolpilot-outreach.yml (backlink outreach campaign)
```

---

## Common Tasks

### Generate content manually
```bash
# Via workflow dispatch on toolpilot-content.yml
# Or run locally:
cd ai-tools-hub
node scripts/generate-content.js --count 3
```

### Post to social networks manually
```bash
# Twitter
node scripts/twitter-poster.js --type auto --count 1

# LinkedIn
node scripts/linkedin-poster.js --count 1

# Pinterest
node scripts/pinterest-poster.js --count 3
```

### Check workflow status
```bash
# View recent runs
gh workflow list

# View specific workflow runs
gh run list --workflow=toolpilot-content.yml
```

---

## Troubleshooting

### Workflow fails with API errors
- Check that secrets are set correctly: `gh secret list`
- Verify API keys are still valid (especially LINKEDIN_ACCESS_TOKEN, which expires ~2026-04-24)
- Check workflow logs: `gh run view <run-id> --log`

### Pinterest pins not posting
- Verify Make.com webhook is active and reachable
- Check that `MAKE_WEBHOOK_PILOTTOOLS` secret is set
- Make.com should NOT receive preflight checks (HEAD/GET) - only POST with data

### Content not deploying to Vercel
- Verify `VERCEL_BRAND_TOKEN` is a personal access token, not project-scoped
- Check that project exists in Vercel org
- Verify `VERCEL_PROJECT_ID` matches the deployment project

### Git push fails in workflow
- Ensure `GITHUB_TOKEN` has `contents: write` permission (already set in all workflows)
- Run `git pull --rebase --autostash` before push

---

## Environment Variables & Timing

All workflows use these timezone conversions:
- **UTC** is the source (POSIX cron format uses UTC)
- **PST** (Pacific Standard Time) is -8 hours from UTC

**Examples:**
- 6AM UTC = 10PM PST previous day
- 8AM UTC = 12AM PST midnight
- 5PM UTC = 9AM PST

---

## Updates Made

### Changes to existing workflows:

**toolpilot-content.yml:**
- Default count increased from 1 → 3
- Added "Repurpose content" step (runs content-repurposer.js)
- Added "Generate lead magnet" step (Mondays only)
- Updated git add to include `downloads/` and `social-queue.json`

**toolpilot-weekly.yml:**
- Added "Generate lead magnet" step before final commit
- Updated git add to include `downloads/` directory

### New workflows created:
- **toolpilot-twitter.yml** - 3x daily Twitter posting
- **toolpilot-linkedin.yml** - 3x weekly LinkedIn posting
- **toolpilot-pinterest.yml** - 2x daily Pinterest posting
- **toolpilot-repurpose.yml** - Daily content repurposing + Twitter queue
- **toolpilot-outreach.yml** - Weekly backlink outreach campaigns

---

## Security Notes

All workflows follow GitHub Actions security best practices:
- User input from `workflow_dispatch` passed through environment variables (no direct shell injection)
- Secrets never logged or echoed
- Git commits use standard bot identity
- `continue-on-error: true` used for non-critical steps (social posting, optional features)

---

## Next Steps

1. **Set up GitHub Secrets** - Add all required API keys and tokens
2. **Test manually** - Run each workflow manually via workflow_dispatch before relying on schedules
3. **Monitor first week** - Watch logs to catch any issues with API integrations
4. **Verify Vercel deployments** - Ensure sites deploy correctly after content generation
5. **Check Make.com webhooks** - Verify Pinterest pins queue correctly
6. **Monitor social posting** - Check that tweets/posts appear on each network

