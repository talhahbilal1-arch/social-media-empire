# Launch Checklist — FitOver35 Body Recomposition Blueprint

Sequential. Check items off as they ship. No item is optional for launch day.

---

## Phase A — Product Setup (manual, 1 day)

- [ ] Create Gumroad product "The FitOver35 Body Recomposition Blueprint"
- [ ] Set primary price to $97
- [ ] Enable Pay-What-You-Want with floor $47 (opt-in toggle on Gumroad product settings)
- [ ] Set URL slug: `fitover35-blueprint`
- [ ] Paste `gumroad-product-description.md` contents into the Gumroad description field
- [ ] Upload cover image (1280x720 JPG, brass + obsidian theme)
- [ ] Set category to Fitness, tags: `men over 35`, `body recomposition`, `strength`, `fat loss`
- [ ] Enable Gumroad receipts with custom thank-you message and Discord invite link
- [ ] Enable affiliate program (see `affiliate-program-setup.md`)

## Phase B — PDF Upload (automated)

- [ ] PDF generation complete in `products/signature/build/` (separate video-rendering step)
- [ ] Run Playwright uploader: `python3 automation/playwright/gumroad_upload.py --product fitover35-blueprint --file products/signature/build/blueprint.pdf`
- [ ] Verify Gumroad preview loads all sections
- [ ] Trigger test purchase at PWYW $0 (author account) to confirm delivery email and download link

## Phase C — Web Integration

- [ ] Copy `products/signature/landing-page.html` to `outputs/fitover35-website/products/blueprint/index.html`
- [ ] Replace Kit form placeholder div with actual Kit embed script for form 8946984
- [ ] Add blueprint tile to `outputs/fitover35-website/products/index.html` product grid
- [ ] Add nav-bar link "Blueprint" on `outputs/fitover35-website/index.html`
- [ ] Commit and push to trigger Vercel deploy
- [ ] Verify live at `fitover35.com/products/blueprint/`
- [ ] Submit updated sitemap to Google Search Console

## Phase D — Content Distribution

- [ ] Insert 3 new `content_ready` rows into Supabase `pinterest_pins` pointing at blueprint landing page
- [ ] Trigger `video_automation/pin_image_generator.py` manually (or wait for next content-engine run)
- [ ] Verify 3 pins posted via Make.com webhook to fitness Pinterest board
- [ ] Write and commit 5 SEO articles linking to the product. Target keywords:
  1. "best workout program for men over 35"
  2. "how to build muscle at 40"
  3. "body recomposition over 40"
  4. "strength training after 35 with joint pain"
  5. "3-day split for busy men"
- [ ] Articles must include a CTA block at 40% and 90% mark pointing to `/products/blueprint/`

## Phase E — Email + Social

- [ ] Kit broadcast to fitover35 list (form 8946984) — "It's here. The Blueprint."
- [ ] Schedule 10 Twitter/X threads via PilotTools distribution engine (`distribution/weekly-posts/`)
- [ ] LinkedIn post on personal brand account
- [ ] Reddit post in r/Fitness30plus (follow sub rules, flair as "Resource")
- [ ] Pinterest idea pins (5) via `post-product-pins.yml`

## Phase F — Measurement

- [ ] Add blueprint revenue line to `revenue-intelligence.yml` daily tracker
- [ ] Create GA4 conversion event `blueprint_purchase` with $97 value
- [ ] Wire Gumroad purchase webhook into Supabase `content_history` with `product = blueprint`
- [ ] Add daily revenue line-item on `outputs/fitover35-website/dashboard/index.html`
- [ ] Set $10k/mo target tile on dashboard with progress bar

## Phase G — Ongoing

- [ ] Collect first 10 testimonials, replace `[TESTIMONIAL_1..3]` placeholders in description and landing page
- [ ] Weekly refresh of Pinterest pin variants (automated — content engine handles this)
- [ ] Quarterly live Q&A recording uploaded to buyer-only portal, Discord announcement
- [ ] Monthly review: conversion rate, refund rate, LTV, top-referring Pinterest pins
