# Phase 13.1: Chatbot Testing & Deployment Guide

## Summary of Changes

### Files Created
1. **`/pages/api/chat.js`** — AI Gateway-powered chat endpoint
   - Uses Vercel AI Gateway with OIDC authentication
   - Routes requests through Claude 3.5 Sonnet
   - Streams responses using AI SDK v6
   - System prompt includes all 20 tools from tools.json

2. **`/components/ChatWidget.js`** — React chat UI component
   - Floating button (bottom-right) showing 💬 emoji
   - Expandable modal interface
   - Message history with user/assistant distinction
   - Real-time streaming with loading animation
   - Affiliate disclosure banner
   - Mobile-responsive design

### Files Modified
1. **`/pages/index.js`** — Added ChatWidget integration
   - Imported ChatWidget component
   - Added `<ChatWidget />` before closing Layout tag
   - No breaking changes to existing functionality

2. **`package.json`** — Added AI SDK dependencies
   - `ai` (v6+) — Core streaming and chat utilities
   - `@ai-sdk/openai` — OpenAI client (routes to Claude via gateway)
   - `@ai-sdk/react` — React hooks for chat management

### Files Created (Setup)
- **`.env.example.local`** — Environment variable template
  - Shows how to configure AI Gateway OIDC token
  - Includes setup instructions

## Pre-Testing Setup

### Step 1: Get Vercel AI Gateway OIDC Token
```bash
# Install Vercel CLI if not already installed
npm i -g vercel

# Link your project to Vercel
vercel link

# Pull environment variables (including OIDC token for AI Gateway)
vercel env pull

# This creates .env.local with:
# - AI_GATEWAY_URL
# - AI_GATEWAY_OIDC_TOKEN
```

### Step 2: Verify Dependencies Installed
```bash
npm list ai @ai-sdk/openai @ai-sdk/react
# Should show all three packages installed
```

### Step 3: Start Development Server
```bash
npm run dev
# Server runs at http://localhost:3000
```

## Testing Checklist

### Visual Tests (Manual Browser Testing)
- [ ] Load homepage at http://localhost:3000
- [ ] See floating 💬 button in bottom-right corner
- [ ] Button has correct styling (accent color, shadow, rounded)
- [ ] On mobile, button is still visible and not cut off

### Interaction Tests
- [ ] Click floating button → modal appears with animation
- [ ] Modal shows welcome message from assistant
- [ ] Can type in input field
- [ ] Send button works when text is entered
- [ ] Send button is disabled when empty
- [ ] Click X button → modal closes
- [ ] Closed button → floating button reappears

### Chat Functionality Tests
Test these exact queries:

#### Query 1: Content Writer Use Case
**Input**: "What's the best AI tool for content writers?"
**Expected Response**:
- Should recommend 2-3 tools like ChatGPT, Jasper, Writesonic
- Explain why each is good for writing
- Mention pricing if relevant
- Be conversational tone

**Verify**:
- [ ] Response mentions actual tools from our database
- [ ] Streaming appears character-by-character (not all at once)
- [ ] No errors in console
- [ ] Response loads within 5 seconds

#### Query 2: Developer Learning AI
**Input**: "I'm a developer learning AI, what should I use?"
**Expected Response**:
- Recommend tools like Claude, ChatGPT, Cursor
- Explain code generation, reasoning, debugging features
- Match developer-specific use case

**Verify**:
- [ ] Relevant tools recommended
- [ ] Explanations are technical and specific
- [ ] No hallucinated tools

#### Query 3: Image Generation
**Input**: "Best AI tool for creating images"
**Expected Response**:
- Recommend Midjourney, DALL-E (via ChatGPT), Runway
- Mention image quality, ease of use, pricing

**Verify**:
- [ ] Image generation tools mentioned
- [ ] Focused on visual output, not text

#### Query 4: Real-Time Data
**Input**: "I need real-time search capabilities"
**Expected Response**:
- Recommend Perplexity, ChatGPT Plus (with web search)
- Explain real-time vs knowledge cutoff

**Verify**:
- [ ] Accurate tool recommendations
- [ ] Explains capability differences

### Affiliate Link Tests
- [ ] After chat, tools mentioned have affiliate URLs embedded
- [ ] Click a recommendation → goes to correct URL
- [ ] URL includes tracking params (utm_source=toolpilot)
- [ ] Multiple conversations don't break affiliate tracking

