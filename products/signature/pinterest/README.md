# Blueprint Launch — Pinterest Pin Seeder

Three dedicated Pinterest pins that drive directly to the $97 FitOver35 Body
Recomposition Blueprint landing page (`https://fitover35.com/products/blueprint/`).

## What this does

1. `pins.json` — declarative pin content (title, description, overlay text,
   image query, board ID, link URL, style, tips). Three pins covering the three
   biggest buyer objections.
2. `seed_pins.py` — reads `pins.json` and inserts each pin into the Supabase
   `pinterest_pins` table with `status='content_ready'`. Also logs to
   `content_history` for variety tracking.

Once seeded, the next scheduled `content-engine.yml` run (6 AM, 9 AM, 12 PM,
3 PM, or 7 PM PST) automatically:

- Picks up `content_ready` rows in Phase 1
- Renders the PIL pin image (using the `style` field — `gradient`, `numbered_list`,
  or `big_stat`) over a Pexels background fetched from `image_query`
- Uploads the JPEG to Supabase Storage
- POSTs to the per-brand Make.com webhook (`MAKE_WEBHOOK_FITNESS`), which posts
  to the Pinterest board listed in `board_id`

No new code paths, no new workflow — the existing rendering and posting
pipeline handles everything.

## Why seed pins this way (vs. creating them manually in Pinterest)

- The content engine already handles image rendering, Supabase Storage upload,
  and Make.com posting. Manual Pinterest creation would skip image rendering,
  skip the watermark/overlay style, and lose pin-level analytics in
  `pinterest_pins`.
- Seeded pins flow through the same status machine as auto-generated ones
  (`content_ready` -> `rendering` -> `ready` -> `posting` -> `posted`), so they
  show up in the pin watchdog, error logs, and analytics dashboard for free.
- Repeatable: re-seed the same JSON file if Make.com drops a pin, or trickle
  one pin per day with `--count 1` to spread the launch over a week.

## The 3 pin angles

| # | Style          | Angle                                                | Why                                                   |
|---|----------------|------------------------------------------------------|-------------------------------------------------------|
| 1 | `big_stat`     | "Lost 22 Pounds at 41 Without Running a Single Mile" | Proof it works at 40+, kills the cardio objection.    |
| 2 | `numbered_list`| "5 Lifts That Build Muscle After 40 (Most Skip 3)"   | Curiosity-gap listicle, proven Pinterest CTR pattern. |
| 3 | `gradient`     | "The 3-Day Lifting Split for Busy Men Over 35"       | Kills the "I don't have time for 6 days/week" objection. |

All three target the fitness "Workouts for Men Over 35" board
(ID `418834902785123337`).

## Commands

Dry run — print every payload, no DB writes:

```bash
python3 products/signature/pinterest/seed_pins.py --dry-run
```

Trickle in one pin per day (run daily for 3 days):

```bash
python3 products/signature/pinterest/seed_pins.py --count 1
```

Seed all three at once:

```bash
python3 products/signature/pinterest/seed_pins.py
```

## Required environment

The script uses `database/supabase_client.py` if available, otherwise falls
back to raw `SUPABASE_URL` + `SUPABASE_KEY` env vars. In CI these are pulled
from GitHub secrets; locally, source them from `.env` or export them first.

## After seeding

Either wait for the next scheduled content-engine run, or trigger it manually
in GitHub Actions UI (`Actions -> content-engine.yml -> Run workflow`).
Watch the run logs for `Found N content_ready pins` in Phase 1 — that is your
seeded pins being picked up.
