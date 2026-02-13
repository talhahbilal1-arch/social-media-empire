# Backup and Recovery Documentation

## Social Media Empire - Comprehensive Backup Guide

This document provides detailed procedures for backing up and restoring all critical components of the Social Media Empire automation system.

---

## 1. Make.com Scenario Backup

Make.com scenarios are the backbone of the Pinterest posting automation. Regular backups ensure quick recovery if scenarios are accidentally modified or deleted.

### How to Export Scenarios

**Step 1: Access Your Scenarios**
1. Log into Make.com at https://www.make.com
2. Navigate to "Scenarios" in the left sidebar
3. Locate the scenario you want to backup (e.g., "Pinterest Idea Pin Poster")

**Step 2: Export the Scenario**
1. Click on the scenario to open it
2. Click the three-dot menu (more options) in the bottom-left corner
3. Select "Export Blueprint"
4. The scenario will download as a JSON file

**Step 3: Verify the Export**
1. Open the downloaded JSON file in a text editor
2. Verify it contains the scenario configuration
3. Check that all module connections are present

### Recommended Backup Frequency

| Scenario Type | Backup Frequency | Rationale |
|---------------|------------------|-----------|
| Production scenarios | Weekly | Active scenarios change infrequently |
| After any modification | Immediately | Capture changes before potential issues |
| Before major updates | Always | Create restore point |

### Where to Store Backups

**Primary Storage:**
```
/social-media-empire/backups/make-scenarios/
    ├── pinterest-poster/
    │   ├── pinterest-poster_2026-01-27.json
    │   ├── pinterest-poster_2026-01-20.json
    │   └── ...
    └── other-scenarios/
```

**Secondary Storage (Recommended):**
- Cloud storage (Google Drive, Dropbox, or iCloud)
- GitHub repository (private, for version control)
- External backup drive (quarterly archive)

### Naming Conventions

Use the following format for backup files:
```
{scenario-name}_{YYYY-MM-DD}_{version}.json
```

Examples:
- `pinterest-idea-pin-poster_2026-01-27_v1.json`
- `pinterest-video-webhook_2026-01-27_v2.json`

### Version Control Recommendations

1. **Git Repository:**
   ```bash
   # Create a dedicated branch for Make.com backups
   git checkout -b make-backups

   # Add backup files
   git add backups/make-scenarios/
   git commit -m "Backup Make.com scenarios - $(date +%Y-%m-%d)"

   # Push to remote
   git push origin make-backups
   ```

2. **Changelog:**
   Maintain a `CHANGELOG.md` in the scenarios folder documenting:
   - Date of change
   - What was modified
   - Who made the change
   - Reason for change

---

## 2. Supabase Data Backup

Supabase stores all operational data including videos, subscribers, content bank, and analytics.

### Using Supabase Dashboard for Backups

**Method 1: Point-in-Time Recovery (Pro Plan)**
1. Navigate to your Supabase project dashboard
2. Go to "Settings" > "Database"
3. Under "Backups", enable Point-in-Time Recovery
4. Backups are automatically created every day
5. Retention: 7 days (Pro), 14 days (Enterprise)

**Method 2: Manual CSV Export**
1. Go to "Table Editor" in Supabase dashboard
2. Select the table you want to export
3. Click the "Export" button (download icon)
4. Choose CSV format
5. Save to your backup location

### pg_dump Commands for Manual Backup

**Full Database Backup:**
```bash
# Set environment variables
export PGPASSWORD="your-database-password"
export DB_HOST="db.your-project-ref.supabase.co"
export DB_NAME="postgres"
export DB_USER="postgres"

# Create full backup
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME \
    --format=custom \
    --file=backups/supabase/full_backup_$(date +%Y%m%d).dump
```

**Table-Specific Backups:**
```bash
# Backup videos table
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME \
    --table=videos \
    --format=custom \
    --file=backups/supabase/videos_$(date +%Y%m%d).dump

# Backup subscribers table
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME \
    --table=subscribers \
    --format=custom \
    --file=backups/supabase/subscribers_$(date +%Y%m%d).dump

# Backup content_bank table
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME \
    --table=content_bank \
    --format=custom \
    --file=backups/supabase/content_bank_$(date +%Y%m%d).dump
```

