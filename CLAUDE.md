# CLAUDE.md - Project Context for AI Assistants

## Project Overview

Social Media Empire is an automated content creation and distribution system for multiple lifestyle brands. It generates video content using AI, renders videos with templates, and posts to multiple social media platforms on a schedule.

## Key Components

### 1. Video Automation (`video_automation/`)
- **daily_video_generator.py**: Main orchestrator for video creation pipeline
- **video_content_generator.py**: Uses Gemini AI to generate video scripts
- **video_templates.py**: Manages Creatomate video templates
- **cross_platform_poster.py**: Posts to all platforms
- **youtube_shorts.py**: YouTube-specific upload logic
- **pinterest_idea_pins.py**: Pinterest-specific posting via Make.com

### 2. Email Marketing (`email_marketing/`)
- **email_sender.py**: Sends emails via Resend, integrates with ConvertKit
- **sequences/**: Welcome email sequences (markdown templates)
- **website_integration/**: HTML signup forms
- **convertkit_setup/**: ConvertKit automation configuration

### 3. Database (`database/`)
- **supabase_client.py**: All database operations
- **schemas.sql**: Database schema (run in Supabase SQL Editor)

### 4. Monitoring (`monitoring/`)
- **health_checker.py**: Checks all API integrations
- **error_reporter.py**: Logs and alerts on errors
- **daily_report_generator.py**: Creates daily performance reports

### 5. GitHub Actions (`.github/workflows/`)
- 3 video automation workflows (morning/noon/evening)
- Email automation workflow
- Health monitoring workflow
- Error alerts workflow
- Daily report workflow
- Self-healing workflow

## Brands

| Brand | Niche | Audience |
|-------|-------|----------|
| daily_deal_darling | Lifestyle deals, beauty, home | Budget-conscious women 25-45 |
| menopause_planner | Menopause wellness | Women 45-60 |
| nurse_planner | Nurse lifestyle, self-care | Healthcare workers |
| adhd_planner | ADHD productivity | Adults with ADHD |

## API Dependencies

| API | Purpose | Rate Limits |
|-----|---------|-------------|
| Gemini | Content generation | 60 RPM |
| Pexels | Stock media | 200 req/hour |
| Creatomate | Video rendering | Per plan |
| Supabase | Database | Per plan |
| Resend | Email sending | 100/day free |
| ConvertKit | Email marketing | Per plan |
| YouTube | Video uploads | Quota-based |
| Make.com | Pinterest webhook | Per plan |

## Common Tasks

### Adding Content Ideas
Edit the JSON files in `video_automation/content_bank/`:
- `wellness_ideas.json` - Cross-brand wellness content
- `deal_topics.json` - Daily Deal Darling specific
- `menopause_topics.json` - Menopause Planner specific

### Modifying Video Templates
Edit files in `video_automation/templates/`:
- Each brand has its own template config
- Templates reference Creatomate template IDs
- Colors and fonts are brand-specific

### Creating Email Sequences
Add markdown files to `email_marketing/sequences/`:
- Follow existing sequence structure
- Include timing, tags, and content
- Reference in `email_sender.py` if needed

### Adding a New Platform
1. Create poster module in `video_automation/`
2. Add client to `utils/api_clients.py`
3. Add to `cross_platform_poster.py`
4. Add secrets to GitHub repository
5. Update workflow environment variables

## Code Patterns

### Configuration
```python
from utils.config import get_config
config = get_config()
# Access: config.gemini_api_key, config.brands, etc.
```

### Database Operations
```python
from database.supabase_client import get_supabase_client
db = get_supabase_client()
db.log_video_creation(brand="...", platform="...", ...)
```

### Error Reporting
```python
from monitoring.error_reporter import report_error
report_error(
    error_type="api_failure",
    error_message="...",
    severity="high",
    context={"brand": "...", "platform": "..."}
)
```

### Health Checks
```python
from monitoring.health_checker import run_health_check
result = run_health_check(full=True)
# result["overall_status"] is "healthy", "degraded", or "unhealthy"
```

## Environment Variables

Required for local development:
```
GEMINI_API_KEY
PEXELS_API_KEY
SUPABASE_URL
SUPABASE_KEY
```

Optional (for full functionality):
```
ANTHROPIC_API_KEY
CREATOMATE_API_KEY
RESEND_API_KEY
CONVERTKIT_API_KEY
CONVERTKIT_API_SECRET
YOUTUBE_CLIENT_ID
YOUTUBE_CLIENT_SECRET
YOUTUBE_REFRESH_TOKEN
MAKE_COM_PINTEREST_WEBHOOK
ALERT_EMAIL
```

## Testing

```bash
# Syntax check all Python files
python -m py_compile video_automation/*.py
python -m py_compile email_marketing/*.py
python -m py_compile monitoring/*.py

# Run health check
python -m monitoring.health_checker --full

# Dry run video generation
python -m video_automation.daily_video_generator --dry-run
```

## Deployment Notes

1. All secrets must be in GitHub repository settings
2. Creatomate templates must be created and IDs updated
3. YouTube OAuth must be set up and refresh token obtained
4. Make.com scenarios must be created for Pinterest
5. ConvertKit forms and tags must be created
6. Supabase tables must be created from schemas.sql

## File Naming Conventions

- Python modules: `snake_case.py`
- Templates: `brand_type.json`
- Workflows: `purpose-name.yml`
- Sequences: `brand_sequence_type.md`

## Important Notes

- Videos are 30 seconds, 9:16 aspect ratio (vertical)
- 3 videos per day per brand = 12 total daily videos
- Schedule is PST timezone
- Error alerts go to ALERT_EMAIL
- Self-healing runs every 6 hours
- Old data cleaned up after 30-90 days
