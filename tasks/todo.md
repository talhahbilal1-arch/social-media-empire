# Project Audit — 2026-04-23

## Scope

Internal audit of all active projects across the `talhahbilal1-arch/social-media-empire` monorepo.

**Important scope limitation:** GitHub MCP access in this session is restricted to ONE repo — `talhahbilal1-arch/social-media-empire`. The authenticated account reports 3 public repos; the other two could not be inspected in this session. Everything below is based on this monorepo plus any local filesystem content.

## Plan
- [x] Confirm auth + repo access scope
- [x] Pull open PRs, issues, branches
- [x] Re-read existing audit/status docs (AUDIT_REPORT, PINTEREST_STATUS, MORNING_REPORT, workflow-health, system-health)
- [x] Recent commit pattern + article counts + sitemap counts
- [x] Inspect side projects (PilotTools/ai-tools-hub, Anti-Gravity, TikTok, Gumroad, quizzes, Etsy)
- [x] Compile-check core modules, YAML-validate every workflow

---

## Review

### 1. WORKING ✅ — production pipelines running on schedule

| System | Evidence |
|---|---|
| **Content Engine** (content-engine.yml, 5x/day) | Bot commits "pinterest: auto-post 2026-04-22" at 17:11 + 22:37 UTC yesterday, plus "content: auto-generated 2026-04-22" 07:32 UTC. Daily cadence unbroken across 4 weeks of git log. |
| **Article generation** | Counts grew substantially since the April 2 audit: FitOver35 148 → **200** (+52), DailyDealDarling 99 → **140** (+41), Menopause 86 → **118** (+32). Sitemaps: 189 / 127 / 108 URLs. |
| **Pinterest posting (images)** | Per-brand Make.com webhooks firing; MORNING_REPORT confirms HTTP 200 end-to-end for fitness/deals/menopause. Make.com dashboard (last captured 2026-03-31) shows 9 active scenarios, 0 errors, 2,904 ops. |
| **Analytics dashboard** | "analytics: update dashboard" committed daily (latest 2026-04-22). |
| **Vercel deploys** | 3 brand sites + PilotTools auto-deploy on push; ads.txt present at all 4 properties. |
| **Supabase Production** | `errors`/`content_history`/`agent_runs` upserts working (no recent schema-column errors in commits). |
| **Compile / YAML health** | Core Python modules compile clean. **All 39 workflow YAMLs parse valid.** |
| **Gumroad products** | 10/11 ZIPs present in `prompt-packs/products/` — just need manual Gumroad upload. |
| **Hygiene: archived workflows** | 24 broken workflows correctly moved to `.github/workflows/archive/` rather than deleted (reversible). |

### 2. IN-FLIGHT / RECENTLY LANDED — be aware

| Item | State |
|---|---|
| **Video-pin pipeline rewrite** | Mid-refactor. Last week (Apr 19–22): switched from Make.com video path to Zernio API, added Remotion, then pivoted again to a local "Short Video Maker" Mac pipeline via launchd (commits `503b1cc`, `9e9e981`, `c6116db`). `VIDEO_STRATEGY=local` flag gates which path runs. **Posting only enabled for `fitness` brand** in `local_video_pipeline.py` (`POSTING_BRANDS={'fitness'}`). Deals + menopause video pins render + stage but do not post. |
| **DB migration 004** | `video_state` column on `pinterest_pins` needs to be run in Supabase before `VIDEO_STRATEGY=local` is flipped in production (see `e3a34fe`). CI has a graceful fallback (`e47d871`) but the migration is required for steady-state. |
| **AdSense compliance** | Live on all 6 brand renderers (b31064d, 2026-04-22). Root-level ads.txt at all 4 sites. |
| **20 buyer-intent articles** | Landed 2026-04-22 — 7 FitOver35, 7 DDD, 6 Menopause. Sitemap regenerated (412 URLs total). |

### 3. NOT WORKING / BLOCKED ❌

