# Quiz Pages - VELVET NOIR Theme Update

## Plan
Update the 3 quiz pages to match the VELVET NOIR dark theme.

### Tasks
- [x] Read all 3 quiz files and the main CSS to understand current state
- [x] Update skincare-routine.html inline styles to dark theme
- [x] Update gift-finder.html inline styles to dark theme
- [x] Update home-organization.html inline styles to dark theme
- [x] Add review section

## Review

Updated all 3 quiz pages to match the VELVET NOIR dark luxury theme. All quiz JavaScript, affiliate links, content, and functionality remain untouched -- only visual styling was changed.

### Changes Applied to All 3 Files

**Quiz options:**
- Border: `#e0e0e0` / `var(--amber, #B45309)` -> `#2A2A30`
- Background: `white` -> `#1A1A20`
- Hover: border `#FF3366`, background `rgba(255,51,102,0.08)`
- Selected: border `#FF3366`, background `rgba(255,51,102,0.15)`
- h4 color: `#F0F0F4`
- p color: `#A0A0A8`

**Buttons:**
- CTA/Next: `#FF3366` background, hover `#E6194D`
- Back: dark background `#1A1A20`, border `#2A2A30`, light text
- Disabled: `#2A2A30` background, `#6A6A72` text (was `#ccc`)

**Typography:**
- Headings: `var(--font-display)` (Playfair Display), color `#F0F0F4`
- Body/buttons: `var(--font-body)` (Sora)
- Subtext: `#A0A0A8`

**Progress bar (skincare quiz):**
- Inactive: `#2A2A30` (was `#f0f0f0`)
- Active: `#FF3366`
- Completed: `#00CC88`

**Result cards (skincare quiz):**
- Background: `#1A1A20` with `1px solid #2A2A30` border (was white with light shadow)
- Product name: `#F0F0F4`
- Price: `#FF3366`
- Description: `#A0A0A8`
- Image placeholder background: `#16161A`
- Shadow: `rgba(0,0,0,0.3)` (deeper for dark theme)

**Results header (skincare quiz):**
- Gradient: `#FF3366` to `#E6194D`

**Gift finder + Home organization:**
- Inline `color: #666` on header paragraphs -> `#A0A0A8`
- h1 inline style: added `color: #F0F0F4`
- Results section h2/p: light colors via CSS rules
- Back link: `#FF3366` via `#quiz-results a:not(.btn)` rule
