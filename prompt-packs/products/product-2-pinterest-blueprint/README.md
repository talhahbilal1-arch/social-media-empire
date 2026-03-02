# Pinterest Automation Blueprint
## The Exact System That Posts 15 Pins/Day Across 3 Brands — Documented and Exported

**This is not a theoretical guide. This is the working system, documented.**

The system runs on GitHub Actions (free), Claude API, Pexels (free tier), Make.com,
and Supabase (free tier). It posts 5 pins/day per brand, generates SEO articles,
deploys them to brand websites, and tracks everything in a database.

Total running cost: ~$20-40/month in Claude API. Everything else is free.

---

## What's Inside

| File | Contents |
|------|---------|
| `01-system-overview.md` | Full architecture — how all parts connect |
| `02-claude-prompts.md` | The exact Claude prompts that generate pin content |
| `03-pinterest-hooks.md` | 45 hook frameworks used by the live system |
| `04-makecom-guide.md` | Make.com scenario setup — step by step |
| `05-pexels-setup.md` | Image selection system — zero banned images |
| `06-content-strategy.md` | Brand voice, topic categories, scheduling logic |

---

## The Stack (All Free or Near-Free)

| Tool | Purpose | Cost |
|------|---------|------|
| GitHub Actions | Runs the pipeline 5x/day automatically | Free |
| Claude API (Sonnet) | Generates all pin content and articles | ~$20-40/mo |
| Pexels API | Background images for pin graphics | Free |
| Make.com | Posts to Pinterest via webhook | Free tier |
| Supabase | Database — tracks content history, avoids repeats | Free tier |
| PIL (Python) | Renders text overlay on images | Free (library) |
| Vercel | Hosts brand websites + SEO articles | Free |

---

## What This System Produces Daily

- 5 Pinterest pins per brand (15 total across 3 brands)
- 5 SEO articles per brand (1 per pin topic)
- Unique Pexels image per pin
- Text overlay rendered on image
- Posted to the right Pinterest board automatically
- Everything logged to database so nothing repeats

---

## Who This Is For

- Pinterest marketers wanting to automate content creation
- Digital product sellers wanting consistent Pinterest traffic
- Bloggers and affiliate marketers driving traffic to websites
- Anyone who wants to build a Pinterest presence without spending hours daily

---

## Prerequisites

You need accounts for (all have free tiers):
- GitHub
- Anthropic (Claude API) — the only real cost
- Pexels API
- Make.com
- Supabase
- Pinterest Business Account
- Vercel (if you want the article blog integration)
