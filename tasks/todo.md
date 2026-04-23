# Fix-All Plan — 2026-04-23 (plain-English version)

## How to read this

Each item below says:
- **What happens** — the actual change
- **Why it matters** — what gets better for you
- **Who does it** — me vs. you
- **Risk** — what could go wrong

I grouped items by outcome, not by phase, so you can pick what matters most.

---

## GROUP A: Start earning money that's currently blocked

### A1. Merge the 3 stuck AdSense PRs (#30, #32, #33)
- **What happens:** Three pull requests from April 17 get merged into main. They add Google AdSense tags + legal pages (Terms/Contact/About) + a fix that tells Google "these are ad links, don't count them for SEO" to dailydealdarling.com, menopauseplanner.com, and pilottools.ai.
- **Why it matters:** You can't earn AdSense revenue until these are live. All three sites now have enough articles to pass Google's "low value content" bar, which was the reason you paused. Money is currently sitting on the table.
- **Who does it:** I merge them after you say yes. Then you manually click "Request Review" in your AdSense console once Google re-scans the sites (~48 hours after merge).
- **Risk:** Low. The changes are additive — they don't modify existing article content. One task on your side: plug a Formspree form ID into the new menopause Contact page (or just use the mailto link that's already there).

### A2. Set up ConvertKit API keys
- **What happens:** You add 2 secrets to GitHub (`CONVERTKIT_API_KEY`, `CONVERTKIT_API_SECRET`). I don't need to change any code — the automation already exists.
- **Why it matters:** 333 articles across your 3 brands have email signup forms baked in. Every visitor who signs up right now goes into a list that never sends them anything. Adding the keys activates:
  - Welcome email sequences for new subscribers
  - Weekly newsletter for Menopause Planner
  - PilotTools newsletter
  - Weekly summary reports to you
- **Who does it:** You — get keys from app.kit.com → Settings → Developer, paste into GitHub repo secrets.
- **Risk:** None. Without the keys the workflows just skip. With them, they start working.

### A3. Upload 10 Gumroad product ZIP files
- **What happens:** You drag-drop 10 ZIP files from `prompt-packs/products/` into their Gumroad listings.
- **Why it matters:** Some of your Gumroad products may not have a deliverable attached — customers pay and can't download. This takes maybe 20 minutes total.
- **Who does it:** You. I can't access your Gumroad account.
- **Risk:** None.

---

## GROUP B: Stop things that are silently broken

### B1. Pick one video-pin strategy, delete the other two
- **What happens:** Right now your repo has three different ways to make and post video pins to Pinterest, all partially wired. Pick one, I delete the code for the other two.
  - **Option A — Remotion in GitHub Actions** (simplest, runs in cloud, no Mac required)
  - **Option B — Local pipeline on your Mac** (faster, but only works when your laptop is awake)
  - **Option C — Keep both** (more resilient, more to maintain)
- **Why it matters:** Having three strategies means three places for bugs to hide. Every time you touch video code, you have to remember which path is actually live. Removing two simplifies everything.
- **Who does it:** You decide which one; I do the delete.
- **Risk:** Low if we pick carefully. I'll test with `dry_run=true` before committing.

### B2. Remove dead Late API code
- **What happens:** `LATE_API_KEY`, `LATE_API_KEY_2`, `_3`, `_4` are all expired. Any code that tries to use them returns 401 errors. I delete the code paths.
- **Why it matters:** Cleaner logs. If you decide later to go back to Late, we add it back — git history keeps everything.
- **Who does it:** Me (after Group B1 decision).
- **Risk:** Low. These calls currently fail anyway.

### B3. Run the Supabase migration (video_state column)
- **What happens:** You paste a small SQL file into Supabase SQL Editor and hit Run. Takes 5 seconds.
- **Why it matters:** The local video pipeline (if you picked Option B above) needs this column to track which pins are waiting to be rendered. Without it, the pipeline silently falls back to old behavior.
- **Who does it:** You. The SQL is at `database/migrations/004_add_video_state_to_pinterest_pins.sql`.
- **Risk:** None — it's an ADD COLUMN, doesn't touch existing data.

---

## GROUP C: Actually see what your automation is doing

