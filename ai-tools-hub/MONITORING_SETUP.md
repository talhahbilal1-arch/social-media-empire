# PilotTools.ai — Analytics Monitoring Setup (Phase 13.2)

## Overview
This document establishes real-time monitoring of PilotTools.ai performance including SEO metrics, user engagement, and monetization data.

**Platform**: Netlify (deployment) + Netlify Analytics + Google Search Console + Manual tracking

---

## 1. Netlify Analytics Status

### Current Configuration
- **Domain**: pilottools.ai
- **Build**: Static export (Next.js static generation)
- **Deployment**: Netlify (via netlify.toml)

### To Enable Netlify Analytics (if not already active)

1. Log in to Netlify dashboard: https://app.netlify.com
2. Navigate to Site Settings → Analytics
3. Enable "Netlify Analytics" (if available on your plan)
4. This provides:
   - Page views, unique visitors, bounce rate
   - Top pages by traffic
   - Geographic data
   - Traffic sources (referral, direct, organic)

### Alternative: Google Analytics 4 Setup

Since Netlify Analytics may not be available on all plans, set up Google Analytics 4:

**Step 1**: Create GA4 property
```
1. Go to analytics.google.com
2. Create new property "PilotTools Analytics"
3. Create web data stream for pilottools.ai
4. Get measurement ID: G-XXXXXXXXXX
```

**Step 2**: Add GA4 tracking to `pages/_app.js`
```javascript
import { useEffect } from 'react';
import { useRouter } from 'next/router';
import Script from 'next/script';

function MyApp({ Component, pageProps }) {
  const router = useRouter();

  useEffect(() => {
    // Track page views
    if (window.gtag) {
      window.gtag('config', 'G-XXXXXXXXXX', {
        page_path: router.asPath,
      });
    }
  }, [router.asPath]);

  return (
    <>
      <Script
        strategy="afterInteractive"
        src={`https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX`}
      />
      <Script
        strategy="afterInteractive"
        dangerouslySetInnerHTML={{
          __html: `
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', 'G-XXXXXXXXXX', {
              page_path: window.location.pathname,
            });
          `,
        }}
      />
      <Component {...pageProps} />
    </>
  );
}

export default MyApp;
```

---

## 2. Google Search Console Configuration

### Current Status
- **Domain**: pilottools.ai
- **Verification**: Assumed via DNS or HTML file (verify in GSC dashboard)

### Weekly Review Process

**Every Monday (9 AM)**:

1. **Open GSC**: https://search.google.com/search-console
2. **Check Performance Tab**:
   - Total clicks (vs. last week)
   - Total impressions
   - Average CTR
   - Average position

3. **Identify Quick Wins** (position 5-20):
   ```
   Filters: Position 5-20, Last 7 days
   Look for: Keywords with high impressions but low CTR
   Action: Create or improve content for these keywords
   ```

4. **Monitor Indexing**:
   - Check "Coverage" for crawl errors
   - Look for "Excluded" pages (blocklisted by robots.txt?)
   - Monitor "sitemaps" section (ensure sitemap.xml is updated)

5. **Log Findings** in `monitoring/weekly-gsc-report.md`:
   ```markdown
   # Week of [Date]
   
   ## Performance Summary
   - Clicks: [X] (↑/↓ vs. last week)
   - Impressions: [X]
   - CTR: [X]%
   - Avg Position: [X]
   
   ## Top 5 Queries by Clicks
   1. [Query] - [Clicks] clicks, position [X]
   
   ## Quick Wins (Position 5-20)
   - [Query] - [Impressions] impressions, [CTR]% CTR
   
   ## Indexing Status
   - Total indexed: [X] pages
   - Coverage errors: [X]
   - Sitemaps: [X] submitted, [X] indexed
   ```

---

## 3. Ezoic Dashboard Monitoring

### Manual Weekly Entry

Ezoic doesn't expose a public API, so we'll track earnings manually:

**Every Friday (5 PM)**:

1. Log in to Ezoic dashboard: https://dashboard.ezoic.com
2. Go to **Earnings > Today's Earnings**
3. Record in `monitoring/earnings-tracker.json`:
   ```json
   {
     "date": "2026-03-22",
     "ezoic_daily_revenue": 5.43,
     "page_views": 842,
     "rpm": 6.45,
     "notes": "Good Friday - tool comparison pages driving traffic"
   }
   ```

4. **Calculate weekly totals** in `monitoring/weekly-earnings-report.md`

---

## 4. Affiliate Link Click Tracking

### Setup UTM Parameters

Modify affiliate links in `content/tools.json`:

```json
{
  "id": "chatgpt",
  "name": "ChatGPT",
  "affiliate_url": "https://chatgpt.com/?utm_source=pilottools&utm_medium=affiliate&utm_campaign=tool-review",
  ...
}
```

**UTM Structure**:
- **utm_source**: pilottools
- **utm_medium**: affiliate
- **utm_campaign**: [page-type] (tool-review, comparison, alternative, pricing)
- **utm_content**: [tool-name] (optional, for clarity)

### Track in Google Analytics

In GA4 dashboard:
1. Go to **Reports > Traffic > Source/Medium**
2. Filter by `utm_source=pilottools`
3. View conversions by `utm_campaign`