**SQL-Format Backup (Human-Readable):**
```bash
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME \
    --format=plain \
    --file=backups/supabase/full_backup_$(date +%Y%m%d).sql
```

### Automated Backup Setup

**Option 1: GitHub Actions Workflow**

Create `.github/workflows/database-backup.yml`:
```yaml
name: Database Backup

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
  workflow_dispatch:

jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Install PostgreSQL client
        run: sudo apt-get install -y postgresql-client

      - name: Create backup
        env:
          PGPASSWORD: ${{ secrets.SUPABASE_DB_PASSWORD }}
        run: |
          pg_dump -h ${{ secrets.SUPABASE_DB_HOST }} \
            -U postgres \
            -d postgres \
            --format=custom \
            --file=backup_$(date +%Y%m%d).dump

      - name: Upload to cloud storage
        # Add your preferred cloud storage upload step
        run: echo "Upload backup to cloud storage"
```

**Option 2: Local Cron Job**
```bash
# Add to crontab (crontab -e)
0 3 * * * /path/to/social-media-empire/scripts/backup_database.sh
```

### What Data to Prioritize

**Critical (Backup Daily):**
| Table | Priority | Reason |
|-------|----------|--------|
| `subscribers` | CRITICAL | Cannot be recreated, subscriber data |
| `content_bank` | HIGH | Content ideas and usage tracking |
| `email_sequences` | HIGH | Email automation state |

**Important (Backup Weekly):**
| Table | Priority | Reason |
|-------|----------|--------|
| `videos` | MEDIUM | Historical record, can be partially rebuilt |
| `posting_schedule` | MEDIUM | Scheduling data |
| `analytics` | MEDIUM | Performance tracking |

**Lower Priority (Backup Monthly):**
| Table | Priority | Reason |
|-------|----------|--------|
| `errors` | LOW | Troubleshooting history |

### Backup Retention Policy

| Backup Type | Retention Period | Storage Location |
|-------------|------------------|------------------|
| Daily backups | 7 days | Local + Cloud |
| Weekly backups | 4 weeks | Cloud storage |
| Monthly backups | 12 months | Archive storage |
| Yearly backups | Indefinite | Archive storage |

---

## 3. Content Bank Backup

The content bank consists of JSON files containing video topics and ideas.

### JSON File Backup Procedures

**Content Bank Files Location:**
```
/social-media-empire/video_automation/content_bank/
    ├── deal_topics.json
    ├── menopause_topics.json
    └── wellness_ideas.json
```

**Manual Backup Script:**
```bash
#!/bin/bash
# scripts/backup_content_bank.sh

BACKUP_DIR="backups/content_bank/$(date +%Y%m%d)"
SOURCE_DIR="video_automation/content_bank"

mkdir -p "$BACKUP_DIR"

# Copy all JSON files
cp "$SOURCE_DIR"/*.json "$BACKUP_DIR/"

# Create compressed archive
tar -czf "backups/content_bank_$(date +%Y%m%d).tar.gz" "$BACKUP_DIR"

echo "Content bank backed up to $BACKUP_DIR"
```

### Version Control with Git

**Recommended Git Workflow:**

1. **Track Content Changes:**
   ```bash
   # Stage content bank changes
   git add video_automation/content_bank/*.json

   # Commit with descriptive message
   git commit -m "Content bank: Add new menopause topics for February"
   ```

2. **Branch Strategy:**
   ```bash
   # Create feature branch for major content updates
   git checkout -b content/february-2026-topics

   # Make changes
   # ... edit JSON files ...

   # Merge back to main
   git checkout main
   git merge content/february-2026-topics
   ```

3. **Git Ignore Pattern:**
   Ensure backup directories are properly handled in `.gitignore`:
   ```
   # Local backups (don't commit)
   backups/

   # But DO commit content bank
   !video_automation/content_bank/
   ```

### Cloud Storage Options

| Service | Use Case | Setup |
|---------|----------|-------|
| Google Drive | Team collaboration | Sync folder or API upload |
| Dropbox | Automatic sync | Desktop app sync |
| AWS S3 | Automated backups | CLI or SDK upload |
| iCloud | macOS integration | Native folder sync |

