# Fix-All Plan — 2026-04-23

Goal: address every issue surfaced in the 2026-04-23 audit. Scoped realistically — separates "I can do now" from "you unblock".

---

## Phase 0 — Commit pending audit (≈1 min)

**Why:** stop-hook is complaining about uncommitted changes (`tasks/todo.md` was edited by the audit).
- [ ] `git add tasks/todo.md && git commit -m "docs(audit): 2026-04-23 internal audit + fix plan"`
- [ ] `git push -u origin claude/audit-projects-ad4IW`
- [ ] Confirm push succeeded.

---

## Phase 1 — Merge unblocking PRs (≈15 min, needs your OK)

Four PRs from Apr 17 are stale. Article-count gates in their bodies are now satisfied.

- [ ] **PR #30** — pilottools ads.txt. Trivial. Low risk. **Recommend merge.**
- [ ] **PR #32** — DDD AdSense + affiliate `rel="nofollow sponsored"` fix. DDD has 140 articles (gate was 18–20). **Recommend merge.**
- [ ] **PR #33** — Menopause AdSense + YMYL disclaimers + Terms/Contact/About. Menopause has 118 articles (gate was 20). **Recommend merge.** *Note: Formspree contact form needs a form ID; your PR body already flags this as a post-merge task.*
- [ ] **PR #31** — pilottools editorial layer. Not trivial (460 pages rebuilt, homepage changed). **Recommend visual spot-check first** — I'll pull the branch, `next build`, and confirm before merging.

**Risk:** PRs modify shared state (deployed sites). I'll ask for explicit approval per PR before merging.

---

## Phase 2 — Branch cleanup (≈5 min, destructive → needs your OK)

- [ ] List all `claude/*` branches on origin.
- [ ] For each: check if tip SHA is an ancestor of `main` OR if the branch's most recent commit is >14 days old with no open PR.
- [ ] Bulk-delete the merged/abandoned ones. Keep: `claude/audit-projects-ad4IW` (current), any branches attached to open PRs, anything touched in last 7 days.
- [ ] Fix `auto-merge.yml` — current pattern `claude/{check-github-automation,merge-to-main,check-workflow-status}-*` misses audit/feature branches. Add `claude/audit-*` and `claude/fix-*` (already matches some, but not all).

**Risk:** deleting a branch that had unmerged work. Mitigation: only delete if tip SHA is in main's ancestry OR commit author was github-actions[bot] (auto-generated, replayable).

---

## Phase 3 — Diagnostic visibility: real workflow run status (≈30 min)

I can't see Actions runs via MCP. I'll build you a local tool.

- [ ] Create `scripts/check_workflow_runs.py`:
  - Reads `GITHUB_TOKEN` from env (or `.env`)
  - Hits `GET /repos/talhahbilal1-arch/social-media-empire/actions/workflows`
  - For each workflow: fetch last 5 runs, show conclusion (success/failure/cancelled/in_progress), timestamp, duration
  - Outputs a markdown table identical in shape to the audit's workflow table, but with REAL pass/fail data
  - Also dumps a ranked list of "workflows with ≥3 failures in last 10 runs"
- [ ] Run it once, paste output into `monitoring/workflow-runs-<date>.md`.
- [ ] **This replaces guesswork with ground truth — you'll know exactly which workflows are red.**

**Dependency:** needs a GitHub PAT with `actions:read` scope. I'll document how to create one.

---

## Phase 4 — Converge video pipeline to one strategy (needs your decision)

Three video paths coexist. I'll keep exactly one and delete the others.

**Options (pick one):**

