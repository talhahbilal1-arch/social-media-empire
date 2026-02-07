# Affiliate Program Signup Prompt for Claude Code

Copy and paste this entire prompt into a new Claude Code session to continue affiliate signups.

---

## PROMPT START

I'm building an AI tools directory site called ToolPilot (https://toolpilot-hub.netlify.app). I need you to help me sign up for affiliate programs using browser automation. The site reviews AI tools and earns revenue through affiliate links.

### My Info (use for all signups)
- **First Name**: Talhah
- **Last Name**: Bilal
- **Email**: talhahbilal1@gmail.com
- **Website**: https://toolpilot-hub.netlify.app
- **Country**: United States
- **Password pattern**: ToolPilot2026!Aff (use this or a variation if needed)

### Promotion Description (use for "how will you promote" fields)
"I run ToolPilot (https://toolpilot-hub.netlify.app), an AI tools directory with in-depth reviews, feature comparisons, and pricing breakdowns. Each tool has a dedicated review page with pros/cons and links to the tool. I also drive traffic through Pinterest (53+ pins) and SEO-optimized content targeting buyer-intent keywords like 'best AI writing tool 2026'."

### Signup Status

Check `ai-tools-hub/AFFILIATE-STATUS.json` for current status of each program. Update it after each signup.

### Programs to Sign Up For

#### 1. Jasper AI (PRIORITY - HIGH)
- **Affiliate page**: https://www.jasper.ai/partners or https://www.jasper.ai/affiliates
- **Commission**: 30% recurring
- **Notes**: May redirect to a partner portal like PartnerStack or Impact

#### 2. Copy.ai (PRIORITY - HIGH)
- **Affiliate page**: https://www.copy.ai/affiliates
- **Commission**: 30% recurring for first year
- **Notes**: Uses PartnerStack for affiliate management

#### 3. Scalenut (PRIORITY - MEDIUM)
- **Affiliate page**: https://www.scalenut.com/affiliate-program
- **Commission**: 20-30% recurring
- **Notes**: May use own portal or FirstPromoter

#### 4. ElevenLabs (PRIORITY - HIGH)
- **Affiliate page**: https://elevenlabs.io/affiliates or check their website footer
- **Commission**: ~20% recurring
- **Notes**: Fast-growing AI audio company, good conversion rates

#### 5. Canva (PRIORITY - MEDIUM)
- **Affiliate page**: https://www.canva.com/affiliates/ or via Impact.com
- **Commission**: Up to $36 per new Canva Pro subscription
- **Notes**: One-time bounty, not recurring. High volume though.

#### 6. Grammarly (PRIORITY - MEDIUM)
- **Affiliate page**: https://www.grammarly.com/affiliates or via Impact/ShareASale
- **Commission**: $25 per free signup, $0.20/activation
- **Notes**: Well-known program, high conversion rate

#### 7. Synthesia (PRIORITY - LOW)
- **Affiliate page**: https://www.synthesia.io/affiliates
- **Commission**: 20-25% recurring
- **Notes**: AI video generation tool

#### 8. Descript (PRIORITY - LOW)
- **Affiliate page**: https://www.descript.com/affiliates
- **Commission**: 15-20% recurring
- **Notes**: Audio/video editing AI tool

### After Each Signup

1. Note the referral/affiliate link you receive
2. Update `ai-tools-hub/AFFILIATE-STATUS.json` with:
   - status: "signed_up" or "pending_approval" or "approved"
   - affiliate_url: the actual referral link
   - signup_date: today's date
   - notes: any relevant details
3. Once you have real affiliate URLs, update `ai-tools-hub/content/tools.json` - replace the placeholder `?ref=toolpilot` URLs with the real affiliate tracking links

### After All Signups

1. Run `cd ai-tools-hub && npm run build` to rebuild the site
2. Commit and push changes to the `revenue-site` branch
3. The GitHub Action will auto-deploy to Netlify

### Browser Automation Notes
- Use Chrome MCP tools (mcp__claude-in-chrome__*)
- Always call tabs_context_mcp first to get current tabs
- Create new tabs for each signup (tabs_create_mcp)
- Some programs use third-party affiliate platforms (PartnerStack, Impact, ShareASale) - you may need to create accounts there too
- If a signup page 404s, try searching "[tool name] affiliate program" to find the current URL
- Take screenshots before and after form submission for verification

## PROMPT END