---

## 5. Weekly Monitoring Checklist

### Daily (5-min check)
- [ ] **Page views**: Check Netlify Analytics or GA4 for daily pageview count
- [ ] **Top page today**: Identify if a specific page is getting traffic spikes
- [ ] **Errors**: Check for 404s or site errors in Netlify build logs

### Weekly (30-min check, every Monday)

**Morning**:
- [ ] GSC performance (clicks, impressions, CTR, avg position)
- [ ] Identify 2-3 quick-win keywords (position 5-20 with high impressions)
- [ ] Record findings in `monitoring/weekly-gsc-report.md`

**Afternoon**:
- [ ] Review top 10 pages by traffic (Netlify Analytics or GA4)
- [ ] Check if traffic is from organic search or referral
- [ ] Identify content gaps (comparisons not yet written, profession pages missing)

**Friday**:
- [ ] Log Ezoic earnings in `monitoring/earnings-tracker.json`
- [ ] Calculate weekly summary: total revenue, RPM, page views
- [ ] Record in `monitoring/weekly-earnings-report.md`

### Monthly (1-hour review, 1st of month)

- [ ] Full GSC deep dive: top 50 queries, ranking opportunities
- [ ] Content audit: identify pages with high impressions but low CTR
- [ ] Create 2-3 new blog posts targeting quick-win keywords
- [ ] Update topical clusters: add internal links between related pages
- [ ] Monthly earnings summary: total revenue, YoY growth, RPM trend

---

## 6. Monitoring Infrastructure Files

### Created Files

1. **`monitoring/weekly-gsc-report.md`** — GSC performance tracker
2. **`monitoring/weekly-earnings-report.md`** — Revenue summary
3. **`monitoring/earnings-tracker.json`** — Daily Ezoic earnings log
4. **`monitoring/content-gaps.md`** — Identified SEO opportunities

### Directory Structure
```
ai-tools-hub/
└── monitoring/
    ├── weekly-gsc-report.md
    ├── weekly-earnings-report.md
    ├── earnings-tracker.json
    ├── content-gaps.md
    └── MONITORING_CHECKLIST.md (this file)
```

---

## 7. Optional: Admin Analytics Dashboard

For real-time monitoring without leaving the site, create `/pages/admin/analytics.js`:

**Features**:
- Display daily page views, bounce rate, session duration
- Show top 10 pages by traffic
- Display weekly earnings estimate
- Show top keywords from GSC
- Protected with simple password check

**Note**: Requires GA4 API integration (advanced setup). For MVP, use manual monitoring above.

---

## 8. Tools Required

| Tool | Purpose | Access |
|------|---------|--------|
| **Google Search Console** | SEO monitoring | search.google.com/search-console |
| **Ezoic Dashboard** | Ad revenue tracking | dashboard.ezoic.com |
| **Netlify Dashboard** | Deployment & analytics | app.netlify.com |
| **Google Analytics 4** | User behavior tracking | analytics.google.com |
| **Text Editor** | Log findings | Any editor |

---

## 9. Alert System (Optional)

### Alerts to Watch For

1. **Traffic Spike** (>50% above daily average)
   - Action: Identify which pages are trending, check Google News for related stories
   
2. **Traffic Drop** (>30% below daily average)
   - Action: Check Netlify build logs for errors, verify site is up
   
3. **High Bounce Rate** (>80% on a page)
   - Action: Review page content, improve title/meta description, check loading time
   
4. **Indexing Issue** (new pages not appearing in GSC)
   - Action: Manually request indexing in GSC, check robots.txt for blocklists

### Setup Alerts

Option 1: **Manual checks** (free, built into above checklist)

Option 2: **Google Analytics alerts** (free):
- Go to GA4 → Admin → Property Settings → Anomaly detection
- Enable alerts for unusual traffic patterns

Option 3: **Email alerts** (premium):
- Set up Slack/email notifications via IFTTT or custom script

---

## 10. Success Metrics

### 30-Day Goals
- [ ] 1,000+ monthly page views
- [ ] 5% average CTR in GSC
- [ ] $50+ in weekly Ezoic revenue
- [ ] 10+ new keywords ranking (position 1-20)

### 90-Day Goals
- [ ] 5,000+ monthly page views
- [ ] 8% average CTR in GSC
- [ ] $250+ in weekly Ezoic revenue
- [ ] 50+ keywords ranking (position 1-20)

### 6-Month Goals
- [ ] 25,000+ monthly page views
- [ ] 10% average CTR in GSC
- [ ] $1,000+ in weekly Ezoic revenue
- [ ] 200+ keywords ranking (position 1-20)

---

## 11. Quick Start (Do This First)

1. **Verify GSC**: Go to https://search.google.com/search-console and confirm pilottools.ai is verified
2. **Enable Analytics**: Go to https://analytics.google.com and create a property for pilottools.ai
3. **Create monitoring directory**: `mkdir -p monitoring/`
4. **Start weekly tracking**: Use the checklist above every Monday
5. **Log findings**: Record GSC and Ezoic data in `.md` and `.json` files in `monitoring/`

---

**Last Updated**: March 22, 2026
**Status**: Ready to implement
**Owner**: Analytics & SEO team