**AWS S3 Backup Script:**
```bash
#!/bin/bash
# scripts/backup_to_s3.sh

BUCKET="your-backup-bucket"
PREFIX="social-media-empire/content-bank"

aws s3 sync video_automation/content_bank/ \
    s3://$BUCKET/$PREFIX/$(date +%Y%m%d)/ \
    --exclude "*.pyc"
```

---

## 4. Restore Procedures

### Restoring Make.com Scenarios from JSON

**Step 1: Access Import Feature**
1. Log into Make.com
2. Navigate to "Scenarios"
3. Click "Create a new scenario" (+ button)
4. Click the three-dot menu in the bottom-left
5. Select "Import Blueprint"

**Step 2: Upload and Configure**
1. Select your backup JSON file
2. Review the imported modules
3. Reconnect any connections that show as disconnected
4. Update webhook URLs if they have changed

**Step 3: Test the Restored Scenario**
1. Click "Run once" to test
2. Verify data flows correctly through all modules
3. Check output in connected services
4. Enable scheduling once verified

**Troubleshooting Common Issues:**
- **Connection errors:** Re-authorize OAuth connections
- **Webhook URLs changed:** Update trigger module with new URL
- **Missing modules:** Reinstall required apps in Make.com

### Restoring Supabase from Backup

**Method 1: pg_restore (Custom Format)**
```bash
# Restore full database
pg_restore -h $DB_HOST -U $DB_USER -d $DB_NAME \
    --clean \
    --if-exists \
    backups/supabase/full_backup_20260127.dump

# Restore specific table
pg_restore -h $DB_HOST -U $DB_USER -d $DB_NAME \
    --table=subscribers \
    --clean \
    backups/supabase/subscribers_20260127.dump
```

**Method 2: SQL File Restore**
```bash
# Restore from SQL file
psql -h $DB_HOST -U $DB_USER -d $DB_NAME \
    < backups/supabase/full_backup_20260127.sql
```

**Method 3: Supabase Dashboard (Point-in-Time)**
1. Go to Supabase dashboard > Settings > Database
2. Select "Backups" section
3. Choose the point-in-time to restore
4. Click "Restore" and confirm

**Post-Restore Verification:**
```sql
-- Verify row counts
SELECT 'videos' as table_name, COUNT(*) FROM videos
UNION ALL
SELECT 'subscribers', COUNT(*) FROM subscribers
UNION ALL
SELECT 'content_bank', COUNT(*) FROM content_bank
UNION ALL
SELECT 'analytics', COUNT(*) FROM analytics;
```

### Restoring Content Banks

**Step 1: Identify Correct Backup**
```bash
# List available backups
ls -la backups/content_bank/

# Or find in git history
git log --oneline video_automation/content_bank/
```

**Step 2: Restore Files**
```bash
# From local backup
cp backups/content_bank/20260127/*.json video_automation/content_bank/

# From git history
git checkout <commit-hash> -- video_automation/content_bank/

# From compressed archive
tar -xzf backups/content_bank_20260127.tar.gz
cp content_bank/20260127/*.json video_automation/content_bank/
```

**Step 3: Validate JSON Files**
```bash
# Validate JSON syntax
python -m json.tool video_automation/content_bank/deal_topics.json > /dev/null && echo "Valid"
python -m json.tool video_automation/content_bank/menopause_topics.json > /dev/null && echo "Valid"
python -m json.tool video_automation/content_bank/wellness_ideas.json > /dev/null && echo "Valid"
```

### Verification After Restore

**1. Run Health Check:**
```bash
python -m monitoring.health_checker --full
```

**2. Test Video Generation (Dry Run):**
```bash
python -m video_automation.daily_video_generator --dry-run
```

**3. Verify Database Connectivity:**
```python
from database.supabase_client import get_supabase_client
db = get_supabase_client()
print(f"Recent videos: {len(db.get_recent_videos())}")
```

---

## 5. Disaster Recovery Checklist

### Complete System Failure Recovery

In the event of a complete system failure, follow this checklist in order:

#### Phase 1: Assessment (15-30 minutes)
- [ ] Identify scope of failure (which components affected)
- [ ] Check if GitHub repository is accessible
- [ ] Verify backup availability and recency
- [ ] Notify team members if applicable
- [ ] Document the failure for post-mortem