| Option | What stays | What gets deleted | Best for |
|---|---|---|---|
| **A — Remotion in CI** (current default) | `video_pipeline/remotion_*`, CI render step | `scripts/local_video_pipeline.py`, launchd plist, Short Video Maker client | Fully cloud — no local Mac dependency |
| **B — Local Mac via Short Video Maker** (the April 21–22 direction) | `scripts/local_video_pipeline.py`, launchd plist, `short_video_maker_client.py` | Remotion path, Zernio-only flow | Faster iteration, offloads GPU render from CI |
| **C — Keep both, clean seams** | Both paths, but gate cleanly via `VIDEO_STRATEGY` flag and document | Late API dead-ends + any duplicate scene-building code | If you genuinely want redundancy |

**Regardless of choice:**
- [ ] Delete the 4 `LATE_API_KEY*` references and call sites. They all 401. If you want to keep Late as a fallback, re-add after you refresh tokens.
- [ ] Run Supabase migration 004 (`video_state` column on `pinterest_pins`) — required for option B, harmless for A. SQL is in `database/migrations/004_*.sql`.
- [ ] Post-convergence: re-run content-engine once with `dry_run=true` to confirm.

**My default recommendation:** Option A (Remotion in CI) — keeps everything reproducible without a running Mac. Local pipeline adds a failure mode ("is my laptop awake?") you don't want for a revenue system.

---

## Phase 5 — Create `docs/NEEDS-USER-ACTION.md` (≈15 min)

A single, prioritized checklist of the things only you can do. I'll generate it; you execute.

- [ ] **CONVERTKIT_API_KEY + CONVERTKIT_API_SECRET** — highest revenue impact. Unblocks: menopause-newsletter, revenue-activation, toolpilot-newsletter, weekly-summary, email-automation. Instructions: app.kit.com → Settings → Developer.
- [ ] **RESEND_API_KEY + ALERT_EMAIL** — unblocks: emergency-alert, toolpilot-outreach (real send, not just log), toolpilot-report, weekly-summary. Instructions: resend.com/api-keys.
- [ ] **MAKE_WEBHOOK_PILOTTOOLS** — unblocks PilotTools Pinterest posting. Create scenario in Make.com, copy webhook URL.
- [ ] **VERCEL_ORG_ID** — unblocks toolpilot-{content,deploy,weekly} deploys. Copy from Vercel dashboard → Settings → General.
- [ ] **Refresh LATE_API_KEY** — only needed if Phase 4 picks option that keeps Late. Otherwise delete.
- [ ] **Supabase migration 004** — run `database/migrations/004_*.sql` in Supabase SQL editor. Required for `VIDEO_STRATEGY=local`.
- [ ] **Gumroad: upload 10 product ZIPs** from `prompt-packs/products/` to their listings. Files exist and are ready.
- [ ] **Etsy shop**: complete banking/billing setup. Manual, no code side.
- [ ] **Twitter/LinkedIn secrets** — verify if you've already set these (recent commits suggest yes); if not, instructions per workflow.

Each item gets: what, where, estimated time, revenue/risk impact.

---

## Phase 6 — Repo hygiene (≈30 min, low risk)

### 6a. Root doc consolidation
- [ ] Move into `docs/reports/`: AUDIT_REPORT.md, AUDIT_MAKE_COM.md, AUDIT_FINDINGS_SUMMARY.txt, MORNING_REPORT.md, OVERNIGHT-SESSION-REPORT.md, PINTEREST_STATUS.md, REVENUE_FIX_REPORT.md, SECRETS_AUDIT_2026-03-21.md, SECRETS_QUICK_REFERENCE.txt, TASK_COMPLETION_REPORT.txt, WORKFLOW_GUIDE.md, PROMPT_PACK_HANDOFF.md, PINTEREST_CTR_NOTES.md, SUBMISSION_GUIDE.md, ANTI_GRAVITY_DEPLOY.md, AG_PLAN.md.
- [ ] Keep at root: CLAUDE.md, README.md, LICENSE, CNAME, PHONE-ACTION-CHECKLIST.md.
- [ ] Update any references to moved files.

