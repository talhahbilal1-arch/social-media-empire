# System Overview — Pinterest Automation Pipeline

## The Big Picture

The pipeline runs automatically 5 times per day via GitHub Actions (a free CI/CD service).
Each run: generates pin content with Claude → renders an image with Python PIL →
uploads the image to cloud storage → posts to Pinterest via Make.com webhook →
generates a full SEO article → commits the article to your website → deploys.

All of this happens without you touching anything.

---

## Architecture Diagram

```
GitHub Actions (cron: 5x daily)
         │
         ├── Phase 0: Pre-flight check
         │   └── Validates all API keys are present
         │
         ├── Phase 1: Generate Pin Content (Claude API)
         │   ├── Reads recent content history from Supabase
         │   ├── Selects: topic + angle + visual style + board (no repeats)
         │   └── Returns: title, description, image_query, text overlay, board
         │
         ├── Phase 2: Generate Article (Claude API)
         │   └── 800-1200 word SEO article matching the pin topic
         │
         ├── Phase 3: Deploy Article
         │   ├── Commits article HTML to GitHub
         │   └── Vercel auto-deploys brand website
         │
         ├── Phase 4: Create Pin Image (Python PIL)
         │   ├── Fetches background image from Pexels
         │   ├── Renders text overlay (5 possible styles)
         │   └── Saves as 1000×1500px JPEG
         │
         ├── Phase 5: Upload Image
         │   └── Uploads to Supabase Storage (pin-images bucket)
         │
         └── Phase 6: Post to Pinterest
             ├── Sends JSON payload to Make.com webhook
             ├── Make.com scenario routes by brand
             └── Posts to correct Pinterest board
```

---

## How Content Variety Works

The database tracks the last 25-30 pins per brand and prevents repeats on:
- Topic (60+ topics per brand rotated)
- Visual style (7 overlay styles — none used back-to-back 4x)
- Board (routes to correct board by topic category)
- Description opener style (10 styles rotate)
- Image query (never the same background image twice in 25 pins)

This means 300+ unique pins per brand before any topic repeats.

---

## Folder Structure

```
social-media-empire/
├── .github/
│   └── workflows/
│       └── content-engine.yml     ← The main cron job (5x daily)
├── video_automation/
│   ├── content_brain.py           ← Claude content generation
│   ├── pin_image_generator.py     ← PIL image rendering
│   ├── pin_article_generator.py   ← Article generation
│   ├── image_selector.py          ← Pexels image selection
│   ├── supabase_storage.py        ← Image upload
│   └── pinterest_boards.py        ← Board ID mapping
├── database/
│   └── migrations/
│       └── 001_master_schema.sql  ← Full database schema
└── outputs/
    ├── fitover35-website/          ← Brand 1 website files
    ├── dailydealdarling-website/   ← Brand 2 website files
    └── menopause-planner-website/  ← Brand 3 website files
```

---

## The Make.com Connection

Make.com receives a JSON webhook from Python. It routes the pin to the correct
Pinterest account based on the `brand` field. It then posts to the specific board
using the `board_id` field.

**Webhook payload structure:**
```json
{
  "brand": "fitness-made-easy",
  "title": "5 Exercises Men Over 35 Should Stop Doing (#3 Is Destroying Your Knees)",
  "description": "After 35, your joints need a different approach...",
  "image_url": "https://your-supabase-url.co/storage/v1/object/public/pin-images/pin_123.jpg",
  "board_id": "1234567890123456789",
  "destination_url": "https://fitover35.com/articles/exercises-to-avoid-after-35",
  "link": "https://fitover35.com/articles/exercises-to-avoid-after-35"
}
```

---

## Database Tables Used

| Table | Purpose |
|-------|---------|
| `content_history` | Every pin ever made — topic, style, board, title |
| `pinterest_pins` | Pin status tracking (pending/posted/failed) |
| `generated_articles` | SEO articles — content, URL, status |
| `agent_runs` | Pipeline health — last run, success/failure |
| `errors` | Error logging with severity levels |

---

## GitHub Secrets Required

Set these in: GitHub repo → Settings → Secrets → Actions

| Secret | Where to Get It |
|--------|----------------|
| `ANTHROPIC_API_KEY` | console.anthropic.com → API Keys |
| `PEXELS_API_KEY` | pexels.com/api → Get Started |
| `SUPABASE_URL` | Supabase Dashboard → Project Settings → API |
| `SUPABASE_KEY` | Supabase Dashboard → Project Settings → API → service_role key |
| `MAKE_WEBHOOK_FITNESS` | Make.com → Your scenario → Webhook URL |
| `MAKE_WEBHOOK_DEALS` | Make.com → Your scenario → Webhook URL |
| `MAKE_WEBHOOK_MENOPAUSE` | Make.com → Your scenario → Webhook URL |
| `VERCEL_BRAND_TOKEN` | vercel.com → Settings → Tokens (personal access token) |

---

## Cost Breakdown (Real Numbers)

| Service | Monthly Cost | Notes |
|---------|-------------|-------|
| Claude API | $15-45/mo | Depends on article length. ~$0.01 per pin+article |
| GitHub Actions | Free | 2,000 min/month free — pipeline uses ~150 min/month |
| Pexels | Free | API is completely free |
| Make.com | Free | Free tier covers 1,000 operations/month |
| Supabase | Free | Free tier covers this volume |
| Vercel | Free | Free tier for 3 static sites |
| **Total** | **~$20-45/mo** | Nearly all cost is Claude API |

---

## Adapting This for Your Niche

The system is brand-agnostic. To add a new niche:
1. Add a new entry to `BRAND_CONFIGS` in `content_brain.py`
2. Create a Make.com scenario for that brand
3. Add the webhook URL as a GitHub Secret
4. Create a Vercel project for the website
5. Run the pipeline

You can run 1 brand on the same code as 10 brands.