#### Phase 2: Infrastructure Recovery (30-60 minutes)
- [ ] Verify GitHub Actions is operational
- [ ] Check Supabase project status
- [ ] Confirm Make.com account access
- [ ] Verify all API keys are still valid

#### Phase 3: Data Recovery (1-2 hours)
- [ ] Restore Supabase database from latest backup
- [ ] Verify database tables and row counts
- [ ] Restore content bank JSON files
- [ ] Verify content bank data integrity

#### Phase 4: Automation Recovery (1-2 hours)
- [ ] Import Make.com scenarios from backup
- [ ] Reconnect all Make.com integrations
- [ ] Test Make.com webhooks
- [ ] Verify GitHub Actions workflows are active
- [ ] Test workflow triggers manually

#### Phase 5: Verification (30-60 minutes)
- [ ] Run full health check
- [ ] Execute dry-run video generation
- [ ] Test email sending (if applicable)
- [ ] Verify all platforms are posting correctly
- [ ] Monitor first automated run

### Priority Order for Restoration

| Priority | Component | Est. Time | Dependency |
|----------|-----------|-----------|------------|
| 1 | GitHub Repository | 15 min | None |
| 2 | Environment Variables/Secrets | 15 min | GitHub |
| 3 | Supabase Database | 30-60 min | None |
| 4 | Content Bank Files | 15 min | GitHub |
| 5 | Make.com Scenarios | 30-45 min | Supabase |
| 6 | GitHub Actions Workflows | 15 min | All above |
| 7 | Test & Verify | 30-60 min | All above |

### Contact Information for Support

| Service | Support URL | Response Time |
|---------|-------------|---------------|
| Supabase | https://supabase.com/dashboard/support | 24-48 hours |
| Make.com | https://www.make.com/en/help | 24-48 hours |
| GitHub | https://support.github.com | Varies by plan |
| Creatomate | https://creatomate.com/docs | 24-48 hours |
| YouTube API | https://developers.google.com/youtube | Community forums |

**Emergency Contacts:**
- Project owner: [Add contact information]
- Technical lead: [Add contact information]
- Backup administrator: [Add contact information]

### Estimated Recovery Times

| Scenario | Recovery Time | Complexity |
|----------|---------------|------------|
| Single table corruption | 15-30 minutes | Low |
| Full database restore | 1-2 hours | Medium |
| Make.com scenario restore | 30-45 minutes | Medium |
| Complete system recovery | 4-6 hours | High |
| New environment setup | 8-12 hours | Very High |

### Post-Recovery Verification

**Automated Verification Script:**
```bash
#!/bin/bash
# scripts/verify_recovery.sh

echo "=== Post-Recovery Verification ==="

# 1. Check Python syntax
echo "Checking Python syntax..."
python -m py_compile video_automation/*.py
python -m py_compile email_marketing/*.py
python -m py_compile monitoring/*.py

# 2. Run health check
echo "Running health check..."
python -m monitoring.health_checker --full

# 3. Test database connection
echo "Testing database..."
python -c "from database.supabase_client import get_supabase_client; db = get_supabase_client(); print('Database: OK')"

# 4. Validate content bank
echo "Validating content bank..."
for f in video_automation/content_bank/*.json; do
    python -m json.tool "$f" > /dev/null && echo "$f: Valid"
done

# 5. Dry run video generation
echo "Dry run video generation..."
python -m video_automation.daily_video_generator --dry-run

echo "=== Verification Complete ==="
```

---

## 6. Regular Backup Schedule

### What to Backup Daily/Weekly/Monthly

#### Daily Backups
| Component | Method | Automation |
|-----------|--------|------------|
| Supabase `subscribers` table | pg_dump | GitHub Actions |
| Supabase `content_bank` table | pg_dump | GitHub Actions |
| Supabase `email_sequences` table | pg_dump | GitHub Actions |
| Error logs | API export | GitHub Actions |

#### Weekly Backups
| Component | Method | Automation |
|-----------|--------|------------|
| Full Supabase database | pg_dump | GitHub Actions |
| Make.com scenarios | Manual export | Calendar reminder |
| Content bank JSON files | Git commit | Pre-commit hook |
| Analytics data | CSV export | Manual |

