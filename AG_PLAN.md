# STRICT RULES — READ BEFORE EXECUTING

**ONLY execute the steps listed below. NOTHING ELSE.**
- Do NOT investigate, fix, or touch any other project, domain, or infrastructure
- Do NOT access Vercel API tokens, auth credentials, or make API calls unless explicitly listed in a step
- Do NOT modify files outside the paths listed in the steps
- Do NOT clear or rewrite this file
- If you find an unrelated issue, STOP and tell the user — do NOT fix it yourself

---

# Task: PilotTools Homepage — Option A + B Upgrade (Hero, Trust & Social Proof)

**Scope: ONLY files in `ai-tools-hub/`. Do NOT touch anything else.**

## Context
PilotTools (pilottools.ai) is our AI tools directory. We're upgrading the homepage with bigger search, pricing badges, social proof, and trust signals based on competitor research.

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
  - Acceptance: Search bar is visibly wider, placeholder is dynamic

- [ ] **Step 2: Add "Submit Your Tool" button to hero** — `ai-tools-hub/pages/index.js` line 62-72
  - Add a 4th button after the "Compare Tools" link:
    ```jsx
    <Link href="/submit/" className="btn-secondary font-bold border-accent/30 text-accent">
      Submit Your Tool
    </Link>
    ```
  - Acceptance: 4 buttons in hero, "Submit Your Tool" has a subtle accent border

- [ ] **Step 3: Add "Submit Tool" to nav** — `ai-tools-hub/components/Navigation.js` line 5-13
  - Add to NAV_LINKS array before the last entry:
    ```js
    { href: '/submit/', label: 'Submit Tool' },
    ```
  - Acceptance: "Submit Tool" appears in top nav between Blog and Tool Finder

- [ ] **Step 4: Create submit page placeholder** — `ai-tools-hub/pages/submit/index.js` (NEW FILE)
  - Simple page with Layout wrapper, heading "Submit Your AI Tool", paragraph explaining we review tools for free listing. Include a mailto link to `talhahbilal1@gmail.com` with subject "Tool Submission - [Tool Name]".
  - Use existing Layout, btn-primary, card classes.
  - Acceptance: `/submit/` route works and renders cleanly

- [ ] **Step 5: Pricing tier badges on ToolCard** — `ai-tools-hub/components/ToolCard.js` line 52-54
  - Replace the current free_tier badge logic with:
    ```jsx
    {tool.pricing.starting_price === 0 || tool.pricing.starting_price === '0' ? (
      <span className="badge-green text-xs">Free</span>
    ) : tool.pricing.free_tier ? (
      <span className="badge-blue text-xs">Freemium</span>
    ) : (
      <span className="badge-purple text-xs">Paid</span>
    )}
    ```
  - Acceptance: Every tool card shows Free / Freemium / Paid badge

### Part B: Trust & Social Proof

- [ ] **Step 6: Upgrade social proof bar** — `ai-tools-hub/pages/index.js` lines 79-97
  - Replace the stats array with:
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
  - Remove the green checkmark SVG, use emoji icons instead
  - Acceptance: 5 stats with emoji icons, no hardcoded month

- [ ] **Step 7: Add "Verified" badge to ToolCard** — `ai-tools-hub/components/ToolCard.js` line 49
  - Replace `<p className="text-sm text-dt-muted">{tool.company}</p>` with:
    ```jsx
    <p className="text-sm text-dt-muted flex items-center gap-1">
      {tool.company}
      <svg className="w-3.5 h-3.5 text-accent" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
      </svg>
    </p>
    ```
  - Acceptance: Cyan verified checkmark next to company name on every card

- [ ] **Step 8: Green "Verified" label** — `ai-tools-hub/components/ToolCard.js` line 62
  - Replace `<span className="text-sm text-dt-muted">Expert reviewed</span>` with:
    ```jsx
    <span className="text-sm text-green-400 flex items-center gap-1">
      <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/></svg>
      Verified
    </span>
    ```
  - Acceptance: Green "Verified" with checkmark next to star rating

---

## Files You May Touch (EXHAUSTIVE LIST)
- `ai-tools-hub/pages/index.js` — edit
- `ai-tools-hub/components/ToolCard.js` — edit
- `ai-tools-hub/components/Navigation.js` — edit
- `ai-tools-hub/pages/submit/index.js` — create new

## Do NOT
- Touch ANY file not listed above
- Modify tailwind.config.js, globals.css, or content/tools.json
- Access Vercel API, auth tokens, or make any infrastructure changes
- Touch fitover35.com, dailydealdarling.com, or any brand site
- Add npm dependencies
- Remove ad slots or newsletter signup
- Clear or rewrite this AG_PLAN.md file

## Verification
After all steps: `cd ai-tools-hub && npm run build` — should complete with 0 errors.
