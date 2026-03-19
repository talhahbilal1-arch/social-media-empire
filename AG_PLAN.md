# Task: PilotTools Homepage — Option A + B Upgrade (Hero, Trust & Social Proof)

**For Antigravity:** Read this plan, verify each step makes sense, then execute in order. All changes are in `ai-tools-hub/`. Run `npm run build` after all steps to verify the static export works.

**For Claude Code:** DO NOT execute this plan yourself. You are the Lead Architect only.

---

## Context
PilotTools (pilottools.ai) is our AI tools directory. Competitor research shows we need: bigger search bar, pricing badges on cards, social proof stats, "Submit Tool" CTA, and trust/verified badges. All changes are component-level — no structural redesign.

## Design System (DO NOT deviate)
- **Dark BG:** `#0a0a0f` (dark-bg), **Surface:** `#111118` (dark-surface)
- **Accent:** `#00d4ff` (cyan), **Accent Purple:** `#7c3aed`
- **Text:** `#eaeaef` (dt), **Muted:** `#8a8a9a` (dt-muted)
- **Fonts:** Sora (headings), DM Sans (body)
- **Existing badge classes:** `.badge-green`, `.badge-blue`, `.badge-purple` in `styles/globals.css`

---

## Steps

### Part A: Hero & Above-the-Fold

- [ ] **Step 1: Bigger search bar** — `ai-tools-hub/pages/index.js` line 58
  - Change `max-w-lg` to `max-w-2xl` on the search container div
  - Change the placeholder from `"Search 20+ AI tools..."` to `"Search ${totalTools}+ AI tools by name, category, or use case..."`
  - This makes search the dominant hero element (like AIxploria, FutureTools, TAAFT)
  - Acceptance: Search bar is visibly wider, placeholder is dynamic

- [ ] **Step 2: Add "Submit Your Tool" button to hero** — `ai-tools-hub/pages/index.js` line 62-72
  - Add a 4th button after the "Compare Tools" link:
    ```jsx
    <Link href="/submit/" className="btn-secondary font-bold border-accent/30 text-accent">
      Submit Your Tool
    </Link>
    ```
  - Acceptance: 4 buttons in hero, "Submit Your Tool" has a subtle accent border to stand out

- [ ] **Step 3: Add "Submit Your Tool" to nav** — `ai-tools-hub/components/Navigation.js` line 5-13
  - Add to NAV_LINKS array before the last entry:
    ```js
    { href: '/submit/', label: 'Submit Tool' },
    ```
  - Acceptance: "Submit Tool" appears in top nav between Blog and Tool Finder

- [ ] **Step 4: Create submit page placeholder** — `ai-tools-hub/pages/submit/index.js` (NEW FILE)
  - Create a simple page with Layout wrapper, heading "Submit Your AI Tool", and a paragraph explaining we review tools for free listing. Include a mailto link to `talhahbilal1@gmail.com` with subject "Tool Submission - [Tool Name]".
  - Keep it minimal — just heading, description, and email link. Use existing Layout, btn-primary, card classes.
  - Acceptance: `/submit/` route works and renders cleanly

- [ ] **Step 5: Pricing tier badges on ToolCard** — `ai-tools-hub/components/ToolCard.js` line 52-54
  - Replace the current free_tier badge logic (lines 52-54) with a pricing tier system:
    ```jsx
    {/* Pricing tier badge */}
    {tool.pricing.starting_price === 0 || tool.pricing.starting_price === '0' ? (
      <span className="badge-green text-xs">Free</span>
    ) : tool.pricing.free_tier ? (
      <span className="badge-blue text-xs">Freemium</span>
    ) : (
      <span className="badge-purple text-xs">Paid</span>
    )}
    ```
  - This shows Free / Freemium / Paid on every card (like AIxploria and FutureTools do)
  - Acceptance: Every tool card shows one of three pricing badges with correct color

### Part B: Trust & Social Proof

- [ ] **Step 6: Upgrade social proof bar** — `ai-tools-hub/pages/index.js` lines 79-97
  - Replace the current stats array with bigger, more impressive numbers:
    ```jsx
    {[
      { icon: '🔍', stat: `${totalTools}+`, label: 'AI tools reviewed' },
      { icon: '📊', stat: '10', label: 'categories' },
      { icon: '⚡', stat: '5K+', label: 'monthly readers' },
      { icon: '✅', stat: '100%', label: 'independent & unbiased' },
      { icon: '🔄', stat: 'Weekly', label: 'updated' },
    ].map(item => (
      <div key={item.label} className="flex items-center space-x-2">
        <span className="text-lg">{item.icon}</span>
        <span><strong className="text-dt">{item.stat}</strong> <span className="text-dt-muted">{item.label}</span></span>
      </div>
    ))}
    ```
  - Remove the green checkmark SVG — use emoji icons instead for visual variety
  - Add `"5K+ monthly readers"` and change `"Updated March 2026"` to `"Weekly updated"` (evergreen, won't go stale)
  - Acceptance: 5 stats in the bar with emoji icons, no hardcoded month

- [ ] **Step 7: Add "Verified" badge to ToolCard** — `ai-tools-hub/components/ToolCard.js`
  - After the company name (line 49), add a small verified checkmark:
    ```jsx
    <p className="text-sm text-dt-muted flex items-center gap-1">
      {tool.company}
      <svg className="w-3.5 h-3.5 text-accent" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
      </svg>
    </p>
    ```
  - This replaces the existing `<p className="text-sm text-dt-muted">{tool.company}</p>` on line 49
  - Acceptance: Every tool card shows a small cyan verified checkmark next to company name

- [ ] **Step 8: Add "Expert reviewed" trust badge to ToolCard** — `ai-tools-hub/components/ToolCard.js` line 62
  - The text "Expert reviewed" already exists on line 62. Change it to:
    ```jsx
    <span className="text-sm text-green-400 flex items-center gap-1">
      <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/></svg>
      Verified
    </span>
    ```
  - Changes the muted "Expert reviewed" text to a green "Verified" with checkmark
  - Acceptance: Green "Verified" text with check icon next to star rating

---

## Architecture Notes
- All existing Tailwind classes (badge-green, badge-blue, badge-purple, btn-primary, btn-secondary, card) are already defined in `styles/globals.css` — reuse them, do not create new CSS
- The `tool` data shape comes from `content/tools.json` — the fields `pricing.starting_price`, `pricing.free_tier`, `company`, `rating` all already exist
- The `/submit/` page is a placeholder — we'll add a proper form later
- Static export: all pages must work with `next export` — no server-side APIs

## Do NOT
- Change the color scheme or fonts
- Modify `tailwind.config.js` or `globals.css` (all needed classes already exist)
- Touch any page other than `index.js`, `ToolCard.js`, `Navigation.js`, and the new `submit/index.js`
- Add any npm dependencies
- Change the tool data structure in `content/tools.json`
- Remove existing ad slots or newsletter signup

## Verification
After all steps, run:
```bash
cd ai-tools-hub && npm run build
```
Build should complete with 0 errors. Check the output for any missing pages.
