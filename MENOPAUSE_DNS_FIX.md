# menopauseplanner.com — DNS Fix Guide

## Root Cause

`menopauseplanner.com` is **NOT registered**. The domain does not exist in any DNS system.

- `dig menopauseplanner.com` → `NXDOMAIN` (no record in `.com` TLD)
- `curl https://menopauseplanner.com` → "Could not resolve host"
- WHOIS returns only the generic VeriSign `.com` TLD record — no domain-specific registrant

The current live site is `menopause-planner-website.vercel.app` (works fine).

## Fix — Two Steps Required

### Step 1: Buy the Domain

Purchase `menopauseplanner.com` at Namecheap (or any registrar):
- Go to namecheap.com → search `menopauseplanner.com`
- Register it (~$10-12/year)

### Step 2: Set DNS Records at Namecheap

After purchasing, go to **Namecheap Dashboard → Domains → menopauseplanner.com → Advanced DNS**.

Add these records:

| Type  | Host | Value              | TTL        |
|-------|------|--------------------|------------|
| A     | @    | `76.76.21.21`      | Automatic  |
| CNAME | www  | `cname.vercel-dns.com` | Automatic |

> **Note**: Delete any default Namecheap parking records (URL Redirect, default A records) before adding the above.

### Step 3: Add Domain to Vercel

1. Go to Vercel Dashboard → Project `menopause-planner-website` (project ID: `prj_Z8gwdM8yH3SdAR7VAlY1KapLaFco`)
2. Settings → Domains → Add domain: `menopauseplanner.com`
3. Also add: `www.menopauseplanner.com`
4. Vercel will verify DNS — takes 5-30 minutes after DNS propagates

### Step 4: Verify

```bash
# After 15-30 min propagation:
dig menopauseplanner.com           # should return 76.76.21.21
dig www.menopauseplanner.com       # should return CNAME to cname.vercel-dns.com
curl -I https://menopauseplanner.com  # should return 200
```

## Current State Summary

| Domain | Status |
|--------|--------|
| fitover35.com | ✅ Live on Vercel |
| dailydealdarling.com | ✅ Live on Vercel |
| menopause-planner-website.vercel.app | ✅ Live (fallback URL) |
| menopauseplanner.com | ❌ **Unregistered — domain does not exist** |

## Cost

~$10-12/year at Namecheap. Worth it for brand credibility and SEO (custom domain vs `.vercel.app`).