### 6b. Archive cleanup decision
- [ ] 24 workflows in `.github/workflows/archive/`. Options:
  - **Keep all** (current, zero risk) — reference material
  - **Delete ones that will never return** (tiktok-*, youtube-*, video-automation-*, creatomate-dependent) — saves ~12 files; git history preserves them anyway
- Recommend: delete the 12 that explicitly depend on abandoned services (TikTok token, YouTube creds, Creatomate, ElevenLabs, Late).

### 6c. Duplicate site directories (HIGHER RISK — verify first)
- `dailydealdarling_website/`, `menopause-planner-site/` (legacy roots) vs `outputs/{brand}-website/` (deploy source per CLAUDE.md).
- `outputs_backup/` — snapshot, safe to delete once confirmed it's not a live deploy target.
- [ ] Grep CI workflows + vercel.json for any path reference to the legacy roots.
- [ ] If zero references: delete legacy dirs + outputs_backup/.
- [ ] Commit in isolation so a revert is clean if something breaks.

---

## Phase 7 — Strategic decisions on dormant projects (needs your input)

Each needs a finish-or-deprecate call. I'll mark explicitly in CLAUDE.md whichever you pick.

| Project | State | Finish = | Deprecate = |
|---|---|---|---|
| **TikTok automation** | Token missing, workflows archived, code in `tiktok_automation/` | Refresh token, restore tiktok-content + tiktok-poster workflows, unblock | Delete `tiktok_automation/`, delete secondary Supabase project tables, remove from CLAUDE.md |
| **YouTube Shorts** | Deferred per AG_PLAN, no credentials, workflow archived | Add YouTube OAuth creds, re-enable `youtube-fitness.yml` | Delete `youtube-fitness.yml` from archive, remove references in prior workflows |
| **Anti-Gravity site** | `anti_gravity/` has site + DB + 5 articles, never deployed | `vercel --prod` deploy, add to CLAUDE.md brands table | Delete `anti_gravity/`, remove from AG_PLAN/ANTI_GRAVITY_DEPLOY |
| **Etsy shop** | Listings JSON exists, banking setup pending | Complete banking → `etsy-product-pins.yml` becomes meaningful | Archive `etsy-product-pins.yml`, delete `etsy_listings.json` |
| **Phase 13 stash** | `git stash pop` restores it | Review what's in stash, merge or drop | `git stash drop` after inspection |

**My default recommendation:** deprecate TikTok + YouTube + Anti-Gravity (consistent with the "3 active brands" principle in CLAUDE.md). Finish Etsy only if the revenue forecast justifies the banking-setup friction. Pop the Phase 13 stash and decide per-file.

---

## Phase 8 — Post-cleanup verification (≈10 min)

- [ ] Re-run: `python3 -m py_compile` on core modules
- [ ] Re-run: YAML validate on all workflows
- [ ] Re-run: `scripts/check_workflow_runs.py` (from Phase 3) → paste new numbers to `monitoring/workflow-runs-<date>.md`
- [ ] Update CLAUDE.md "Current Status" section with post-cleanup state
- [ ] Final commit + push

---

## Decisions I need from you before I start

1. **Phase 1 PR merges** — green-light all four, or handle case-by-case?
2. **Phase 2 branch deletion** — OK to auto-delete branches whose tips are already in main?
3. **Phase 4 video strategy** — A (Remotion CI), B (Local Mac), or C (keep both)?
4. **Phase 6c duplicate dir deletion** — OK to delete after grep verification, or you want to see the list first?
5. **Phase 7 dormant projects** — deprecate TikTok/YouTube/Anti-Gravity, or finish any?
6. **Phase 3 GitHub PAT** — will you create one, or should I write a version that reads `~/.config/gh/hosts.yml` from an existing `gh` CLI login?

## What this plan does NOT cover

- Live runtime Supabase queries (would need `.env` loaded in this session)
- Visual QA on deployed brand sites (no browser in this session)
- The other 2 repos under your `talhahbilal1-arch` GitHub account (MCP token scope)

## Review
_(to be filled after execution)_