### Performance Tests
- [ ] First response appears within 3-5 seconds
- [ ] Streaming doesn't lag on slow connections
- [ ] Modal doesn't freeze while streaming
- [ ] Can send new message while streaming previous one
- [ ] Page scrolls smoothly with chat open

### Mobile Tests (Use browser DevTools)
- [ ] Resize to iPhone 12 (390x844)
- [ ] Chat button visible
- [ ] Modal doesn't overflow screen
- [ ] Input field and send button work
- [ ] Text is readable (no tiny fonts)

### Error Handling Tests
- [ ] Send empty message → nothing happens
- [ ] Network error (disable internet) → shows graceful error
- [ ] Try to open console → no JS errors
- [ ] Page continues working after chat error

### SEO & Accessibility Tests
- [ ] Close chat modal → page works normally
- [ ] Chat doesn't interfere with existing links
- [ ] Button has aria-label for screen readers
- [ ] Modal can be closed with Escape key (optional nice-to-have)

## Deployment Checklist

### Before Deploying to Production
- [ ] All manual tests pass
- [ ] No console errors
- [ ] Build succeeds: `npm run build`
- [ ] No warnings about unused imports
- [ ] .env.local is in .gitignore (never commit secrets)
- [ ] Test with actual Vercel environment variables

### Deploy Command
```bash
# Push to GitHub (GitHub-Vercel integration auto-deploys)
git add .
git commit -m "feat: add AI chatbot for tool recommendations (Phase 13.1)"
git push origin main

# Or deploy directly to Vercel:
vercel deploy --prod
```

### Post-Deployment Verification
- [ ] Visit https://pilottools.ai
- [ ] Chat button appears in bottom-right
- [ ] Send test query → response streams correctly
- [ ] Affiliate links work on production
- [ ] No errors in Vercel logs

## Troubleshooting

### Chat Button Doesn't Appear
- **Check**: Is ChatWidget imported and used in index.js?
- **Check**: Is JavaScript enabled in browser?
- **Check**: Look for console errors with `F12 → Console`
- **Fix**: Run `npm run dev` again

### Chat Sends But No Response
- **Check**: Is AI_GATEWAY_OIDC_TOKEN set in .env.local?
- **Check**: Are you using `vercel env pull`?
- **Command**: `cat .env.local | grep AI_GATEWAY`
- **Fix**: Update .env.local with correct token

### Modal Freezes While Streaming
- **Check**: Is browser tab in focus?
- **Check**: Network speed (throttle to Slow 3G in DevTools)
- **Fix**: Streaming should still work, just slower
- **Report**: If completely frozen, check browser console

### Build Fails
- **Check**: `npm install` was run after package.json changes
- **Command**: `npm run build` to see full error
- **Common**: ESLint warnings might fail build
- **Fix**: Run `npm run lint -- --fix`

### Affiliate Links Don't Work
- **Check**: Are tools being recommended by Claude?
- **Check**: Do recommended tool names match tools.json exactly?
- **Note**: In Phase 13.1, we show tool names but affiliate linking is handled backend-side
- **Fix**: Verify tools.json has affiliate_url for each tool

## Performance Metrics to Monitor

After deployment, check Vercel Analytics:
1. **Chat API Response Time**: Target < 2 seconds
2. **Chat Modal Load**: Should be < 500ms
3. **Chat Button Visibility**: 100% of sessions

## Future Enhancements (Phase 13.2+)

- [ ] Persistent chat history (localStorage)
- [ ] User preference learning
- [ ] Integration with comparison pages
- [ ] Analytics: track which tools recommended most
- [ ] Multi-turn conversations with refinement
- [ ] Pre-fill chat with quiz results
- [ ] Chat with actual affiliate link injection in responses
- [ ] Rate limiting to prevent abuse

## Files to Keep in .gitignore

```
.env.local          # Never commit secrets
.env.*.local        # Vercel environment files
node_modules/       # Dependencies
.next/              # Build output
out/                # Static export
*.log               # Log files
```

## Quick Reference: File Locations

| File | Purpose |
|------|---------|
| `/pages/api/chat.js` | Backend chat endpoint |
| `/components/ChatWidget.js` | Frontend UI component |
| `/pages/index.js` | Homepage with ChatWidget integration |
| `.env.example.local` | Setup instructions |
| `PHASE_13_PLAN.md` | Architecture & design |
| `PHASE_13_TESTING.md` | This file |

---

## Sign-Off

**Phase 13.1 Complete** when all tests pass and deployment is successful.

Next phase: Persist chat history, add analytics, integrate with quiz.