### C1. Build a workflow status checker
- **What happens:** I write a small Python script you can run any time (`python3 scripts/check_workflow_runs.py`) that prints a table: workflow name, last 5 runs, green or red, how long each took.
- **Why it matters:** Right now, nobody (including me) actually knows how many of your 39 workflows are succeeding vs. failing. I've been inferring from git commits, which only catches some of them. This script gives you the real answer.
- **Who does it:** I write it. You run it with a GitHub token (I'll give you one-line instructions to create one).
- **Risk:** None — script only reads data, never modifies anything.

### C2. One clean "Things only you can do" checklist
- **What happens:** I create `docs/NEEDS-USER-ACTION.md` — a single file with every pending manual task in priority order, each one saying: what to do, where to do it, how long it takes, what it unblocks.
- **Why it matters:** Instead of scattered action items across 8+ old audit docs, you get one page. Cross items off as you go.
- **Who does it:** I write it. You work through it.
- **Risk:** None.

---

## GROUP D: Clean up the repo (easier to navigate)

### D1. Delete ~47 abandoned branches
- **What happens:** Your GitHub repo has 47+ branches named things like `claude/blissful-villani` from old Claude sessions. Most have no unique work. I delete the ones whose commits are already in `main` (so nothing is lost) or that are older than 14 days with no pull request.
- **Why it matters:** Branch picker in GitHub UI becomes usable. Current state is unreadable.
- **Who does it:** Me, after you say yes.
- **Risk:** Very low. I only delete branches where the work is already merged OR abandoned + ancient.

### D2. Move 15 old audit docs out of the repo root
- **What happens:** Files like `AUDIT_REPORT.md`, `MORNING_REPORT.md`, `OVERNIGHT-SESSION-REPORT.md`, etc. move from the root folder into `docs/reports/`. Active files (CLAUDE.md, README.md, PHONE-ACTION-CHECKLIST.md) stay at the root.
- **Why it matters:** When you open the repo, you see ~15 current/useful files instead of ~30 mixed ones. The old reports are still there for reference, just in a subfolder.
- **Who does it:** Me.
- **Risk:** Low. I check for any code that references the moved files first and update paths.

### D3. Delete duplicate site directories (AFTER checking nothing breaks)
- **What happens:** You have `outputs/dailydealdarling-website/` (live) AND `dailydealdarling_website/` (legacy). Same for menopause. Plus `outputs_backup/`. I delete the unused copies.
- **Why it matters:** Right now it's not obvious which folder deploys to which site. After cleanup, each brand has exactly one folder.
- **Who does it:** Me, after grepping the codebase to confirm nothing reads from the legacy folders.
- **Risk:** **Medium.** This is where I'll pause and show you the list before deleting.

### D4. Delete ~12 obsolete archived workflows
- **What happens:** In `.github/workflows/archive/` there are workflows for TikTok, YouTube, Creatomate video rendering, ElevenLabs voiceover, and the old Late rescue-poster. If you're never bringing these services back, I delete the files. (Git history keeps them if you change your mind.)
- **Why it matters:** Fewer files to sift through when searching.
- **Who does it:** Me, after Group E below.
- **Risk:** Low — they're already archived, so deleting them changes nothing runtime-wise.

---

## GROUP E: Decide what to do with half-built projects

Each of these was started but isn't currently running. Pick "finish" or "kill" for each.

### E1. TikTok automation
- **Currently:** Code exists in `tiktok_automation/`, workflows archived, token missing.
- **Finish:** Get TikTok API token, restore workflows, start posting.
- **Kill:** Delete `tiktok_automation/`, delete the TikTok tables in your secondary Supabase project.
- **My recommendation:** Kill. You said in CLAUDE.md you're focused on 3 brands on Pinterest.

### E2. YouTube Shorts
- **Currently:** Workflow archived, no credentials.
- **Finish:** Set up YouTube OAuth, re-enable workflow.
- **Kill:** Delete the archived workflow file.
- **My recommendation:** Kill. You marked this "deferred" a year ago.

### E3. Anti-Gravity home office site
- **Currently:** 5 seed articles, SQLite database, never deployed.
- **Finish:** Run `vercel --prod`, add as 4th brand to the system.
- **Kill:** Delete `anti_gravity/`.
- **My recommendation:** Your call — you've mentioned deploying it before. If you're not going to in the next 30 days, kill it and restart later if you want.

### E4. Etsy shop
- **Currently:** Product listings exist as JSON, banking setup incomplete, Etsy pin workflow live but posting to nothing useful.
- **Finish:** Complete Etsy banking/billing setup (manual, on etsy.com).
- **Kill:** Archive the workflow, delete listings JSON.
- **My recommendation:** Finish only if you're ready to commit to running an Etsy store. Otherwise kill.

### E5. Phase 13 stashed work
- **Currently:** Some unfinished work is sitting in `git stash`.
- **Options:** I run `git stash show` to see what's in it, then either pop (restore) or drop (delete).
- **My recommendation:** Show you the contents, then you decide.

---

## What you need to decide

Answer these 6 questions and I start executing:

1. **AdSense PRs** — merge all 4? Or skip any?
2. **Abandoned branches** — OK to bulk-delete merged/old branches?
3. **Video strategy** — A (cloud/Remotion), B (local Mac), or C (keep both)?
4. **Duplicate site folders** — delete after I show you the list, or don't touch?
5. **TikTok / YouTube / Anti-Gravity / Etsy** — finish any, or kill all?
6. **GitHub token for workflow status script** — you'll create one, or should I make the script reuse your existing `gh` CLI login if you have one?

## What happens after you answer

Once you approve:
1. I execute each group, committing after each logical chunk so you can see progress
2. After everything, I re-run the audit and post "what changed" before/after numbers
3. You work through `docs/NEEDS-USER-ACTION.md` at your own pace (ConvertKit keys, Gumroad uploads, etc.)

## What this plan WON'T do

- Touch live deployed sites (only the merges trigger deploys, via Vercel auto-deploy)
- Modify any content in existing articles
- Delete anything without showing you first (for the medium-risk items in Group D)
- Affect the other 2 repos in your GitHub account (I don't have access)

## Review
_(to be filled after execution)_
