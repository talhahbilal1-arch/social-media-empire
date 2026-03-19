# STRICT RULES — READ BEFORE EXECUTING

**ONLY execute the steps listed below. NOTHING ELSE.**
- Do NOT investigate, fix, or touch any other project, domain, or infrastructure
- Do NOT access Vercel API tokens, auth credentials, or make API calls
- Do NOT modify files outside the paths listed in the steps
- Do NOT clear or rewrite this file
- If you find an unrelated issue, STOP and tell the user

---

# Task: PilotTools Mobile Responsiveness Fixes

**Scope: ONLY files in `ai-tools-hub/`. Do NOT touch anything else.**

## Context
The recent Option A+B hero upgrade introduced 3 mobile layout issues on screens < 640px (iPhone SE = 375px, iPhone 14 = 390px). All fixes are Tailwind class adjustments — no new CSS or dependencies.

---

## Steps

- [ ] **Step 1: Fix hero buttons stacking** — `ai-tools-hub/pages/index.js` line 62
  - Current: `<div className="flex flex-wrap justify-center gap-4 animate-fade-in-up stagger-4">`
  - Problem: 4 buttons with `px-6` don't fit 2-per-row on 375px, creating a 2+1+1 pattern
  - Fix: Change to `<div className="grid grid-cols-2 sm:flex sm:flex-wrap justify-center gap-3 sm:gap-4 animate-fade-in-up stagger-4">`
  - Also make each button full-width on mobile by adding `w-full sm:w-auto text-center` to each Link's className (all 4 buttons, lines 63-74)
  - This creates a clean 2x2 grid on mobile, flowing row on tablet+
  - Acceptance: On 375px, buttons form a clean 2-column grid. On 640px+, they flow inline.

- [ ] **Step 2: Fix social proof bar on mobile** — `ai-tools-hub/pages/index.js` line 84
  - Current: `<div className="flex flex-wrap justify-center items-center gap-6 md:gap-12 text-sm text-dt-muted">`
  - Problem: 5 items wrap messily on mobile
  - Fix: Change to `<div className="grid grid-cols-2 sm:grid-cols-3 md:flex md:flex-wrap justify-center items-center gap-4 md:gap-12 text-sm text-dt-muted">`
  - Also add `text-center sm:text-left` to each stat item div (the `<div key={item.label}` on line 92)
  - This creates a clean 2-column grid on mobile (2+2+1 centered), 3-col on tablet, inline on desktop
  - Acceptance: Stats are in a tidy grid on mobile, not randomly wrapping

- [ ] **Step 3: Tighten hero heading on mobile** — `ai-tools-hub/pages/index.js` line 47
  - Current: `className="text-4xl md:text-6xl font-extrabold text-dt mb-6 leading-tight animate-fade-in-up"`
  - Fix: Change `text-4xl` to `text-3xl` — making it `text-3xl md:text-6xl`
  - Also on line 50, change `text-xl md:text-2xl` to `text-lg md:text-2xl` for the subtitle
  - Acceptance: Hero text is proportional on small screens without being overwhelming

- [ ] **Step 4: Tighten hero padding on mobile** — `ai-tools-hub/pages/index.js` line 43
  - Current: `className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center relative z-10"`
  - Fix: Change `py-20` to `py-12 sm:py-20`
  - This reduces hero vertical padding from 80px to 48px on mobile — less wasted space
  - Acceptance: Hero fits better on mobile viewport without excessive whitespace

- [ ] **Step 5: Ensure ToolCard verified text doesn't overflow** — `ai-tools-hub/components/ToolCard.js` line 71
  - Current: The rating row has `<span className="text-sm text-green-400 flex items-center gap-1">`
  - Fix: Add `whitespace-nowrap` to prevent the "Verified" text from wrapping:
    `<span className="text-sm text-green-400 flex items-center gap-1 whitespace-nowrap">`
  - Acceptance: "Verified" stays on one line even on narrow cards

---

## Files You May Touch (EXHAUSTIVE LIST)
- `ai-tools-hub/pages/index.js` — edit only
- `ai-tools-hub/components/ToolCard.js` — edit only

## Do NOT
- Touch ANY file not listed above
- Add new CSS, modify tailwind.config.js or globals.css
- Touch fitover35, dailydealdarling, or any brand site
- Add npm dependencies
- Access Vercel API or auth tokens
- Clear or rewrite this AG_PLAN.md file

## Verification
After all steps: `cd ai-tools-hub && npm run build` — should complete with 0 errors.
Then visually verify by resizing browser to 375px width.