| Problem | Impact | Fix |
|---|---|---|
| **4 open PRs stale since 2026-04-17 (6 days)** — #30 pilottools ads.txt, #31 pilottools editorial layer, #32 DDD AdSense, #33 Menopause AdSense | Blocks AdSense revenue activation on DDD, Menopause, PilotTools. **Article-count gates in the PR bodies are now satisfied** (DDD 140 ≥ 18, Menopause 118 ≥ 20), so the stated blocker is stale. | Merge #30 + #32 + #33 (AdSense prep). Merge #31 only after visual spot-check. |
| **~47 orphan `claude/*` branches on GitHub** | Noise; confuses audit surface; slows branch pickers | Bulk-delete branches whose tips are merged into main; keep only active feature branches. |
| **ConvertKit API keys still missing** | 4 workflows can't run: `menopause-newsletter`, `revenue-activation`, `toolpilot-newsletter`, `weekly-summary`. Forms are embedded on 333+ articles but no welcome sequence or broadcast. Biggest revenue leak in the audit. | Add `CONVERTKIT_API_KEY` + `CONVERTKIT_API_SECRET` as repo secrets. |
| **Resend API key missing** | Emergency alerts, outreach, weekly reports, toolpilot-report all non-functional. Dead-man's-switch has no teeth. | `RESEND_API_KEY` + `ALERT_EMAIL`. |
| **All Twitter / LinkedIn secrets missing** | PilotTools Twitter, Repurpose, LinkedIn workflows are shipping dry-run. AG_PLAN calls this "BUILD COMPLETE" but the external accounts are not wired. | Add Twitter 4-tuple + `LINKEDIN_ACCESS_TOKEN` + `LINKEDIN_PERSON_ID`. |
| **`MAKE_WEBHOOK_PILOTTOOLS` missing** | PilotTools Pinterest fires but no scenario receives. | Create Make.com scenario, add secret. |
| **Late API keys expired (401)** | Video-pin posting via Late broken. Partly mitigated by the Zernio switch, but any remaining Late call paths return 401. | Refresh at getlate.dev, OR delete the Late code paths now that Zernio/local-pipeline is the strategy. |
| **Gemini image-gen model 404** | Pins fall back to Pexels+PIL (functional but no AI image). PINTEREST_STATUS notes `gemini-2.0-flash-preview-image-generation` returns 404. Recent commit `22f87b9` flipped to `gemini-2.5-flash-image`; status doc hasn't been reconciled. | Verify current image model works in one live run; update PINTEREST_STATUS.md. |
| **Phase 13 work stashed** (per CLAUDE.md) | Unfinished work sitting in git stash | Decide: `git stash pop` to resume, or drop. |
| **TikTok pipeline dormant** | `tiktok_automation/` present, Supabase secondary project has tables, but `TIKTOK_ACCESS_TOKEN` missing and workflows archived. | Either deprecate (delete `tiktok_automation/`) or refresh token + restore workflow. |
| **YouTube Shorts dormant** | AG_PLAN marks it "deferred". No credentials. Workflow archived. | Confirm deferred; keep archive. |
| **Anti-Gravity site not deployed** | `anti_gravity/` has site + SQLite DB + setup script; 5 seed articles per system-health-report; never deployed to Vercel. | Decide: deploy to Vercel, or deprioritize and mark dormant. |
| **Etsy shop** | Listings JSON exists (`etsy_listings.json`); banking/billing setup still manual per CLAUDE.md. | Manual — out of scope for code. |

### 4. HYGIENE / TECHNICAL DEBT

- **Monorepo bloat** — root contains 10+ top-level status docs (AUDIT_REPORT, AUDIT_MAKE_COM, AUDIT_FINDINGS_SUMMARY, MORNING_REPORT, OVERNIGHT-SESSION-REPORT, PINTEREST_STATUS, REVENUE_FIX_REPORT, SECRETS_AUDIT, PROMPT_PACK_HANDOFF, TASK_COMPLETION_REPORT, PHONE-ACTION-CHECKLIST…). Each was useful at the time; together they make the repo hard to navigate and the "source of truth" ambiguous. Recommend: move to `docs/reports/` and keep only `CLAUDE.md` + `README.md` at root.
- **Duplicate site directories** — `dailydealdarling_website/`, `menopause-planner-site/`, `anti_gravity/site/`, `sites/`, `outputs/*-website/`, plus an `outputs_backup/`. The deploy targets are under `outputs/`; the others are either legacy or variant experiments. Confirm and prune.
- **672 Amazon search URLs remaining** (per CLAUDE.md) — these don't map to single products; long-tail. Consider leaving as-is and investing elsewhere.
- **Late API code paths** — if Zernio/local is the chosen video strategy, remove Late code rather than keeping dead branches.
- **24 archived workflows** — acceptable to keep in `archive/`, but if no plan to resurrect (youtube, tiktok, late rescue-poster, creatomate), delete to reduce cognitive load.

### 5. OUT OF SCOPE THIS SESSION

- **Other GitHub repos under `talhahbilal1-arch`** (3 public total per `/me`). MCP token is scoped to `social-media-empire` only. If you want those audited, grant the MCP server access to each repo or paste the list of repo names.
- **Live runtime data** — I can't query Supabase directly from this session (no env), so "errors in last 24h" and "content_history row counts" are inferred from git commit cadence, not measured. If desired, a one-off `scripts/` runner with `.env` loaded would pull the exact numbers.
- **Browser-based sanity checks** — I did not load fitover35.com, dailydealdarling.com, menopauseplanner.com, or pilottools.ai in a browser. If any rendering regression happened on live sites, it would not show up in this audit.

---

## Recommended next actions (in priority order)

1. **Set `CONVERTKIT_API_KEY` + `CONVERTKIT_API_SECRET`** — unblocks the highest-revenue workflow (email monetization on 333 articles with forms already embedded).
2. **Merge PRs #30, #32, #33** (pilottools/DDD/menopause AdSense compliance) — article-count blockers in the PR bodies are now satisfied. PR #31 gets a visual check before merge.
3. **Decide on video-pipeline strategy** — the repo currently contains three video paths (Remotion in CI, Zernio posting, local Short Video Maker via launchd). Pick one, delete the other two.
4. **Run Supabase migration 004** (`video_state` column) before flipping `VIDEO_STRATEGY=local` in production.
5. **Delete or archive the 47 orphan `claude/*` branches** on GitHub.
6. **Move root-level status docs into `docs/reports/`** to reduce repo clutter.
7. **Make a call on TikTok / YouTube / Anti-Gravity / Etsy** — each is half-built; either finish or explicitly mark dormant in CLAUDE.md.
8. **Refresh Late API keys OR delete the Late code paths** (pick one, don't leave 401 paths live).
9. **Add `RESEND_API_KEY` + `ALERT_EMAIL`** — the emergency-alert dead-man's-switch is currently silent.
10. **After secrets land, re-check PilotTools social (Twitter/LinkedIn) — AG_PLAN claims "complete" but the workflows are shipping dry-run.**
