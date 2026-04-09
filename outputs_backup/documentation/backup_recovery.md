# Backup and Recovery Documentation -- Pinterest Empire

Complete procedures for backing up all system components, restoring from backups, and recovering from various disaster scenarios.

---

## Table of Contents

1. [Backup Overview](#backup-overview)
2. [Automatic Backups](#automatic-backups)
3. [Manual Backup Procedures](#manual-backup-procedures)
4. [Recovery Procedures](#recovery-procedures)
5. [Disaster Recovery Plan](#disaster-recovery-plan)
6. [Backup Schedule Summary](#backup-schedule-summary)

---

## Backup Overview

### What Needs to Be Backed Up

| Component | Data | Backup Method | Frequency | Retention |
|-----------|------|---------------|-----------|-----------|
| Supabase database | All tables (pins, content history, errors, calendars, articles) | CSV export + PITR | Weekly manual, continuous PITR | 7 days (PITR), permanent (CSV) |
| Make.com scenarios | Agent 2A and 2B configurations | JSON blueprint export | Weekly manual | Keep last 5 versions |
| Website code | All site HTML, CSS, JS, articles | Git repository | Continuous (every commit) | Permanent |
| Content JSONs | Brand configs, affiliate configs, content bank | Git repository | Continuous (every commit) | Permanent |
| GitHub Secrets | All API keys and tokens | Encrypted document | Monthly | Keep current only |
| Pinterest board data | Board IDs, names, descriptions | Manual documentation | Monthly | Keep current + previous |

### What Does NOT Need Backup

- Pexels images (always re-fetchable via API)
- Claude API responses (content is stored in Supabase)
- Make.com execution history (auto-retained by Make.com)
- GitHub Actions logs (auto-retained by GitHub)

---

## Automatic Backups

### Supabase Point-in-Time Recovery (PITR)

Supabase Pro plan includes automatic PITR. On the free tier, PITR is not available and you must rely on manual backups.

**How to enable PITR (Pro plan only):**

1. Go to Supabase Dashboard > Settings > Database
2. Scroll to "Point in Time Recovery"
3. Toggle ON
4. Set retention period: 7 days (minimum recommended)

**How PITR works:**
- Supabase continuously logs all database changes (WAL)
- You can restore to any second within the retention window
- Restoration creates a new project with the database state at that point
- PITR does not affect the running project until you explicitly switch

**Free tier alternative:**
- Supabase free tier creates daily backups automatically
- Available under Dashboard > Database > Backups
- These are full database dumps, not point-in-time
- Retention: 7 days of daily backups
- To download: Click the backup date and download the SQL dump

### Git-Based Code Backup

The GitHub repository serves as the primary code backup. All website code, Python automation scripts, configuration files, and workflow definitions are version-controlled.

**Automatic via GitHub Actions:**
- Every push to `main` is backed up to GitHub's servers
- GitHub stores all commit history permanently
- Branch history is preserved even after merge

**To verify the backup is current:**
```bash
git log --oneline -5
git status
```

Ensure no important files are in `.gitignore` that should be backed up.

### Weekly Maintenance Workflow Backup

The `weekly-maintenance.yml` GitHub Actions workflow runs every Sunday and generates a summary JSON that is uploaded as a workflow artifact. This serves as an automatic snapshot of system state.

- **Artifact retention**: 90 days (configured in the workflow)
- **Contains**: Pin counts by brand, error stats, subscriber count
- **Access**: GitHub Actions > weekly-maintenance > [run] > Artifacts

---

## Manual Backup Procedures

### Procedure 1: Export Supabase Tables as CSV

Run these SQL queries in the Supabase SQL Editor. For each table, copy the results and save as a CSV file.

**Step 1: pinterest_pins table**
```sql
-- Export all pins
COPY (
    SELECT *
    FROM pinterest_pins
    ORDER BY created_at DESC
) TO STDOUT WITH CSV HEADER;
```

> **Alternative (Dashboard method):** Go to Table Editor > pinterest_pins > Click "Export" button > Select CSV.

**Step 2: content_history table**
```sql
COPY (
    SELECT *
    FROM content_history
    ORDER BY created_at DESC
) TO STDOUT WITH CSV HEADER;
```

**Step 3: scheduled_inline_pins table**
```sql
COPY (
    SELECT *
    FROM scheduled_inline_pins
    ORDER BY created_at DESC
) TO STDOUT WITH CSV HEADER;
```

**Step 4: weekly_calendar table**
```sql
COPY (
    SELECT *
    FROM weekly_calendar
    ORDER BY created_at DESC
) TO STDOUT WITH CSV HEADER;
```

**Step 5: generated_articles table**
```sql
COPY (
    SELECT *
    FROM generated_articles
    ORDER BY created_at DESC
) TO STDOUT WITH CSV HEADER;
```

**Step 6: errors table**
```sql
COPY (
    SELECT *
    FROM errors
    ORDER BY created_at DESC
) TO STDOUT WITH CSV HEADER;
```

**Step 7: All remaining tables**
```sql
-- Videos
COPY (SELECT * FROM videos ORDER BY created_at DESC) TO STDOUT WITH CSV HEADER;

-- Content bank
COPY (SELECT * FROM content_bank ORDER BY created_at DESC) TO STDOUT WITH CSV HEADER;

-- Subscribers
COPY (SELECT * FROM subscribers ORDER BY created_at DESC) TO STDOUT WITH CSV HEADER;

-- Analytics
COPY (SELECT * FROM analytics ORDER BY created_at DESC) TO STDOUT WITH CSV HEADER;
```

**Save location:** `outputs/database/backups/YYYY-MM-DD/`

**Naming convention:** `tablename_YYYY-MM-DD.csv`

**Full table dump as SQL (for restoration):**
```sql
-- Generate a full CREATE TABLE + INSERT script
-- Run this in psql or the SQL Editor
SELECT 'INSERT INTO content_history (brand, title, description, topic, category, angle_framework, visual_style, board, description_opener, image_query, pexels_image_id, destination_url, posting_method, created_at) VALUES ('
    || quote_literal(brand) || ', '
    || quote_literal(COALESCE(title, '')) || ', '
    || quote_literal(COALESCE(description, '')) || ', '
    || quote_literal(COALESCE(topic, '')) || ', '
    || quote_literal(COALESCE(category, '')) || ', '
    || quote_literal(COALESCE(angle_framework, '')) || ', '
    || quote_literal(COALESCE(visual_style, '')) || ', '
    || quote_literal(COALESCE(board, '')) || ', '
    || quote_literal(COALESCE(description_opener, '')) || ', '
    || quote_literal(COALESCE(image_query, '')) || ', '
    || quote_literal(COALESCE(pexels_image_id, '')) || ', '
    || quote_literal(COALESCE(destination_url, '')) || ', '
    || quote_literal(COALESCE(posting_method, '')) || ', '
    || quote_literal(created_at::text) || ');'
FROM content_history;
```

---

### Procedure 2: Export Make.com Scenarios as JSON

**Step 1: Export Agent 2A (Listicle Creator)**

1. Open Make.com and navigate to the Agent 2A scenario
2. Click the three-dot menu in the bottom-left corner of the scenario editor
3. Select **Export Blueprint**
4. Save the downloaded JSON file as:
   `outputs/documentation/make_backups/agent_2a_listicle_YYYY-MM-DD.json`

**Step 2: Export Agent 2B (Inline Pinner)**

1. Navigate to the Agent 2B scenario
2. Click the three-dot menu > **Export Blueprint**
3. Save as:
   `outputs/documentation/make_backups/agent_2b_inline_YYYY-MM-DD.json`

**Step 3: Document connection details** (do NOT store credentials in plaintext)

Create a file `outputs/documentation/make_backups/connections_YYYY-MM-DD.txt`:
```
Connection 1: Supabase
  - Type: HTTP
  - Base URL: https://epfoxpgrpsnhlsglxvsa.supabase.co
  - Auth: Service Role Key (stored in password manager)

Connection 2: Pinterest (Brand 1)
  - Type: OAuth2
  - Account: [Pinterest username]
  - Scopes: boards:read, pins:read, pins:write

Connection 3: Pinterest (Brand 2)
  - Type: OAuth2
  - Account: [Pinterest username]
  - Scopes: boards:read, pins:read, pins:write
```

---

### Procedure 3: Git Push All Website Code

Ensure all website code is committed and pushed:

```bash
cd /Users/homefolder/Desktop/social-media-empire

# Check for uncommitted changes
git status

# If there are changes, commit them
git add sites/ outputs/ articles/ landing_pages/
git commit -m "backup: weekly code snapshot $(date +%Y-%m-%d)"
git push origin main
```

For subdomain sites deployed via Netlify:
```bash
# List all sites
ls sites/
ls outputs/fitover35-website/
ls outputs/dailydealdarling-website/
ls outputs/menopause-planner-website/
```

Verify these directories are tracked in git (not in `.gitignore`).

---

### Procedure 4: Backup Content JSONs

These are critical configuration files that drive content generation:

```bash
# Content brain (brand configs, hook frameworks, visual styles)
cp video_automation/content_brain.py outputs/database/backups/$(date +%Y-%m-%d)/

# Trend discovery configs
cp video_automation/trend_discovery.py outputs/database/backups/$(date +%Y-%m-%d)/

# Image selector rules
cp video_automation/image_selector.py outputs/database/backups/$(date +%Y-%m-%d)/

# Affiliate config
cp monetization/affiliate_config.json outputs/database/backups/$(date +%Y-%m-%d)/ 2>/dev/null

# Content bank files
cp -r video_automation/content_bank/ outputs/database/backups/$(date +%Y-%m-%d)/content_bank/
```

---

### Procedure 5: Backup GitHub Secrets Documentation

**CRITICAL: Never store actual secrets in plaintext files.** Instead, maintain a reference list of what secrets exist and where to regenerate them.

Save to your password manager (not to a file in the repository):

```
ANTHROPIC_API_KEY: console.anthropic.com > API Keys
PEXELS_API_KEY: pexels.com > API > Your API Key
SUPABASE_URL: supabase.com > Project Settings > API > URL
SUPABASE_KEY: supabase.com > Project Settings > API > service_role key
CREATOMATE_API_KEY: creatomate.com > Account > API Keys
RESEND_API_KEY: resend.com > API Keys
CONVERTKIT_API_KEY: convertkit.com > Settings > Advanced > API Key
CONVERTKIT_API_SECRET: convertkit.com > Settings > Advanced > API Secret
LATE_API_KEY: getlate.dev > Settings > API Keys
LATE_API_KEY_3: getlate.dev > Settings > API Keys (secondary)
MAKE_WEBHOOK_DEALS: make.com > Scenario 1 > Webhook trigger URL
MAKE_WEBHOOK_MENOPAUSE: make.com > Scenario 2 > Webhook trigger URL
PINTEREST_FITNESS_ACCOUNT_ID: Pinterest API > GET /v5/user_account
PINTEREST_FITNESS_BOARD_ID: Pinterest API > GET /v5/boards
NETLIFY_API_TOKEN: netlify.com > User Settings > Applications > Personal access tokens
ALERT_EMAIL: your notification email address
YOUTUBE_CLIENT_ID: Google Cloud Console > Credentials
YOUTUBE_CLIENT_SECRET: Google Cloud Console > Credentials
YOUTUBE_REFRESH_TOKEN: OAuth2 playground or custom flow
GEMINI_API_KEY: ai.google.dev > API Keys
```

---

## Recovery Procedures

### Recovery 1: Supabase Restore from Backup

**Scenario**: Database data is lost, corrupted, or needs to be rolled back.

**Option A: Restore from PITR (Pro plan)**

1. Go to Supabase Dashboard > Settings > Database > Point in Time Recovery
2. Select the target timestamp (when the data was last known good)
3. Click "Start Restore"
4. Supabase will create a new project with the restored data
5. Update all connection strings (SUPABASE_URL, SUPABASE_KEY) to point to the new project:
   - GitHub Secrets
   - Make.com connections
   - Local .env files
6. Verify data integrity with spot checks:
   ```sql
   SELECT COUNT(*) FROM content_history;
   SELECT COUNT(*) FROM pinterest_pins;
   SELECT MAX(created_at) FROM content_history;
   ```
7. Once verified, decommission the old project

**Option B: Restore from Daily Backup (Free tier)**

1. Go to Supabase Dashboard > Database > Backups
2. Download the backup closest to your target date
3. Create a new Supabase project (or use the existing one)
4. Run the backup SQL in the SQL Editor
5. Re-run the schema grants:
   ```sql
   GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated, service_role;
   GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated, service_role;
   ```
6. Update connection strings if using a new project

**Option C: Restore from CSV Backups**

1. Create the tables using the schema files:
   - `database/schemas.sql`
   - `database/content_history_schema.sql`
   - `database/weekly_calendar_schema.sql`
2. For each CSV backup file, use the Supabase Dashboard > Table Editor > Import CSV
3. Or use SQL:
   ```sql
   -- Example: restore content_history from CSV
   -- First, upload the CSV to Supabase Storage or a public URL
   -- Then use the COPY command or the import tool
   ```
4. Verify row counts match the backup

---

### Recovery 2: Make.com Import Scenario JSON

**Scenario**: A Make.com scenario was accidentally deleted, corrupted, or needs to be recreated on a new account.

1. Go to Make.com > Scenarios > Create a new scenario
2. Click the three-dot menu in the bottom-left corner
3. Select **Import Blueprint**
4. Upload the JSON file:
   - `agent_2a_listicle_YYYY-MM-DD.json` for Agent 2A
   - `agent_2b_inline_YYYY-MM-DD.json` for Agent 2B
5. The scenario structure will be imported but connections will be broken
6. Click on each module that shows a red warning:
   - Re-select or re-create the appropriate connection
   - For Supabase modules: select your Supabase connection
   - For HTTP modules: no connection needed (API keys are in headers)
   - For Pinterest modules: reconnect your Pinterest OAuth
7. Update any hardcoded values:
   - API keys in HTTP module headers
   - Supabase project URL
   - Board IDs (may have changed)
8. Run a test execution manually
9. Verify the output at each module
10. Activate the schedule

---

### Recovery 3: Netlify Redeploy from Git

**Scenario**: A Netlify site is broken, shows wrong content, or the deployment was corrupted.

**Quick fix: Trigger a fresh deploy**

1. Go to Netlify Dashboard > [Site name] > Deploys
2. Click "Trigger deploy" > "Clear cache and deploy site"
3. Wait for the build to complete
4. Verify the site loads correctly

**Full restore from a previous deploy:**

1. Go to Netlify Dashboard > [Site name] > Deploys
2. Scroll down to find a known-good deploy
3. Click on that deploy
4. Click "Publish deploy" to make it the live version
5. Verify the site

**Restore from Git:**

1. Find the last known-good commit:
   ```bash
   git log --oneline -20
   ```
2. Check out that commit to verify:
   ```bash
   git checkout <commit-hash> -- sites/
   ```
3. Push the restored code:
   ```bash
   git add sites/
   git commit -m "restore: reverting sites to known-good state"
   git push origin main
   ```
4. Netlify will auto-deploy from the push

**Recreate a Netlify site from scratch:**

1. Go to Netlify Dashboard > Add new site > Import an existing project
2. Connect to GitHub repository
3. Set the publish directory to the appropriate path (e.g., `sites/fitover35/`)
4. Set the build command (if any)
5. Add environment variables if needed
6. Deploy
7. Configure custom domain in Netlify > Domain settings
8. Update the Netlify Site ID in GitHub Secrets if needed

---

### Recovery 4: Content Restore from JSON Backups

**Scenario**: The content configuration files (`content_brain.py`, `content_bank/`, `affiliate_config.json`) were accidentally modified or deleted.

1. Check git history for the last known-good version:
   ```bash
   git log --oneline video_automation/content_brain.py
   ```

2. Restore a specific file from a past commit:
   ```bash
   git checkout <commit-hash> -- video_automation/content_brain.py
   ```

3. Or restore from the backup directory:
   ```bash
   cp outputs/database/backups/YYYY-MM-DD/content_brain.py video_automation/
   ```

4. Verify the file is correct by checking brand configs:
   ```bash
   python3 -c "
   import sys; sys.path.insert(0, '.')
   from video_automation.content_brain import BRAND_CONFIGS
   for brand, config in BRAND_CONFIGS.items():
       print(f'{brand}: {len(config[\"topics_by_category\"])} categories, {len(config[\"pinterest_boards\"])} boards')
   "
   ```

5. Commit the restored file:
   ```bash
   git add video_automation/content_brain.py
   git commit -m "restore: content_brain.py from backup"
   git push origin main
   ```

---

## Disaster Recovery Plan

### Scenario A: Full System Down (All Components)

**Impact**: No pins are being generated or posted. All automation is stopped.

**Recovery Time Objective (RTO)**: 2 hours

**Steps:**

1. **Triage** (5 min):
   - Check each component: Supabase, Make.com, GitHub, Netlify, Pinterest
   - Identify which components are down
   - Check status pages for each service

2. **Quick wins** (15 min):
   - If Supabase paused: Restore project (5-8 min wait)
   - If Make.com scenarios paused: Reactivate them
   - If Netlify deploy failed: Trigger redeploy
   - If GitHub Actions failed: Re-run failed workflows

3. **Deeper fixes** (30-60 min):
   - If API keys rotated: Update keys in GitHub Secrets and Make.com connections
   - If database corrupted: Restore from backup (see Recovery 1)
   - If scenarios broken: Import from JSON backup (see Recovery 2)

4. **Validation** (15 min):
   - Run Agent 2A manually once
   - Verify pin appears on Pinterest
   - Verify Supabase records were created
   - Run Agent 2B manually once
   - Check that inline pins post correctly

5. **Post-incident** (10 min):
   - Document what failed and why
   - Log the incident in the errors table
   - Identify preventive measures

### Scenario B: Single Component Failure

| Component | Impact | Recovery Steps | Time |
|-----------|--------|----------------|------|
| Supabase down | No data storage, dedup fails | Restore project, wait 5-8 min | 10 min |
| Make.com down | No automated posting | Wait for Make.com recovery, or post manually via GitHub Actions | 15 min |
| Claude API down | No content generation | Switch to fallback content from content_bank table, or wait | 5 min |
| Pexels down | No images | Use cached/previous image URLs, or use Unsplash as fallback | 10 min |
| Pinterest API down | Pins queue but don't post | Pins will retry on next run; no data loss | 0 min (auto-recovery) |
| Netlify down | Subdomain sites offline | Sites will auto-recover; no action needed | 0 min |
| GitHub down | No Actions workflows | Make.com scenarios still run independently | 0 min |

### Scenario C: Data Corruption

**Symptoms**: Wrong data in Supabase tables, pins with garbage content, duplicate records everywhere.

**Steps:**

1. **IMMEDIATELY pause all automation**:
   - Pause both Make.com scenarios
   - Disable content-engine GitHub workflow: rename to `content-engine.yml.disabled`

2. **Identify the scope of corruption**:
   ```sql
   -- Check for anomalies in recent data
   SELECT created_at, brand, title, LEFT(description, 50)
   FROM content_history
   ORDER BY created_at DESC
   LIMIT 50;

   -- Check for any records with NULL required fields
   SELECT id, brand, title
   FROM pinterest_pins
   WHERE title IS NULL OR brand IS NULL
   ORDER BY created_at DESC;
   ```

3. **Identify the corruption start time**:
   ```sql
   -- Find when bad data started appearing
   SELECT MIN(created_at) as corruption_start
   FROM content_history
   WHERE title LIKE '%ERROR%' OR title LIKE '%null%' OR LENGTH(title) < 5;
   ```

4. **Delete corrupted records**:
   ```sql
   -- Delete corrupted records (adjust the timestamp)
   DELETE FROM content_history
   WHERE created_at > 'CORRUPTION_START_TIMESTAMP';

   DELETE FROM pinterest_pins
   WHERE created_at > 'CORRUPTION_START_TIMESTAMP';

   DELETE FROM scheduled_inline_pins
   WHERE created_at > 'CORRUPTION_START_TIMESTAMP';
   ```

5. **If corruption is extensive, restore from backup**:
   - Follow Recovery 1 procedures
   - You will lose any legitimate data created after the backup

6. **Fix the root cause**:
   - Review Make.com scenario changes
   - Check for Claude prompt issues
   - Verify Supabase schema hasn't been altered

7. **Reactivate automation**:
   - Re-enable GitHub workflow
   - Reactivate Make.com scenarios
   - Monitor closely for 24 hours

### Scenario D: Account Suspension

| Account | Impact | Recovery |
|---------|--------|----------|
| Pinterest account suspended | No new pins posted | File appeal; pause automation; wait for reinstatement |
| Supabase account suspended | No database access | Contact support; restore to new project from backups |
| Make.com account suspended | No automation runs | Contact support; migrate to new account using JSON backups |
| GitHub account suspended | No Actions, no code access | Contact support; restore from local git clone |
| Netlify account suspended | Sites offline | Contact support; redeploy to Vercel or Cloudflare Pages from git |
| Claude API account suspended | No content generation | Switch to Gemini (already configured); contact Anthropic support |

**Pinterest Suspension Recovery (Most Likely Scenario):**

1. Pause all Make.com scenarios immediately
2. Review the suspension email for specific reasons
3. File an appeal at https://help.pinterest.com/en/business/article/account-suspension
4. While waiting (can take 1-14 days):
   - Continue generating content (store in Supabase, don't post)
   - Prepare a backlog of pins to post once reinstated
   - Review all recent pins for policy compliance
   - Reduce scheduled posting frequency in Make.com scenarios (prepare but don't activate)
5. After reinstatement:
   - Do NOT immediately reactivate automation
   - Manually post 5-10 pins over 2-3 days
   - Then reactivate Agent 2A at 1x/day for one week
   - Gradually increase back to 3x/day over 2 weeks

---

## Backup Schedule Summary

| Task | Frequency | Day/Time | Method | Owner |
|------|-----------|----------|--------|-------|
| Supabase CSV export | Weekly | Sunday 10 AM | Manual (SQL Editor) | Operator |
| Make.com blueprint export | Weekly | Sunday 10 AM | Manual (Export button) | Operator |
| Git push check | Daily | Automated | GitHub Actions + manual verify | Automated |
| GitHub Secrets audit | Monthly | 1st of month | Manual (compare with reference) | Operator |
| Board ID verification | Monthly | 1st of month | Manual (Pinterest API check) | Operator |
| Content brain backup | Weekly | Sunday 10 AM | `cp` to backup dir + git | Operator |
| Full disaster recovery drill | Quarterly | 1st Monday of quarter | Simulate recovery from scratch | Operator |

### Backup Storage Locations

| Backup Type | Primary Location | Secondary Location |
|------------|-----------------|-------------------|
| Supabase CSVs | `outputs/database/backups/YYYY-MM-DD/` | Google Drive / cloud storage |
| Make.com JSONs | `outputs/documentation/make_backups/` | Google Drive / cloud storage |
| Website code | GitHub repository | Local git clone |
| API key reference | Password manager | Encrypted document |
| Content configs | Git repository | `outputs/database/backups/` |
