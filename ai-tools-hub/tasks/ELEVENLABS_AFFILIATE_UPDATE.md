# Task B: Update ElevenLabs Affiliate Links (Phase 14)

## Objective
Replace every ElevenLabs link with new affiliate URL and ensure proper markup.

**NEW AFFILIATE URL**: https://try.elevenlabs.io/a17kfvge5u00
**REQUIRED ATTRIBUTES**: rel="nofollow sponsored" target="_blank"

## Files to Update

### 1. content/tools.json - PRIORITY
- [ ] Update affiliate_url field (line 1592): https://elevenlabs.io?ref=pilottools → https://try.elevenlabs.io/a17kfvge5u00
- [ ] Keep website field as-is for reference

### 2. content/articles.json - CRITICAL
- [ ] Find "best-ai-voice-audio-tools-2026-elevenlabs-vs-murf-vs-descript" article
- [ ] Update all CTA buttons with correct href, rel="nofollow sponsored" target="_blank"
  - "Try ElevenLabs Free →" button (around line 223)
  - "Try Murf Free →" button (around line 363)  
  - "Try Descript Free →" button (around line 500)
  - "Compare All AI Voice Tools" button (around line 665)
- [ ] Verify all links use new affiliate URL

### 3. content/comparisons.json - Reference
- [ ] Check for actual links (mostly slug references, may not need updating)

### 4. content/categories.json - Reference
- [ ] Check for actual links (mostly descriptive text)

### 5. content/pinterest-pins.json - Reference
- [ ] Links point to pilottools.ai internal pages, not affiliate URLs

## Status
- Started: [TBD]
- Current Step: Analyzing codebase
- Blocked by: None

## Notes
- ElevenLabs affiliate links are mainly in tools.json (affiliate_url) and articles.json (CTA buttons)
- The key change is: affiliate_url in tools.json may be used in dynamic links on tool detail pages
- All external affiliate links need rel="nofollow sponsored" and target="_blank" for proper SEO and UX
