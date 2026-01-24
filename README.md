# Social Media Empire

Automated content creation and distribution system for multiple brands across social media platforms.

## Overview

Social Media Empire automates the entire content pipeline from idea generation to multi-platform posting for:

- **Daily Deal Darling** - Lifestyle deals and product recommendations
- **Menopause Planner** - Menopause wellness and support
- **Nurse Planner** - Nurse lifestyle and self-care
- **ADHD Planner** - ADHD-friendly productivity tips

## Features

### Video Automation
- AI-powered content generation using Google Gemini
- Stock media from Pexels API
- Video rendering via Creatomate
- Multi-platform posting (YouTube Shorts, Pinterest, TikTok, Instagram Reels)
- Scheduled posting (6 AM, 12 PM, 6 PM PST)

### Email Marketing
- ConvertKit integration for subscriber management
- Resend for transactional emails
- Automated welcome sequences (7 emails per brand)
- Weekly newsletter templates
- Website signup forms (popup, inline, footer)

### Monitoring & Reliability
- Health checks for all integrated services
- Error tracking and alerting
- Daily performance reports
- Self-healing automation for failed tasks

## Architecture

```
social-media-empire/
├── .github/workflows/     # GitHub Actions automation
├── video_automation/      # Video generation system
├── email_marketing/       # Email campaigns and forms
├── database/              # Supabase integration
├── monitoring/            # Health checks and reporting
├── utils/                 # Shared utilities and API clients
└── products/              # Brand-specific product assets
```

## Quick Start

### Prerequisites
- Python 3.11+
- GitHub account with Actions enabled
- API keys for all integrations

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/social-media-empire.git
cd social-media-empire

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your API keys
```

### Environment Variables

Create a `.env` file with:

```env
# AI Services
ANTHROPIC_API_KEY=your_key
GEMINI_API_KEY=your_key

# Media Services
PEXELS_API_KEY=your_key
CREATOMATE_API_KEY=your_key

# Database
SUPABASE_URL=your_url
SUPABASE_KEY=your_key

# Email
RESEND_API_KEY=your_key
CONVERTKIT_API_KEY=your_key
CONVERTKIT_API_SECRET=your_secret

# Social Platforms
YOUTUBE_CLIENT_ID=your_id
YOUTUBE_CLIENT_SECRET=your_secret
YOUTUBE_REFRESH_TOKEN=your_token
MAKE_COM_PINTEREST_WEBHOOK=your_webhook

# Alerts
ALERT_EMAIL=your_email
```

### GitHub Secrets

Add these secrets to your repository for GitHub Actions:
- All environment variables listed above

### Database Setup

Run the schema in Supabase SQL Editor:

```bash
# The schema is in database/schemas.sql
```

## Usage

### Generate Videos Manually

```bash
# Generate for all brands
python -m video_automation.daily_video_generator

# Generate for specific brand
python -m video_automation.daily_video_generator --brand daily_deal_darling

# Dry run (don't post)
python -m video_automation.daily_video_generator --dry-run
```

### Health Checks

```bash
# Run full health check
python -m monitoring.health_checker --full

# Quick check (critical services only)
python -m monitoring.health_checker

# Output as JSON
python -m monitoring.health_checker --json
```

### Daily Reports

```bash
# Generate report
python -m monitoring.daily_report_generator

# Generate and send via email
python -m monitoring.daily_report_generator --send
```

### Error Reporting

```bash
# View error summary
python -m monitoring.error_reporter --summary

# Send error digest
python -m monitoring.error_reporter --digest
```

## GitHub Actions Workflows

| Workflow | Schedule | Description |
|----------|----------|-------------|
| video-automation-morning | 6 AM PST | Generate and post morning videos |
| video-automation-noon | 12 PM PST | Generate and post noon videos |
| video-automation-evening | 6 PM PST | Generate and post evening videos |
| email-automation | 9 AM, 5 PM PST | Process email sequences |
| health-monitoring | Every 4 hours | Check service health |
| error-alerts | Hourly | Monitor for critical errors |
| daily-report | 9 PM PST | Send daily performance report |
| self-healing | Every 6 hours | Retry failed tasks, cleanup |

## API Integrations

| Service | Purpose | Documentation |
|---------|---------|---------------|
| Google Gemini | AI content generation | [API Docs](https://ai.google.dev/docs) |
| Pexels | Stock photos/videos | [API Docs](https://www.pexels.com/api/documentation/) |
| Creatomate | Video rendering | [API Docs](https://creatomate.com/docs/api/introduction) |
| Supabase | Database | [API Docs](https://supabase.com/docs) |
| Resend | Email delivery | [API Docs](https://resend.com/docs/api-reference) |
| ConvertKit | Email marketing | [API Docs](https://developers.convertkit.com/) |
| YouTube | Video uploads | [API Docs](https://developers.google.com/youtube/v3) |
| Make.com | Pinterest webhooks | [Documentation](https://www.make.com/en/help) |

## Monitoring

### Health Score

The system calculates a health score (0-100) based on:
- Video completion rate (40 points)
- Service health (30 points)
- Error status (30 points)

### Alerts

Alerts are sent for:
- Critical service failures
- Failed video generation
- Unresolved critical errors
- Daily summaries

## Development

### Running Tests

```bash
pytest tests/
```

### Code Style

```bash
# Check style
flake8 .

# Format code
black .
```

### Adding a New Brand

1. Add brand config in `utils/config.py`
2. Add content generator config in `video_automation/video_content_generator.py`
3. Create video template in `video_automation/templates/`
4. Add content bank in `video_automation/content_bank/`
5. Create email sequence in `email_marketing/sequences/`
6. Add ConvertKit setup in `email_marketing/convertkit_setup/`

## Troubleshooting

### Common Issues

**Videos not posting:**
- Check API credentials in GitHub Secrets
- Verify Creatomate template IDs
- Check Make.com webhook status

**Emails not sending:**
- Verify Resend API key
- Check domain verification
- Review ConvertKit form IDs

**Health check failing:**
- Run manual health check with `--full` flag
- Check specific service status
- Verify API quotas

### Logs

- GitHub Actions logs: Check workflow runs
- Database logs: Query `errors` table in Supabase
- Health history: Query `analytics` table for `event_type='health_check'`

## License

This project is proprietary. All rights reserved.

## Support

For issues, please create a GitHub issue or contact the development team.