#### Monthly Backups
| Component | Method | Storage |
|-----------|--------|---------|
| Full system snapshot | All methods | Archive storage |
| Video templates | Export from Creatomate | Cloud storage |
| Email templates | Git archive | Cloud storage |
| Configuration files | Git archive | Cloud storage |

### Automation Options

**Option 1: GitHub Actions Backup Workflow**

Create `.github/workflows/scheduled-backup.yml`:
```yaml
name: Scheduled Backup

on:
  schedule:
    # Daily at 3 AM UTC
    - cron: '0 3 * * *'
  workflow_dispatch:

jobs:
  daily-backup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Backup critical tables
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
        run: python scripts/backup_critical_tables.py

      - name: Upload backup artifacts
        uses: actions/upload-artifact@v4
        with:
          name: daily-backup-${{ github.run_number }}
          path: backups/
          retention-days: 7

  weekly-backup:
    runs-on: ubuntu-latest
    if: github.event.schedule == '0 3 * * 0'  # Sundays only
    steps:
      - uses: actions/checkout@v4

      - name: Full database backup
        run: |
          # Full backup commands here
          echo "Performing weekly full backup"
```

**Option 2: Local Automation (macOS)**

Create a LaunchAgent for automated backups:
```xml
<!-- ~/Library/LaunchAgents/com.socialmediaempire.backup.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.socialmediaempire.backup</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/social-media-empire/scripts/daily_backup.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>3</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
</dict>
</plist>
```

### Storage Requirements

**Estimated Storage per Backup:**

| Component | Size (Approx.) | Growth Rate |
|-----------|---------------|-------------|
| Supabase full backup | 50-200 MB | 5-10 MB/month |
| Content bank JSON | 1-5 MB | Minimal |
| Make.com scenarios | 100-500 KB | Minimal |
| Analytics export | 10-50 MB | 10-20 MB/month |

**Recommended Storage Allocation:**

| Backup Type | Storage Needed | Location |
|-------------|---------------|----------|
| Daily (7 days) | 1-2 GB | Local + Cloud |
| Weekly (4 weeks) | 1-2 GB | Cloud |
| Monthly (12 months) | 3-5 GB | Archive |
| **Total** | **5-10 GB** | Mixed |

### Backup Monitoring

**Create a Backup Health Dashboard:**
```python
# scripts/check_backup_status.py
import os
from datetime import datetime, timedelta
from pathlib import Path

def check_backup_freshness():
    backup_dir = Path("backups")
    issues = []

    # Check daily backups
    daily_backup = backup_dir / "supabase" / f"daily_{datetime.now().strftime('%Y%m%d')}.dump"
    if not daily_backup.exists():
        issues.append("Daily Supabase backup missing")

    # Check content bank was committed recently
    content_dir = Path("video_automation/content_bank")
    for json_file in content_dir.glob("*.json"):
        mtime = datetime.fromtimestamp(json_file.stat().st_mtime)
        if datetime.now() - mtime > timedelta(days=7):
            issues.append(f"Content bank file not updated: {json_file.name}")

    return issues

if __name__ == "__main__":
    issues = check_backup_freshness()
    if issues:
        print("Backup Issues Found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("All backups are current.")
```

---

## Quick Reference Card

### Emergency Commands

```bash
# Immediate full backup
pg_dump -h $DB_HOST -U postgres -d postgres -Fc > emergency_backup.dump

# Quick content bank backup
tar -czf content_bank_emergency.tar.gz video_automation/content_bank/

# Check backup status
python scripts/check_backup_status.py

# Verify system health
python -m monitoring.health_checker --full
```

### Key File Locations

| Component | Location |
|-----------|----------|
| Content Bank | `/video_automation/content_bank/` |
| Database Schema | `/database/schemas.sql` |
| Supabase Client | `/database/supabase_client.py` |
| Health Checker | `/monitoring/health_checker.py` |
| Local Backups | `/backups/` (create if needed) |

### Backup Verification Checklist

- [ ] Backup files exist and are recent
- [ ] Backup files are not corrupted (can be opened/restored)
- [ ] Backup includes all critical data
- [ ] Restore procedure has been tested
- [ ] Off-site copy exists
- [ ] Team knows restore procedures

---

*Last Updated: January 27, 2026*
*Document Version: 1.0*
